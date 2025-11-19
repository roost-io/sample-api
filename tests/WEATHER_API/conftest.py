# conftest.py

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _read_file_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except Exception:
        # Any other IO error should not crash test collection
        return None


def _safe_yaml_load(text: str) -> Dict[str, Any]:
    try:
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except yaml.YAMLError:
        # Bad YAML should not kill test run; fall back to minimal structure
        return {}


_env_pattern = re.compile(r"\$\{([^}:]+)(?::-(.*?))?\}")


def _strip_wrapping_quotes(s: str) -> str:
    if not s:
        return s
    s = s.strip()
    # Remove single or double quotes that wrap the entire string
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    return s


def _sanitize_unbalanced_braces(s: str) -> str:
    # If there are trailing unmatched closing braces, trim them
    # Count braces to decide minimal trimming
    open_braces = s.count("{")
    close_braces = s.count("}")
    if close_braces > open_braces:
        s = s.rstrip("}")
        # re-check once more in case of multiple
        open_braces = s.count("{")
        close_braces = s.count("}")
        if close_braces > open_braces:
            s = s.rstrip("}")
    return s


def _parse_default_value(raw_default: Optional[str]) -> str:
    if raw_default is None:
        return ""
    d = raw_default.strip()

    # Handle coalesce-like syntax "a ?? b" by picking first non-empty after cleaning quotes
    candidates = [d]
    if "??" in d:
        candidates = [c.strip() for c in d.split("??")]

    for cand in candidates:
        c = cand.strip()
        # Strip wrapping quotes
        c = _strip_wrapping_quotes(c)
        # Interpret "" or '' as empty string
        if c in ('""', "''"):
            c = ""
        if c != "":
            return c
    return ""


def _expand_env_in_string(value: str) -> str:
    if not isinstance(value, str):
        return value

    original = value

    # Pre-sanitize to mitigate malformed inputs
    value = _sanitize_unbalanced_braces(value)
    value = value.strip()

    def repl(match: re.Match) -> str:
        var = match.group(1).strip()
        default = _parse_default_value(match.group(2))
        env_val = os.environ.get(var)
        if env_val is not None:
            return env_val
        return default

    expanded = _env_pattern.sub(repl, value)
    expanded = _strip_wrapping_quotes(expanded).strip()
    return expanded


def _expand_env(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(x) for x in obj]
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    return obj


def _ensure_config_keys(conf: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure required top-level keys exist with the exact same structure
    conf.setdefault("api", {})
    conf.setdefault("auth", {})
    if not isinstance(conf["api"], dict):
        conf["api"] = {}
    if not isinstance(conf["auth"], dict):
        conf["auth"] = {}
    conf["api"].setdefault("host", "")
    conf["auth"].setdefault("ApiKeyAuth", "")
    return conf


def _load_config_from_yaml() -> Dict[str, Any]:
    # Find config.yml located in the same directory as this conftest.py
    here = Path(__file__).resolve().parent
    # Requirement: use os.path.join to find config file in same directory
    cfg_path = Path(os.path.join(str(here), "config.yml"))
    content = _read_file_text(cfg_path)
    if not content:
        conf = {}
    else:
        conf = _safe_yaml_load(content)

    conf = _expand_env(conf)
    conf = _ensure_config_keys(conf)

    # Clean up host and ApiKeyAuth strings (remove stray quotes/whitespace)
    api_host = conf.get("api", {}).get("host", "")
    conf["api"]["host"] = _strip_wrapping_quotes(str(api_host or "")).strip()

    api_key_auth = conf.get("auth", {}).get("ApiKeyAuth", "")
    api_key_auth = _strip_wrapping_quotes(str(api_key_auth or "")).strip()
    conf["auth"]["ApiKeyAuth"] = api_key_auth

    return conf


class APIClient:
    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        default_params: Optional[Dict[str, Any]] = None,
        timeout: Union[int, float] = 15,
        retries: int = 3,
        backoff_factor: float = 0.3,
    ):
        self.base_url = (base_url or "").strip()
        # Normalize base_url: remove trailing slashes
        self.base_url = self.base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.default_params = default_params or {}
        self.timeout = timeout

        self.session = requests.Session()

        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        ep = (endpoint or "").strip()
        if ep.startswith("http://") or ep.startswith("https://"):
            return ep
        if not self.base_url:
            # No base_url supplied; return endpoint as-is
            return ep
        if not ep:
            return self.base_url
        if ep.startswith("/"):
            return f"{self.base_url}{ep}"
        return f"{self.base_url}/{ep}"

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        json: Any = None,
        data: Any = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        req_headers = dict(self.default_headers)
        if headers:
            req_headers.update(headers)

        req_params = dict(self.default_params)
        if params:
            req_params.update(params)

        resp = self.session.request(
            method=method.upper().strip(),
            url=url,
            headers=req_headers,
            params=req_params,
            json=json,
            data=data,
            timeout=self._resolve_timeout(timeout),
        )
        return resp

    def _resolve_timeout(self, timeout: Optional[Union[int, float]]) -> Union[int, float]:
        if timeout is None:
            return self.timeout
        return timeout

    # Convenience methods
    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET", timeout=timeout)

    def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json=json, data=data, timeout=timeout)

    def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json=json, data=data, timeout=timeout)

    def patch(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json=json, data=data, timeout=timeout)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", timeout=timeout)

    def head(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="HEAD", timeout=timeout)

    def options(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: Optional[Union[int, float]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="OPTIONS", timeout=timeout)


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load configuration from config.yml (same directory as this file),
    expand ${VAR:-default} with environment values, and return dict with structure:
    {
        "api": {"host": "..."},
        "auth": {"ApiKeyAuth": "..."}
    }
    """
    return _load_config_from_yaml()


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    host = (config.get("api", {}).get("host", "") or "").strip()
    # Strip wrapping quotes that might have been preserved from YAML
    host = _strip_wrapping_quotes(host)
    return host


@pytest.fixture(scope="session")
def api_key_auth(config: Dict[str, Any]) -> str:
    key = (config.get("auth", {}).get("ApiKeyAuth", "") or "").strip()
    key = _strip_wrapping_quotes(key)
    return key


@pytest.fixture(scope="session")
def default_params(api_key_auth: str) -> Dict[str, Any]:
    """
    Default params included in each request.
    If ApiKeyAuth is provided, pass it as a 'key' query parameter.
    """
    params: Dict[str, Any] = {}
    if api_key_auth:
        params["key"] = api_key_auth
    return params


@pytest.fixture(scope="session")
def default_headers() -> Dict[str, str]:
    """
    Default headers for all requests (empty by default).
    """
    return {}


@pytest.fixture
def api_client(api_host: str, default_headers: Dict[str, str], default_params: Dict[str, Any]) -> APIClient:
    """
    A simple, retry-enabled API client that uses config values.
    """
    return APIClient(
        base_url=api_host,
        default_headers=default_headers,
        default_params=default_params,
        timeout=15,
        retries=3,
        backoff_factor=0.3,
    )
