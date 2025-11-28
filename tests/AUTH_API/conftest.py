# conftest.py
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: For all success scenarios")


def _expand_env_in_string(value: str) -> str:
    """
    Expand ${VAR} and ${VAR:-default} with environment variables.
    - If default is provided with ':-', use it when env var is unset or empty.
    """
    if not isinstance(value, str):
        return value

    pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*?))?\}")

    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        default = match.group(2)
        env_val = os.getenv(var_name)
        if default is not None:
            # Use default if env is unset or empty
            return env_val if env_val not in (None, "") else default
        # No default -> use env value or empty string if unset
        return env_val if env_val is not None else ""

    return pattern.sub(replacer, value)


def _expand_env(obj: Any) -> Any:
    """
    Recursively expand environment references in dict/list/str structures.
    """
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(i) for i in obj]
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    return obj


def _load_yaml_file(path: Path) -> Dict[str, Any]:
    if not path.exists() or not path.is_file():
        pytest.fail(f"Configuration file not found at: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        pytest.fail(f"Failed to parse YAML file {path}: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error reading YAML file {path}: {e}")
    return data


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    # Find config.yml in the same directory as this conftest.py using os.path.join and pathlib
    base_dir = Path(__file__).resolve().parent
    config_path = Path(os.path.join(str(base_dir), "config.yml"))

    raw_cfg = _load_yaml_file(config_path)
    expanded_cfg = _expand_env(raw_cfg)

    # Basic validation per provided structure (do not assume custom keys)
    api_section = expanded_cfg.get("api", {})
    if not isinstance(api_section, dict):
        pytest.fail("Invalid configuration: 'api' section must be a mapping")

    host_val = str(api_section.get("host", "")).strip()
    if not host_val:
        pytest.fail("Invalid configuration: 'api.host' must be provided in config.yml (after env expansion)")

    # Normalize minimal whitespace trimming (robust base URL handling)
    expanded_cfg["api"]["host"] = host_val

    # Ensure test_data exists even if empty in file
    if "test_data" not in expanded_cfg or expanded_cfg["test_data"] is None:
        expanded_cfg["test_data"] = {}

    return expanded_cfg


@pytest.fixture(scope="session")
def host(config: Dict[str, Any]) -> str:
    # Only use provided key; no assumptions
    value = str(config["api"]["host"]).strip()
    return value.rstrip("/")  # avoid double slashes when joining endpoints


class ApiClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: Optional[list] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.base_url = (base_url or "").strip().rstrip("/")
        if not self.base_url:
            raise ValueError("ApiClient requires a non-empty base_url")

        self.timeout = timeout
        self.session = requests.Session()

        if status_forcelist is None:
            status_forcelist = [429, 500, 502, 503, 504]

        # Retry configuration with compatibility for urllib3 versions
        try:
            retry = Retry(
                total=retries,
                connect=retries,
                read=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
                allowed_methods=frozenset({"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}),
                raise_on_status=False,
            )
        except TypeError:
            retry = Retry(
                total=retries,
                connect=retries,
                read=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
                method_whitelist=frozenset({"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}),
                raise_on_status=False,
            )

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Default headers; can be overridden per request
        default_headers = {"Accept": "application/json"}
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)

    def _build_url(self, endpoint: str) -> str:
        endpoint = (endpoint or "").strip()
        if endpoint.lower().startswith(("http://", "https://")):
            return endpoint
        if not endpoint:
            return self.base_url
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        json: Any = None,
        data: Any = None,
        **kwargs: Any,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        req_headers = dict(self.session.headers)
        if headers:
            req_headers.update(headers)
        timeout = kwargs.pop("timeout", self.timeout)
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=req_headers,
            json=json,
            data=data,
            timeout=timeout,
            **kwargs,
        )
        return response

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET", **kwargs)

    def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json=json, data=data, **kwargs)

    def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json=json, data=data, **kwargs)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", **kwargs)

    def patch(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json=json, data=data, **kwargs)

    # Uppercase aliases, if desired
    def GET(self, *args: Any, **kwargs: Any) -> requests.Response:
        return self.get(*args, **kwargs)

    def POST(self, *args: Any, **kwargs: Any) -> requests.Response:
        return self.post(*args, **kwargs)

    def PUT(self, *args: Any, **kwargs: Any) -> requests.Response:
        return self.put(*args, **kwargs)

    def DELETE(self, *args: Any, **kwargs: Any) -> requests.Response:
        return self.delete(*args, **kwargs)

    def PATCH(self, *args: Any, **kwargs: Any) -> requests.Response:
        return self.patch(*args, **kwargs)


@pytest.fixture(scope="session")
def api_client(config: Dict[str, Any], host: str) -> ApiClient:
    # Use config-driven host; no assumptions about other keys
    client = ApiClient(base_url=host)
    return client


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    return config.get("test_data", {})
