# conftest.py
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _expand_env_in_string(value: str) -> str:
    """
    Expand patterns like ${ENV_VAR:-default} in the given string using os.environ.
    If ENV_VAR is not present in the environment, use the provided default (which can be empty).
    """
    if not isinstance(value, str):
        return value

    pattern = re.compile(r"\$\{(?P<name>[^:}]+)(?::-(?P<default>[^}]*))?\}")

    def repl(match: re.Match) -> str:
        name = match.group("name")
        default = match.group("default") if match.group("default") is not None else ""
        return os.environ.get(name, default)

    return pattern.sub(repl, value)


def _expand_env_in_data(data: Any) -> Any:
    """
    Recursively expand environment variables in all strings within the given data structure.
    """
    if isinstance(data, dict):
        return {k: _expand_env_in_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_expand_env_in_data(item) for item in data]
    elif isinstance(data, str):
        return _expand_env_in_string(data)
    else:
        return data


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        pytest.fail(f"config.yml not found at: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        pytest.fail(f"Failed to parse YAML at {config_path}: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error loading {config_path}: {e}")

    if not isinstance(raw, dict):
        pytest.fail(f"Configuration at {config_path} must be a YAML mapping (dict)")

    expanded = _expand_env_in_data(raw)

    # Normalize base URL if present
    api_section = expanded.get("api", {})
    if isinstance(api_section, dict) and "host" in api_section and api_section["host"] is not None:
        host = str(api_section["host"]).strip()
        api_section["host"] = host
        expanded["api"] = api_section

    return expanded


class APIClient:
    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Mapping[str, str]] = None,
        default_params: Optional[Mapping[str, str]] = None,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Optional[Mapping[int, str]] = None,
    ):
        self.base_url = (base_url or "").strip().rstrip("/")
        self.default_headers = dict(default_headers or {})
        self.default_params = dict(default_params or {})
        self.timeout = timeout

        status_forcelist = status_forcelist or {429: "Too Many Requests", 500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout"}

        self.session = requests.Session()

        # Build a Retry strategy compatible across urllib3 versions
        methods = frozenset({"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"})
        try:
            retry = Retry(
                total=retries,
                connect=retries,
                read=retries,
                status=retries,
                backoff_factor=backoff_factor,
                status_forcelist=set(status_forcelist.keys()),
                allowed_methods=methods,
            )
        except TypeError:
            # Fallback for older urllib3 that uses method_whitelist and doesn't support 'status'
            retry = Retry(
                total=retries,
                connect=retries,
                read=retries,
                backoff_factor=backoff_factor,
                status_forcelist=set(status_forcelist.keys()),
                method_whitelist=methods,  # type: ignore[arg-type]
            )

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        endpoint = (endpoint or "").strip()
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return f"{self.base_url}{endpoint}"

    def make_request(
        self,
        endpoint: str,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        method: str = "GET",
        json: Any = None,
        data: Any = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        merged_params: Dict[str, Any] = dict(self.default_params)
        if params:
            merged_params.update(params)

        resp = self.session.request(
            method=method.upper(),
            url=url,
            params=merged_params or None,
            headers=merged_headers or None,
            json=json,
            data=data,
            timeout=timeout if timeout is not None else self.timeout,
        )
        return resp

    def get(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET", timeout=timeout)

    def post(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json=json, data=data, timeout=timeout)

    def put(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json=json, data=data, timeout=timeout)

    def patch(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json=json, data=data, timeout=timeout)

    def delete(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", timeout=timeout)

    def head(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="HEAD", timeout=timeout)

    def options(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="OPTIONS", timeout=timeout)


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load configuration from config.yml located in the same directory as this conftest.py.
    Expands ${ENV_VAR:-default} placeholders using environment variables.
    """
    base_dir = Path(__file__).parent
    config_path = Path(os.path.join(base_dir, "config.yml"))
    cfg = _load_yaml_config(config_path)
    return cfg


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    try:
        host = config["api"]["host"]
    except Exception:
        pytest.fail("Missing required key: api.host in config.yml")
    return str(host).strip().rstrip("/")


@pytest.fixture(scope="session")
def host(api_host: str) -> str:
    # Alias for convenience
    return api_host


@pytest.fixture(scope="session")
def auth_api_key_header(config: Dict[str, Any]) -> str:
    # Token value for API key provided via header (if any)
    return str(config.get("auth", {}).get("api_key_header", "") or "").strip()


@pytest.fixture(scope="session")
def auth_api_key_query(config: Dict[str, Any]) -> str:
    # Token value for API key provided via query param (if any)
    return str(config.get("auth", {}).get("api_key_query", "") or "").strip()


@pytest.fixture(scope="session")
def auth(auth_api_key_header: str, auth_api_key_query: str) -> Dict[str, Dict[str, str]]:
    """
    Compose default auth headers/params using known names from the provided structure.
    - Header name: Circle-Token
    - Query param name: circle-token
    """
    headers: Dict[str, str] = {}
    params: Dict[str, str] = {}

    if auth_api_key_header:
        headers["Circle-Token"] = auth_api_key_header

    if auth_api_key_query:
        params["circle-token"] = auth_api_key_query

    return {"headers": headers, "params": params}


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provides the test_data section from config.yml.
    """
    return dict(config.get("test_data", {}) or {})


@pytest.fixture(scope="session")
def api_client(api_host: str, auth: Dict[str, Dict[str, str]]) -> APIClient:
    """
    Provides a configured API client that uses values from the config rather than hardcoded values.
    Includes basic retry and timeout configuration.
    """
    return APIClient(
        base_url=api_host,
        default_headers=auth.get("headers") or {},
        default_params=auth.get("params") or {},
        timeout=30.0,
        retries=3,
        backoff_factor=0.5,
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: For all success scenarios")
