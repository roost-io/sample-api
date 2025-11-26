# conftest.py

import os
import re
import json
import logging
from typing import Any, Dict, Optional, Mapping

import pytest
import requests
import yaml
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _read_file_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise RuntimeError(f"config.yml not found at: {path}") from e
    except Exception as e:
        raise RuntimeError(f"Error reading config.yml at {path}: {e}") from e


def _expand_env_in_string(value: str) -> str:
    # Supports patterns like ${ENV_VAR} and ${ENV_VAR:-default}
    # Allows hyphens in var names as provided in the config schema.
    pattern = re.compile(r"\$\{([^}:]+)(?::-(.*?))?\}")

    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        default = match.group(2) if match.group(2) is not None else ""
        env_val = os.environ.get(var_name)
        return env_val if env_val is not None and env_val != "" else default

    # Apply repeatedly until no more placeholders remain or no change
    prev = None
    curr = value
    max_iter = 10
    while prev != curr and max_iter > 0:
        prev = curr
        curr = pattern.sub(replacer, curr)
        max_iter -= 1
    return curr


def _expand_env_in_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _expand_env_in_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_in_obj(i) for i in obj]
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    return obj


def _load_config_from_yaml() -> Dict[str, Any]:
    # Use os.path.join to locate config.yml in same directory as this conftest.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(base_dir, "config.yml")
    cfg_file = Path(cfg_path)

    raw = _read_file_text(cfg_file)
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid YAML in config.yml: {e}") from e

    expanded = _expand_env_in_obj(data)

    # Sanity: ensure api.host exists (per provided schema)
    api = expanded.get("api", {})
    if not isinstance(api, dict) or "host" not in api:
        raise RuntimeError("config.yml must include 'api.host'")

    # Normalize host whitespace early
    if isinstance(api.get("host"), str):
        expanded["api"]["host"] = api["host"].strip()

    return expanded


class APIClient:
    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Mapping[str, str]] = None,
        default_params: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Optional[list] = None,
    ) -> None:
        if not base_url or not isinstance(base_url, str):
            raise ValueError("base_url must be a non-empty string")
        self.base_url = base_url.strip().rstrip("/")
        self.default_headers = dict(default_headers or {})
        self.default_params = dict(default_params or {})
        self.timeout = timeout if timeout is not None else float(os.environ.get("API_TIMEOUT", "30"))

        if status_forcelist is None:
            status_forcelist = [429, 500, 502, 503, 504]

        self.session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            status=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=frozenset(["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"]),
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        # Generic defaults
        self.session.headers.setdefault("Accept", "application/json")

        if self.default_headers:
            self.session.headers.update(self.default_headers)

    def _prepare_url(self, endpoint: str) -> str:
        if not endpoint:
            return self.base_url
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _merge(self, base: Optional[Mapping[str, Any]], extra: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        merged = dict(base or {})
        if extra:
            for k, v in extra.items():
                # None values should remove the key
                if v is None and k in merged:
                    merged.pop(k, None)
                elif v is not None:
                    merged[k] = v
        return merged

    def make_request(
        self,
        endpoint: str,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        method: str = "GET",
        json_body: Any = None,
        data: Any = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = self._prepare_url(endpoint)
        req_params = self._merge(self.default_params, params)
        req_headers = self._merge(self.session.headers, headers)
        eff_timeout = timeout if timeout is not None else self.timeout

        response = self.session.request(
            method=method.upper(),
            url=url,
            params=req_params or None,
            headers=req_headers or None,
            json=json_body,
            data=data,
            timeout=eff_timeout,
        )
        return response

    def get(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET", timeout=timeout)

    def post(self, endpoint: str, json_body: Any = None, data: Any = None, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json_body=json_body, data=data, timeout=timeout)

    def put(self, endpoint: str, json_body: Any = None, data: Any = None, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json_body=json_body, data=data, timeout=timeout)

    def patch(self, endpoint: str, json_body: Any = None, data: Any = None, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json_body=json_body, data=data, timeout=timeout)

    def delete(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", timeout=timeout)

    def options(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="OPTIONS", timeout=timeout)

    def head(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="HEAD", timeout=timeout)


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    cfg = _load_config_from_yaml()
    return cfg


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    host = config.get("api", {}).get("host", "")
    if not isinstance(host, str) or not host.strip():
        raise RuntimeError("api.host must be a non-empty string in config.yml")
    return host.strip()


@pytest.fixture(scope="session")
def auth_tokens(config: Dict[str, Any]) -> Dict[str, str]:
    # Exact keys per provided schema
    auth = config.get("auth", {}) or {}
    token_header = auth.get("api_key_header", "") or ""
    token_query = auth.get("api_key_query", "") or ""
    return {
        "api_key_header": token_header,
        "api_key_query": token_query,
    }


@pytest.fixture(scope="session")
def auth_headers(auth_tokens: Dict[str, str]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    # CircleCI API v2 typically uses 'Circle-Token' header
    if auth_tokens.get("api_key_header"):
        headers["Circle-Token"] = auth_tokens["api_key_header"]
    return headers


@pytest.fixture(scope="session")
def auth_params(auth_tokens: Dict[str, str]) -> Dict[str, str]:
    params: Dict[str, str] = {}
    # Legacy CircleCI patterns often accept 'circle-token' as a query param
    if auth_tokens.get("api_key_query"):
        params["circle-token"] = auth_tokens["api_key_query"]
    return params


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    # Per schema: keep exact hyphenated keys
    return dict(config.get("test_data", {}) or {})


@pytest.fixture(scope="session")
def api_client(api_host: str, auth_headers: Dict[str, str], auth_params: Dict[str, str]) -> APIClient:
    # Defaults with retries and timeout; environment can override timeout via API_TIMEOUT env var
    client = APIClient(
        base_url=api_host,
        default_headers=auth_headers,
        default_params=auth_params,
        retries=3,
        backoff_factor=0.5,
    )
    return client


def pytest_configure(config_pytest) -> None:
    # Register markers
    config_pytest.addinivalue_line("markers", "smoke: For all success scenarios")
