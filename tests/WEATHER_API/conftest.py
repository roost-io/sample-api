# conftest.py

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Mapping

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _maybe_strip_wrapping_quotes(value: str) -> str:
    s = value.strip()
    if (len(s) >= 2) and ((s[0] == s[-1]) and s[0] in ("'", '"')):
        return s[1:-1]
    return s


_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)?(?::-(.*?))?\}")


def _expand_env_in_string(value: str) -> str:
    """
    Replace ${ENV_VAR:-default} patterns using environment variables.
    - ${VAR} -> requires VAR in env, else empty string
    - ${VAR:-default} -> uses env if present, else default
    """
    def replacer(match: re.Match) -> str:
        var = match.group(1) or ""
        default = match.group(2)
        if var:
            if var in os.environ:
                return os.environ[var]
            if default is not None:
                return default
            # If no default and var not in env, return empty string
            return ""
        return match.group(0)

    expanded = _ENV_PATTERN.sub(replacer, value)
    expanded = _maybe_strip_wrapping_quotes(expanded)
    return expanded.strip()


def _expand_env_in_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    if isinstance(obj, Mapping):
        return {k: _expand_env_in_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_in_obj(i) for i in obj]
    return obj


def _load_config_from_yaml() -> Dict[str, Any]:
    # Locate config.yml in the same directory as this file using pathlib and os.path.join
    here = Path(__file__).resolve().parent
    config_path = Path(os.path.join(str(here), "config.yml"))

    if not config_path.exists():
        pytest.fail(f"config.yml not found at: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        pytest.fail(f"Failed to parse YAML config at {config_path}: {e}")
    except OSError as e:
        pytest.fail(f"Failed to read config at {config_path}: {e}")

    expanded = _expand_env_in_obj(raw)

    # Validate required structure based on the provided configuration structure
    if "api" not in expanded or not isinstance(expanded["api"], dict):
        pytest.fail("Invalid config: missing 'api' section")
    if "host" not in expanded["api"]:
        pytest.fail("Invalid config: missing 'api.host'")

    if "auth" not in expanded or not isinstance(expanded["auth"], dict):
        pytest.fail("Invalid config: missing 'auth' section")
    if "ApiKeyAuth" not in expanded["auth"]:
        pytest.fail("Invalid config: missing 'auth.ApiKeyAuth'")

    # Normalize host: trim whitespace, remove trailing slash
    host_raw = str(expanded["api"]["host"])
    expanded["api"]["host"] = host_raw.strip().rstrip("/")

    # Normalize ApiKeyAuth to string
    expanded["auth"]["ApiKeyAuth"] = str(expanded["auth"]["ApiKeyAuth"]).strip()

    return expanded


class APIClient:
    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: float = 15.0,
        retry_total: int = 3,
        retry_backoff: float = 0.5,
        retry_statuses: Optional[tuple] = (429, 500, 502, 503, 504),
    ):
        self.base_url = (base_url or "").strip().rstrip("/")
        if not self.base_url:
            raise ValueError("Base URL must not be empty")
        self.default_headers = dict(default_headers or {})
        self.timeout = timeout

        self.session = requests.Session()
        retry = Retry(
            total=retry_total,
            read=retry_total,
            connect=retry_total,
            status=retry_total,
            backoff_factor=retry_backoff,
            status_forcelist=retry_statuses or (),
            allowed_methods=frozenset(["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"]),
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        ep = (endpoint or "").strip()
        if not ep:
            return self.base_url
        if ep.startswith("http://") or ep.startswith("https://"):
            return ep
        if not ep.startswith("/"):
            ep = "/" + ep
        return f"{self.base_url}{ep}"

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        json: Any = None,
        data: Any = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=merged_headers,
            json=json,
            data=data,
            timeout=timeout if timeout is not None else self.timeout,
        )
        return response

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET", timeout=timeout)

    def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json=json, data=data, timeout=timeout)

    def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json=json, data=data, timeout=timeout)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", timeout=timeout)

    def patch(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json=json, data=data, timeout=timeout)

    def head(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="HEAD", timeout=timeout)

    def options(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="OPTIONS", timeout=timeout)


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Loads and returns the YAML configuration after expanding ${ENV_VAR:-default} placeholders.
    Follows the exact keys as provided:
    - api.host
    - auth.ApiKeyAuth
    """
    return _load_config_from_yaml()


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    return str(config["api"]["host"]).strip().rstrip("/")


@pytest.fixture(scope="session")
def api_key(config: Dict[str, Any]) -> str:
    return str(config["auth"]["ApiKeyAuth"]).strip()


@pytest.fixture(scope="session")
def auth(config: Dict[str, Any]) -> Dict[str, Any]:
    return dict(config["auth"])


@pytest.fixture(scope="session")
def default_headers() -> Dict[str, str]:
    """
    Default headers for API requests. Override in tests if needed.
    Not assuming any particular auth header scheme.
    """
    return {}


@pytest.fixture(scope="session")
def api_client(api_host: str, default_headers: Dict[str, str]) -> APIClient:
    """
    Provides a reusable API client that uses the config-derived base URL.
    Includes sensible timeout and retry settings.
    """
    client = APIClient(
        base_url=api_host,
        default_headers=default_headers,
        timeout=15.0,
        retry_total=3,
        retry_backoff=0.5,
        retry_statuses=(429, 500, 502, 503, 504),
    )
    return client
