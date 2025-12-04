import json
import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ---------------------------
# Utility: Environment expansion
# ---------------------------

# Regex similar to r"${([^}:s]+):-([^}]+)}" to support ${ENV_VAR:-default}
_ENV_PATTERN = re.compile(r"\$\{([^}:\s]+):-([^}]+)\}")


def _expand_env_vars(value: Any) -> Any:
    """
    Recursively expand environment variable placeholders in strings using the
    pattern ${ENV_VAR:-default}. If ENV_VAR is unset or empty, 'default' is used.
    Non-string inputs are returned unchanged, dicts/lists are processed recursively.
    """

    def _expand_str(s: str) -> str:
        def _repl(match: re.Match) -> str:
            var_name = match.group(1)
            default_val = match.group(2)
            env_val = os.environ.get(var_name)
            return env_val if env_val not in (None, "") else default_val

        # Expand repeatedly in case a replacement introduces another pattern
        previous = None
        current = s
        # Avoid infinite loops by capping iterations
        for _ in range(10):
            if previous == current:
                break
            previous = current
            current = _ENV_PATTERN.sub(_repl, current)
        return current

    if isinstance(value, str):
        return _expand_str(value)
    elif isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    else:
        return value


# ---------------------------
# Config loading
# ---------------------------

def _load_raw_config() -> Dict[str, Any]:
    here = Path(__file__).parent
    cfg_path = here / "config.yml"
    if not cfg_path.exists():
        raise pytest.UsageError(f"Missing configuration file: {cfg_path}")

    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise pytest.UsageError(f"Invalid YAML in {cfg_path}: {e}") from e
    except Exception as e:
        raise pytest.UsageError(f"Failed to read {cfg_path}: {e}") from e

    return data


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load config.yml from the same directory as this conftest.py,
    expanding environment variables using ${ENV_VAR:-default}.
    """
    raw = _load_raw_config()
    expanded = _expand_env_vars(raw)
    if not isinstance(expanded, dict):
        raise pytest.UsageError("Top-level config must be a mapping/dictionary.")
    return expanded


# ---------------------------
# Dynamic config getter
# ---------------------------

@pytest.fixture(scope="session")
def get_config(config: Dict[str, Any]) -> Callable[[str, Optional[Any]], Any]:
    """
    Returns a callable to fetch config values via dotted keys, e.g.:
    get_config("api.host") or get_config("test_data.project-slug").
    """

    def _getter(dotted_key: str, default: Any = None) -> Any:
        parts = dotted_key.split(".")
        current: Any = config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                if default is not None:
                    return default
                raise KeyError(f"Config key not found: {dotted_key}")
        return current

    return _getter


# ---------------------------
# Endpoint test data loading and merge
# ---------------------------

@pytest.fixture
def load_endpoint_test_data(request) -> Callable[[str], Dict[str, Any]]:
    """
    Returns a callable that loads JSON test data from a path.
    Resolution order:
      - absolute path
      - relative to the test file's directory
      - relative to current working directory
    """

    def _loader(path: str) -> Dict[str, Any]:
        candidate = Path(path)
        if not candidate.is_absolute():
            test_dir = Path(getattr(request, "fspath", Path.cwd())).parent
            if (test_dir / path).exists():
                candidate = test_dir / path
            elif (Path.cwd() / path).exists():
                candidate = Path.cwd() / path

        if not candidate.exists():
            raise FileNotFoundError(f"Endpoint test data file not found: {path}")

        try:
            with candidate.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {candidate}: {e}") from e
        if not isinstance(data, dict):
            raise ValueError(f"Endpoint test data must be a JSON object: {candidate}")
        return data

    return _loader


@pytest.fixture
def merged_test_data(config: Dict[str, Any], load_endpoint_test_data: Callable[[str], Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
    """
    Returns a callable that merges config['test_data'] with endpoint JSON data.
    Values from endpoint JSON override keys in config.yml.test_data when duplicated.
    """

    def _merger(path: str) -> Dict[str, Any]:
        base = config.get("test_data", {})
        if base is None:
            base = {}
        if not isinstance(base, dict):
            raise ValueError("config['test_data'] must be a mapping if present.")
        ep = load_endpoint_test_data(path)
        merged = dict(base)
        merged.update(ep)
        return merged

    return _merger


# ---------------------------
# API Client
# ---------------------------

class APIClient:
    def __init__(
        self,
        base_url: str,
        default_timeout: Optional[float] = None,
        retries_config: Optional[Dict[str, Any]] = None,
        verify: Optional[bool] = None,
        session: Optional[requests.Session] = None,
    ):
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("Base URL must be a non-empty string.")
        self.base_url = base_url.strip().rstrip("/")
        self.default_timeout = default_timeout
        self.verify = verify

        self.session = session or requests.Session()

        # Configure retries if provided or use sensible defaults
        rc = retries_config or {}
        total = int(rc.get("total", 3))
        backoff_factor = float(rc.get("backoff_factor", 0.3))
        status_forcelist = rc.get("status_forcelist", (429, 500, 502, 503, 504))
        allowed_methods = rc.get("allowed_methods", frozenset(["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]))

        retry = Retry(
            total=total,
            read=total,
            connect=total,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=allowed_methods,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _full_url(self, endpoint: Optional[str]) -> str:
        if not endpoint:
            return self.base_url
        return f"{self.base_url}/{str(endpoint).lstrip('/')}"

    def make_request(self, endpoint: Optional[str], method: str = "GET", headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        url = self._full_url(endpoint)
        hdrs = {}
        if headers:
            hdrs.update(headers)

        # Default timeout if not provided
        if "timeout" not in kwargs and self.default_timeout is not None:
            kwargs["timeout"] = self.default_timeout

        # Allow per-request override of verify; fallback to client default
        if "verify" not in kwargs and self.verify is not None:
            kwargs["verify"] = self.verify

        response = self.session.request(method=method.upper(), url=url, headers=hdrs, **kwargs)
        return response

    def get(self, endpoint: Optional[str], headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="GET", headers=headers, **kwargs)

    def post(self, endpoint: Optional[str], headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="POST", headers=headers, **kwargs)

    def put(self, endpoint: Optional[str], headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="PUT", headers=headers, **kwargs)

    def patch(self, endpoint: Optional[str], headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="PATCH", headers=headers, **kwargs)

    def delete(self, endpoint: Optional[str], headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="DELETE", headers=headers, **kwargs)


@pytest.fixture(scope="session")
def api_client(config: Dict[str, Any]) -> APIClient:
    # Base URL required
    try:
        base_url = config["api"]["host"]
    except Exception as e:
        raise pytest.UsageError("config['api']['host'] is required in config.yml") from e

    # Optional settings
    api_cfg = config.get("api", {}) if isinstance(config.get("api", {}), dict) else {}
    timeout = api_cfg.get("timeout", None)
    if timeout is not None:
        try:
            timeout = float(timeout)
        except Exception:
            raise pytest.UsageError("config['api']['timeout'] must be numeric if provided.")

    verify = api_cfg.get("verify", None)
    if isinstance(verify, str):
        # Interpret common string booleans
        v = verify.strip().lower()
        if v in ("true", "1", "yes", "y", "on"):
            verify = True
        elif v in ("false", "0", "no", "n", "off"):
            verify = False

    retries_cfg = api_cfg.get("retry") or api_cfg.get("retries")  # support common naming if present
    if retries_cfg is not None and not isinstance(retries_cfg, dict):
        raise pytest.UsageError("config['api']['retry'|'retries'] must be a mapping if provided.")

    return APIClient(
        base_url=str(base_url).strip(),
        default_timeout=timeout,
        retries_config=retries_cfg,
        verify=verify if isinstance(verify, bool) else None,
    )


# ---------------------------
# Pytest hooks / markers
# ---------------------------

def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: mark test as part of the smoke suite")
