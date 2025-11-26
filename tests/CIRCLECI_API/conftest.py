# conftest.py

import os
import re
import json
import pytest
import yaml
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Mapping, Union
from urllib.parse import urljoin, urlencode
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _expand_env_in_string(value: str) -> str:
    """
    Expand ${VAR:-default} patterns in the given string.
    Supports multiple occurrences in one string.
    """

    # Regex to capture ${VAR} or ${VAR:-default} style
    pattern = re.compile(r"\$\{([^}]+)\}")

    def replacer(match: re.Match) -> str:
        inner = match.group(1)
        # Format: VAR or VAR:-default
        if ":-" in inner:
            var_name, default = inner.split(":-", 1)
            var_name = var_name.strip()
            default = default
            return os.environ.get(var_name, default)
        else:
            var_name = inner.strip()
            return os.environ.get(var_name, "")

    # Replace until no more patterns to avoid nested or chained expansions
    prev = None
    current = value
    while prev != current:
        prev = current
        current = pattern.sub(replacer, current)

    return current


def _expand_env_in_obj(obj: Any) -> Any:
    """
    Walk the object (dict/list/str) and expand environment variable patterns.
    """
    if isinstance(obj, dict):
        return {k: _expand_env_in_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_in_obj(v) for v in obj]
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    return obj


def _load_yaml_config(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found at: {file_path}")
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing YAML config at {file_path}: {e}") from e


class APIClient:
    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Mapping[str, str]] = None,
        default_params: Optional[Mapping[str, str]] = None,
        timeout: Optional[Union[int, float]] = None,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Optional[list] = None,
        pool_maxsize: int = 10,
    ) -> None:
        self.base_url = (base_url or "").strip()
        self.default_headers = dict(default_headers or {})
        self.default_params = dict(default_params or {})
        self.timeout = timeout if timeout is not None else float(os.environ.get("API_TIMEOUT_SECONDS", 30))
        self.session = requests.Session()

        # Configure retries and HTTP adapters
        status_forcelist = status_forcelist or [429, 500, 502, 503, 504]
        allowed_methods = frozenset(["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"])
        retry = Retry(
            total=int(os.environ.get("API_MAX_RETRIES", retries)),
            backoff_factor=float(os.environ.get("API_BACKOFF_FACTOR", backoff_factor)),
            status_forcelist=status_forcelist,
            allowed_methods=allowed_methods,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_maxsize=int(os.environ.get("API_POOL_MAXSIZE", pool_maxsize)))
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        ep = (endpoint or "").strip()
        if ep.lower().startswith(("http://", "https://")):
            return ep
        # Ensure base_url ends with a slash for proper urljoin behavior
        base = self.base_url
        if not base.endswith("/"):
            base = base + "/"
        return urljoin(base, ep.lstrip("/"))

    def _merge(self, base: Optional[Mapping[str, Any]], override: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        result = dict(base or {})
        if override:
            result.update(override)
        return result

    def make_request(
        self,
        endpoint: str,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        method: str = "GET",
        json: Any = None,
        data: Any = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        req_headers = self._merge(self.default_headers, headers)
        req_params = self._merge(self.default_params, params)
        eff_timeout = timeout if timeout is not None else self.timeout

        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=req_headers or None,
            params=req_params or None,
            json=json,
            data=data,
            timeout=eff_timeout,
        )
        return response

    # Convenience methods (lowercase)
    def get(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET", timeout=timeout)

    def post(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json=json, data=data, timeout=timeout)

    def put(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json=json, data=data, timeout=timeout)

    def patch(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json=json, data=data, timeout=timeout)

    def delete(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", json=json, data=data, timeout=timeout)

    def head(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="HEAD", timeout=timeout)

    def options(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="OPTIONS", timeout=timeout)

    # Uppercase aliases for convenience
    def GET(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.get(endpoint, headers=headers, params=params, timeout=timeout)

    def POST(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.post(endpoint, headers=headers, params=params, json=json, data=data, timeout=timeout)

    def PUT(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.put(endpoint, headers=headers, params=params, json=json, data=data, timeout=timeout)

    def PATCH(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.patch(endpoint, headers=headers, params=params, json=json, data=data, timeout=timeout)

    def DELETE(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.delete(endpoint, headers=headers, params=params, json=json, data=data, timeout=timeout)


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    # Locate config.yml in the same directory as this conftest.py, using os.path.join as requested
    base_dir = Path(__file__).resolve().parent
    config_path = Path(os.path.join(str(base_dir), "config.yml"))

    raw = _load_yaml_config(config_path)
    expanded = _expand_env_in_obj(raw)

    # Ensure base URL formatting robustness if present
    api_cfg = expanded.get("api", {})
    if isinstance(api_cfg, dict):
        host = api_cfg.get("host")
        if isinstance(host, str):
            api_cfg["host"] = host.strip()
        expanded["api"] = api_cfg

    return expanded


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    api = config.get("api", {})
    host = api.get("host", "")
    return str(host).strip()


@pytest.fixture(scope="session")
def auth(config: Dict[str, Any]) -> Dict[str, Any]:
    return dict(config.get("auth", {}))


@pytest.fixture(scope="session")
def auth_api_key_header(auth: Dict[str, Any]) -> str:
    return str(auth.get("api_key_header", "") or "")


@pytest.fixture(scope="session")
def auth_api_key_query(auth: Dict[str, Any]) -> str:
    return str(auth.get("api_key_query", "") or "")


@pytest.fixture(scope="session")
def default_headers(auth_api_key_header: str) -> Dict[str, str]:
    """
    Create default headers. If an API header token is provided, use 'Circle-Token' header.
    """
    headers: Dict[str, str] = {}
    if auth_api_key_header:
        headers["Circle-Token"] = auth_api_key_header
    return headers


@pytest.fixture(scope="session")
def default_query_params(auth_api_key_query: str) -> Dict[str, str]:
    """
    Create default query params. If a query token is provided, use 'circle-token' query param.
    """
    params: Dict[str, str] = {}
    if auth_api_key_query:
        params["circle-token"] = auth_api_key_query
    return params


@pytest.fixture(scope="session")
def api_client(
    api_host: str,
    default_headers: Dict[str, str],
    default_query_params: Dict[str, str],
) -> APIClient:
    # Instantiate API client with retry and timeout defaults sourced from env if set.
    client = APIClient(
        base_url=api_host,
        default_headers=default_headers,
        default_params=default_query_params,
        # Timeout and retry values can be overridden via environment variables as implemented in APIClient
    )
    return client


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    return dict(config.get("test_data", {}))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: For all success scenarios")
