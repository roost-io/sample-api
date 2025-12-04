# conftest.py
import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# -------------------------
# Pytest marker registration
# -------------------------
def pytest_configure(config) -> None:
    # Register smoke marker for success scenarios
    config.addinivalue_line("markers", "smoke: mark test as smoke (success scenarios)")


# -------------------------
# Environment expansion utils
# -------------------------
# Pattern with default: ${ENV_VAR:-defaultValue}
_DEFAULT_PATTERN = re.compile(r"\$\{([^}: \t\r\n]+):-([^}]+)\}")
# Simple pattern: ${ENV_VAR}
_SIMPLE_PATTERN = re.compile(r"\$\{([^}:\s]+)\}")


def _expand_env_in_string(value: str) -> str:
    # First handle defaulted placeholders
    def _repl_default(match: re.Match) -> str:
        var_name = match.group(1)
        default = match.group(2)
        return os.environ.get(var_name, default)

    value = _DEFAULT_PATTERN.sub(_repl_default, value)

    # Then handle simple placeholders without default
    def _repl_simple(match: re.Match) -> str:
        var_name = match.group(1)
        return os.environ.get(var_name, "")

    value = _SIMPLE_PATTERN.sub(_repl_simple, value)
    return value


def _expand_env(obj: Any) -> Any:
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    if isinstance(obj, Mapping):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_expand_env(v) for v in obj)
    return obj


# -------------------------
# Config loading helpers
# -------------------------
_ALLOWED_TOP_LEVEL_KEYS = {"api", "test_data"}


def _sanitize_base_url(url: str) -> str:
    s = (url or "").strip()
    if not s or s.lower() == "undefined":
        raise pytest.UsageError(
            "Invalid or undefined API host in config.yml (api.host). "
            "Ensure it resolves from environment and is not 'undefined'."
        )
    # Remove trailing slash for consistency
    return s.rstrip("/")


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise pytest.UsageError(f"Config file not found at: {config_path}")

    try:
        raw_text = config_path.read_text(encoding="utf-8")
    except Exception as e:
        raise pytest.UsageError(f"Failed to read config file {config_path}: {e}") from e

    try:
        data = yaml.safe_load(raw_text) or {}
    except yaml.YAMLError as e:
        raise pytest.UsageError(f"YAML parsing error in {config_path}: {e}") from e

    if not isinstance(data, dict):
        raise pytest.UsageError(f"Top-level YAML content must be a mapping in {config_path}")

    # Strictly enforce allowed keys only
    unexpected = set(data.keys()) - _ALLOWED_TOP_LEVEL_KEYS
    if unexpected:
        raise pytest.UsageError(
            f"Unexpected keys in config.yml: {sorted(unexpected)}. "
            f"Allowed keys: {sorted(_ALLOWED_TOP_LEVEL_KEYS)}"
        )

    # Expand environment placeholders
    data = _expand_env(data)

    # Validate structure
    api_section = data.get("api")
    if not isinstance(api_section, dict):
        raise pytest.UsageError("Missing or invalid 'api' section in config.yml")

    host = api_section.get("host")
    if not isinstance(host, str):
        raise pytest.UsageError("Missing or invalid 'api.host' (must be a string) in config.yml")

    # Sanitize and set back
    data["api"]["host"] = _sanitize_base_url(host)

    # Ensure test_data exists (as provided), default to {} if missing but do not introduce new keys beyond allowed
    if "test_data" not in data:
        data["test_data"] = {}

    if not isinstance(data["test_data"], dict):
        raise pytest.UsageError("'test_data' must be a mapping/object in config.yml")

    return data


# -------------------------
# API Client
# -------------------------
class APIClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: Sequence[int] = (429, 500, 502, 503, 504),
    ) -> None:
        self.base_url = _sanitize_base_url(base_url)
        self.timeout = float(timeout)

        self.session = requests.Session()

        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            status=retries,
            backoff_factor=backoff_factor,
            status_forcelist=frozenset(status_forcelist),
            allowed_methods=frozenset({"HEAD", "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"}),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: Optional[str]) -> str:
        if not endpoint:
            return self.base_url
        ep = endpoint.strip()
        if ep.startswith("http://") or ep.startswith("https://"):
            return ep
        return f"{self.base_url}/{ep.lstrip('/')}"

    def make_request(self, endpoint: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        url = self._build_url(endpoint)
        method = (method or "GET").upper()
        # default timeout if not provided
        kwargs.setdefault("timeout", self.timeout)
        if headers:
            kwargs.setdefault("headers", headers)
        return self.session.request(method=method, url=url, **kwargs)

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="GET", **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="POST", **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="PUT", **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="DELETE", **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="PATCH", **kwargs)


# -------------------------
# Fixtures
# -------------------------
@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    # Find config.yml in the same directory as this conftest.py using os.path.join + pathlib
    current_dir = Path(__file__).resolve().parent
    config_path = Path(os.path.join(str(current_dir), "config.yml"))
    return _load_yaml_config(config_path)


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    return config["api"]["host"]


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    return config["test_data"]


@pytest.fixture(scope="session")
def api_client(api_host: str) -> APIClient:
    # Use sane defaults for timeout and retries (config does not define extra keys)
    return APIClient(
        base_url=api_host,
        timeout=10.0,
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
    )
