# conftest.py

import os
import json
import re
from pathlib import Path
from typing import Any, Dict, Callable, Optional, Union

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Regex "like" r"${([^}:s]+):-([^}]+)}" but corrected to support whitespace class
_ENV_VAR_PATTERN = re.compile(r"\$\{([^}:\s]+):-([^}]+)\}")


def _expand_env_vars(obj: Any) -> Any:
    """
    Recursively expand environment variables in the form ${VAR:-default}.
    If VAR is unset or empty, uses 'default'.
    """

    def _substitute(s: str) -> str:
        def repl(match: re.Match) -> str:
            var_name = match.group(1)
            default = match.group(2)
            val = os.environ.get(var_name)
            if val is None or val == "":
                return default
            return val

        # Apply substitutions repeatedly until no more matches
        prev = None
        cur = s
        while prev != cur:
            prev = cur
            cur = _ENV_VAR_PATTERN.sub(repl, cur)
        return cur

    if isinstance(obj, str):
        return _substitute(obj)
    elif isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(i) for i in obj]
    else:
        return obj


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise pytest.UsageError(f"config.yml not found at: {config_path}")
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise pytest.UsageError(f"Invalid YAML in config.yml: {e}") from e
    if not isinstance(data, dict):
        raise pytest.UsageError("config.yml must contain a mapping at the top level.")
    return data


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load config.yml from the same directory as this conftest.py
    and expand env vars in the format ${VAR:-default}.
    """
    base_dir = Path(__file__).parent
    cfg_path = base_dir / "config.yml"
    raw_cfg = _load_yaml_config(cfg_path)
    expanded_cfg = _expand_env_vars(raw_cfg)
    return expanded_cfg


@pytest.fixture(scope="session")
def get_config(config: Dict[str, Any]) -> Callable[[str, Optional[Any]], Any]:
    """
    Return a function to fetch config values via dotted keys.
    Example: get_config("api.host") or get_config("test_data.project-slug")
    """

    def _getter(key: str, default: Optional[Any] = None) -> Any:
        parts = key.split(".") if key else []
        cur: Any = config
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return default
        return cur

    return _getter


@pytest.fixture
def load_endpoint_test_data() -> Callable[[Union[str, Path]], Dict[str, Any]]:
    """
    Load endpoint-specific test data JSON dynamically.
    Usage in tests:
        endpoint_data = load_endpoint_test_data("tests/data/endpoint.json")
    """

    def _loader(path: Union[str, Path]) -> Dict[str, Any]:
        p = Path(path)
        tried = []
        if not p.is_absolute():
            # Try current working directory
            candidate = Path.cwd() / p
            tried.append(str(candidate))
            if candidate.exists():
                p = candidate
            else:
                # Try relative to this conftest.py directory
                conf_rel = Path(__file__).parent / p
                tried.append(str(conf_rel))
                if conf_rel.exists():
                    p = conf_rel

        if not p.exists():
            tried_str = ", ".join(tried) if tried else str(p)
            raise pytest.UsageError(f"Endpoint test data JSON not found. Tried: {tried_str}")

        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise pytest.UsageError(f"Invalid JSON in {p}: {e}") from e

        if not isinstance(data, dict):
            raise pytest.UsageError(f"Endpoint test data must be a JSON object at top level: {p}")
        return data

    return _loader


@pytest.fixture
def merged_test_data(
    config: Dict[str, Any], load_endpoint_test_data: Callable[[Union[str, Path]], Dict[str, Any]]
) -> Callable[[Optional[Union[str, Path, Dict[str, Any]]]], Dict[str, Any]]:
    """
    Factory that merges test_data from config.yml with endpoint-specific data.
    Endpoint data overrides config.yml test_data on conflicts (shallow merge).
    Usage:
        data = merged_test_data("tests/data/endpoint.json")
        data = merged_test_data(Path("tests/data/endpoint.json"))
        data = merged_test_data({"key": "override"})  # if you already have a dict
        data = merged_test_data(None)  # only config test_data
    """
    base_td = {}
    if isinstance(config, dict):
        base_td = config.get("test_data", {}) or {}
        if not isinstance(base_td, dict):
            raise pytest.UsageError("config.yml 'test_data' must be a mapping if present.")

    def _merge(endpoint: Optional[Union[str, Path, Dict[str, Any]]] = None) -> Dict[str, Any]:
        if endpoint is None:
            endpoint_td = {}
        elif isinstance(endpoint, dict):
            endpoint_td = endpoint
        else:
            endpoint_td = load_endpoint_test_data(endpoint)

        if not isinstance(endpoint_td, dict):
            raise pytest.UsageError("Endpoint test data must be a dict/mapping.")

        merged = dict(base_td)
        merged.update(endpoint_td)  # endpoint overrides
        return merged

    return _merge


class APIClient:
    def __init__(self, base_url: str, timeout: Optional[float] = None, retry_cfg: Optional[Dict[str, Any]] = None):
        self.base_url = (base_url or "").strip().rstrip("/")
        if not self.base_url:
            raise pytest.UsageError("Invalid API base URL from config (api.host).")

        self.timeout = timeout if timeout is not None else 30.0

        self.session = requests.Session()

        # Configure retry strategy
        retry_cfg = retry_cfg or {}
        total = int(retry_cfg.get("total", 3))
        backoff = float(retry_cfg.get("backoff_factor", 0.5))
        status_forcelist = retry_cfg.get("status_forcelist", [429, 500, 502, 503, 504])
        methods = retry_cfg.get(
            "allowed_methods",
            frozenset({"HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"})
        )
        retry = Retry(
            total=total,
            read=total,
            connect=total,
            backoff_factor=backoff,
            status_forcelist=status_forcelist,
            allowed_methods=methods,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Default headers (none unless caller sets via methods)
        self.default_headers: Dict[str, str] = {}

    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.strip()
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return f"{self.base_url}{endpoint}"

    def make_request(self, endpoint: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        url = self._build_url(endpoint)
        req_headers = dict(self.default_headers)
        if headers:
            req_headers.update(headers)
        timeout = kwargs.pop("timeout", self.timeout)
        resp = self.session.request(method=method.upper(), url=url, headers=req_headers, timeout=timeout, **kwargs)
        return resp

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="GET", headers=headers, **kwargs)

    def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="POST", headers=headers, **kwargs)

    def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="PUT", headers=headers, **kwargs)

    def patch(self, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="PATCH", headers=headers, **kwargs)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="DELETE", headers=headers, **kwargs)


@pytest.fixture(scope="session")
def api_client(config: Dict[str, Any]) -> APIClient:
    """
    Provide an API client configured via config.yml
    """
    api_cfg = config.get("api", {}) if isinstance(config, dict) else {}
    host = api_cfg.get("host")
    if not host:
        raise pytest.UsageError("config.yml missing required key: api.host")

    timeout = api_cfg.get("timeout")
    try:
        timeout_value: Optional[float]
        if timeout is None or timeout == "":
            timeout_value = None
        else:
            timeout_value = float(timeout)
    except (TypeError, ValueError):
        raise pytest.UsageError("api.timeout must be a number (seconds).")

    retry_cfg = api_cfg.get("retry", {}) if isinstance(api_cfg.get("retry", {}), dict) else {}

    client = APIClient(base_url=str(host), timeout=timeout_value, retry_cfg=retry_cfg)

    # Optional: if config provides default headers in a generic way, apply them.
    # We avoid renaming keys; only apply if a mapping exists at config['api'].get('default_headers')
    default_headers = api_cfg.get("default_headers")
    if isinstance(default_headers, dict):
        client.default_headers.update({str(k): str(v) for k, v in default_headers.items()})

    # Common auth conveniences without renaming: If known keys exist, use them.
    auth_cfg = config.get("auth", {}) if isinstance(config.get("auth", {}), dict) else {}
    jwt_token = auth_cfg.get("jwt_token")
    if isinstance(jwt_token, str) and jwt_token.strip():
        client.default_headers.setdefault("Authorization", f"Bearer {jwt_token.strip()}")

    # If api_key header name/value provided, apply them (support a couple of common key names)
    api_key_header_name = auth_cfg.get("api_key_header")
    api_key_value = auth_cfg.get("api_key_value", auth_cfg.get("api_key"))
    if isinstance(api_key_header_name, str) and isinstance(api_key_value, str) and api_key_header_name and api_key_value:
        client.default_headers.setdefault(api_key_header_name, api_key_value)

    # If cookie_auth provided, set Cookie header directly
    cookie_auth = auth_cfg.get("cookie_auth")
    if isinstance(cookie_auth, str) and cookie_auth:
        client.default_headers.setdefault("Cookie", cookie_auth)

    return client


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: mark test as a smoke test")
