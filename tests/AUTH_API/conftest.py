# conftest.py
import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def pytest_configure(config):
    # Register test markers
    config.addinivalue_line("markers", "smoke: For all success scenarios")


def _expand_env_in_string(value: str) -> str:
    """
    Expand ${VAR} or ${VAR:-default} patterns from environment variables.
    If VAR is unset/empty and default is provided, use default; otherwise empty string.
    """
    pattern = re.compile(r"\$\{([^:{}]+)(?::-(.*?))?\}")

    def repl(match: re.Match) -> str:
        var = match.group(1)
        default = match.group(2)
        env_val = os.environ.get(var, "")
        if env_val != "":
            return env_val
        return default if default is not None else ""

    return pattern.sub(repl, value)


def _expand_env_in_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    if isinstance(obj, Mapping):
        return {k: _expand_env_in_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_in_obj(v) for v in obj]
    return obj


def _load_yaml_config() -> Dict[str, Any]:
    """
    Load and validate YAML config from config.yml placed in the same directory as this conftest.py.
    """
    base_dir = Path(__file__).parent.resolve()
    # Intentionally use os.path.join along with pathlib as requested
    cfg_path = Path(os.path.join(str(base_dir), "config.yml"))

    if not cfg_path.exists():
        pytest.fail(f"config.yml not found at path: {cfg_path}")

    try:
        raw = cfg_path.read_text(encoding="utf-8")
    except Exception as e:
        pytest.fail(f"Unable to read config file {cfg_path}: {e}")

    try:
        data = yaml.safe_load(raw) or {}
    except Exception as e:
        pytest.fail(f"Error parsing YAML config {cfg_path}: {e}")

    data = _expand_env_in_obj(data)

    if not isinstance(data, dict):
        pytest.fail("Root of config.yml must be a mapping")

    # Only use expected keys without assuming any custom keys
    api = data.get("api", {})
    if not isinstance(api, dict):
        pytest.fail("'api' must be a mapping in config.yml")

    # Normalize host if present
    host = api.get("host")
    if host is not None:
        if not isinstance(host, str):
            pytest.fail("'api.host' must be a string")
        api["host"] = host.strip()

    data["api"] = api

    test_data = data.get("test_data", {})
    if not isinstance(test_data, dict):
        pytest.fail("'test_data' must be a mapping in config.yml")
    data["test_data"] = test_data

    return data


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Loaded configuration from config.yml with environment variable expansion.
    Expected structure:
      api:
        host: "${API_HOST:-https://example.com}"
      test_data: {}
    """
    return _load_yaml_config()


@pytest.fixture(scope="session")
def host(config: Dict[str, Any]) -> str:
    """
    Provides the API host from config['api']['host'].
    """
    api_cfg = config.get("api", {})
    host_value = api_cfg.get("host")
    if not host_value or not isinstance(host_value, str):
        pytest.fail("Missing or invalid 'api.host' in config.yml")
    return host_value.strip()


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provides test_data from config.
    """
    return config.get("test_data", {})


class APIClient:
    """
    Simple API client that uses requests.Session with retry and timeout support.
    Base URL is derived from the loaded config.
    """

    def __init__(
        self,
        base_url: str,
        default_timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: Optional[tuple] = (429, 500, 502, 503, 504),
    ):
        self.base_url = self._normalize_base_url(base_url)
        self.default_timeout = default_timeout

        self.session = requests.Session()
        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=frozenset({"HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @staticmethod
    def _normalize_base_url(url: str) -> str:
        url = (url or "").strip()
        return url.rstrip("/")

    def _build_url(self, endpoint: str) -> str:
        endpoint = (endpoint or "").strip()
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"{self.base_url}{endpoint}"

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        timeout: Optional[float] = None,
        json: Any = None,
        data: Any = None,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        method = (method or "GET").upper()

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json=json,
            data=data,
            timeout=self.default_timeout if timeout is None else timeout,
        )
        return response

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET", timeout=timeout)

    def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json=json, data=data, timeout=timeout)

    def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json=json, data=data, timeout=timeout)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", json=json, data=data, timeout=timeout)

    def patch(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json=json, data=data, timeout=timeout)


@pytest.fixture(scope="session")
def api_client(host: str) -> APIClient:
    """
    Provides an APIClient initialized with the host from config.
    """
    return APIClient(base_url=host)
