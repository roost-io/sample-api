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


def pytest_configure(config):  # register markers
    config.addinivalue_line("markers", "smoke: For all success scenarios")


_ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::-(.*?))?\}")


def _expand_env_in_string(value: str) -> str:
    """
    Expand environment variable placeholders in the form ${VAR:-default}.
    If VAR is unset, use 'default' (which may be empty). If no default provided and
    VAR is unset, replace with empty string.
    """
    def repl(match: re.Match) -> str:
        var_name = match.group(1)
        default = match.group(2) if match.group(2) is not None else ""
        return os.environ.get(var_name, default)

    # Process repeatedly until no patterns remain (handles multiple occurrences)
    prev = None
    cur = value
    # Guard against infinite loops by limiting passes
    for _ in range(5):
        prev = cur
        cur = _ENV_PATTERN.sub(repl, cur)
        if cur == prev:
            break
    return cur


def _expand_env(obj: Any) -> Any:
    """
    Recursively expand env placeholders for all strings in the given structure.
    """
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(v) for v in obj]
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    return obj


def _load_config() -> Dict[str, Any]:
    """
    Load YAML config from config.yml located in the same directory as this file.
    Expand env vars where required and normalize values.
    """
    base_dir = Path(__file__).parent
    cfg_path = Path(os.path.join(str(base_dir), "config.yml"))
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found at: {cfg_path}")

    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Failed to parse YAML config at {cfg_path}: {exc}") from exc

    # Expand environment vars
    cfg = _expand_env(raw)

    # Make base URL robust (strip whitespace)
    api_section = cfg.get("api") or {}
    host = api_section.get("host", "")
    if isinstance(host, str):
        api_section["host"] = host.strip()
    else:
        api_section["host"] = ""

    cfg["api"] = api_section

    # Ensure required top-level keys exist, without assuming extra/custom keys
    if "auth" not in cfg:
        cfg["auth"] = {}
    if "test_data" not in cfg:
        cfg["test_data"] = {}

    return cfg


class APIClient:
    """
    Simple API client leveraging requests.Session with retry and timeout defaults.
    Host and other details are sourced from the provided config.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 15.0,
        total_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("A valid base_url must be provided.")
        self.base_url = base_url.strip()
        self.timeout = timeout

        # Configure session with retries
        self.session = requests.Session()
        retry = Retry(
            total=total_retries,
            connect=total_retries,
            read=total_retries,
            status=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _join_url(self, endpoint: str) -> str:
        if not endpoint:
            return self.base_url
        ep = endpoint.strip()
        # If absolute URL provided, use it directly
        if ep.lower().startswith(("http://", "https://")):
            return ep
        return f"{self.base_url.rstrip('/')}/{ep.lstrip('/')}"

    def _prepare_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        base = {
            "Accept": "application/json",
        }
        if headers:
            base.update(headers)
        return base

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
    ) -> requests.Response:
        url = self._join_url(endpoint)
        merged_headers = self._prepare_headers(headers)
        resp = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=merged_headers,
            timeout=self.timeout,
        )
        return resp

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self.make_request(endpoint=endpoint, params=params, headers=headers, method="GET")

    def post(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Any = None,
        data: Any = None,
    ) -> requests.Response:
        url = self._join_url(endpoint)
        merged_headers = self._prepare_headers(headers)
        return self.session.request(
            method="POST",
            url=url,
            params=params,
            headers=merged_headers,
            json=json,
            data=data,
            timeout=self.timeout,
        )

    def put(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Any = None,
        data: Any = None,
    ) -> requests.Response:
        url = self._join_url(endpoint)
        merged_headers = self._prepare_headers(headers)
        return self.session.request(
            method="PUT",
            url=url,
            params=params,
            headers=merged_headers,
            json=json,
            data=data,
            timeout=self.timeout,
        )

    def patch(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Any = None,
        data: Any = None,
    ) -> requests.Response:
        url = self._join_url(endpoint)
        merged_headers = self._prepare_headers(headers)
        return self.session.request(
            method="PATCH",
            url=url,
            params=params,
            headers=merged_headers,
            json=json,
            data=data,
            timeout=self.timeout,
        )

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        return self.make_request(endpoint=endpoint, params=params, headers=headers, method="DELETE")


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load and provide the merged/expanded configuration.
    """
    return _load_config()


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    """
    Provide the API host/base URL from config.
    """
    host = (config.get("api") or {}).get("host", "")
    if not host:
        raise pytest.UsageError("Missing required 'api.host' in config.yml")
    return host.strip()


@pytest.fixture(scope="session")
def api_auth(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide the 'auth' section as-is from config.
    """
    return config.get("auth") or {}


@pytest.fixture(scope="session")
def api_auth_api_key(api_auth: Dict[str, Any]) -> str:
    """
    Provide the ApiKeyAuth value from the 'auth' section.
    """
    return api_auth.get("ApiKeyAuth", "")


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide test_data from config.
    """
    td = config.get("test_data")
    return td if isinstance(td, dict) else {}


@pytest.fixture(scope="session")
def api_client(api_host: str) -> APIClient:
    """
    Provide an API client configured using the loaded config values.
    """
    # Defaults for timeout/retries are set within APIClient; not sourced from config to avoid assuming custom keys.
    return APIClient(base_url=api_host)
