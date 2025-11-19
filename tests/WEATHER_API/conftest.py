# conftest.py

import os
import re
import json
from pathlib import Path
from typing import Any, Dict, Optional, Mapping, Union

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def _strip_wrapping_quotes(value: str) -> str:
    """
    Remove a single pair of matching wrapping quotes if present.
    This helps when YAML contains values like '"${VAR:-default}"' (double quotes preserved as literal).
    """
    if not isinstance(value, str):
        return value
    s = value.strip()
    if len(s) >= 2 and ((s[0] == s[-1]) and s[0] in ("'", '"')):
        return s[1:-1]
    return s


_ENV_PATTERN = re.compile(r"\$\{(?P<name>[A-Za-z_][A-Za-z0-9_]*)?(?::-(?P<default>[^}]*))?\}")


def _expand_env_in_string(s: str) -> str:
    """
    Expand ${VAR} or ${VAR:-default} inside a string using environment variables.
    - If VAR is not set and default is provided, use default.
    - If VAR is not set and default is not provided, substitute with empty string.
    Process repeatedly until no more patterns remain.
    Also trims wrapping quotes that may have been persisted by YAML quoting.
    """
    if not isinstance(s, str):
        return s

    # Remove wrapping quotes first (if any)
    s = _strip_wrapping_quotes(s)

    def repl(match: re.Match) -> str:
        name = match.group("name")
        default = match.group("default")
        val = os.environ.get(name)
        if val is None:
            val = "" if default is None else default
        return str(val)

    previous = None
    current = s
    # Repeat until stable in case expansion introduces new ${...} patterns
    for _ in range(10):
        previous = current
        current = _ENV_PATTERN.sub(repl, current)
        if current == previous:
            break

    # Final trimming of wrapping quotes (in case the expansion resulted in quoted values)
    current = _strip_wrapping_quotes(current).strip()
    return current


def _expand_env_in_obj(obj: Any) -> Any:
    """
    Recursively expand environment variables in strings within nested dicts/lists.
    """
    if isinstance(obj, dict):
        return {k: _expand_env_in_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_in_obj(item) for item in obj]
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    return obj


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """
    Load YAML configuration with error handling and environment expansion.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML at {config_path}: {e}") from e

    # Ensure dict
    if not isinstance(raw, dict):
        raise TypeError(f"Configuration at {config_path} must be a mapping/object.")

    # Expand environment variables for all string values
    expanded = _expand_env_in_obj(raw)
    return expanded


class APIClient:
    """
    Simple API client built on requests.Session with retry and timeout handling.
    Uses base_url from config['api']['host'].
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Optional[list] = None,
        allowed_methods: Optional[Union[frozenset, set]] = None,
        default_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        if status_forcelist is None:
            status_forcelist = [429, 500, 502, 503, 504]
        if allowed_methods is None:
            allowed_methods = frozenset({"HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"})

        self.base_url = (base_url or "").strip()
        # Normalize base URL: remove trailing slash to avoid double slashes
        self.base_url = self.base_url.rstrip("/")
        if not self.base_url:
            raise ValueError("base_url must be provided and non-empty")

        self.timeout = timeout

        self.session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=allowed_methods,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.default_headers: Dict[str, str] = {"Accept": "application/json"}
        if default_headers:
            self.default_headers.update(dict(default_headers))

    def _full_url(self, endpoint: str) -> str:
        ep = (endpoint or "").strip()
        if not ep:
            return self.base_url
        if ep.startswith("http://") or ep.startswith("https://"):
            return ep
        # Ensure single slash between base and endpoint
        if not ep.startswith("/"):
            ep = "/" + ep
        return f"{self.base_url}{ep}"

    def make_request(
        self,
        endpoint: str,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        method: str = "GET",
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_body: Optional[Any] = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = self._full_url(endpoint)
        method = (method or "GET").upper()
        hdrs = dict(self.default_headers)
        if headers:
            hdrs.update(headers)

        # If json_body provided, prefer setting content-type automatically
        if json_body is not None and "Content-Type" not in {k.title(): v for k, v in hdrs.items()}:
            hdrs.setdefault("Content-Type", "application/json")

        try:
            resp = self.session.request(
                method=method,
                url=url,
                params=dict(params) if params else None,
                headers=hdrs,
                data=data,
                json=json_body,
                timeout=self._resolve_timeout(timeout),
            )
        except requests.RequestException as e:
            # Re-raise with context that includes URL and method
            raise RuntimeError(f"Request failed: {method} {url} - {e}") from e

        return resp

    def _resolve_timeout(self, timeout: Optional[float]) -> float:
        if timeout is None:
            return self.timeout
        try:
            return float(timeout)
        except (TypeError, ValueError):
            return self.timeout

    # Convenience methods
    def get(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint=endpoint, method="GET", headers=headers, params=params, timeout=timeout)

    def post(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, data: Optional[Union[Dict[str, Any], str, bytes]] = None, json: Optional[Any] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint=endpoint, method="POST", headers=headers, params=params, data=data, json_body=json, timeout=timeout)

    def put(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, data: Optional[Union[Dict[str, Any], str, bytes]] = None, json: Optional[Any] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint=endpoint, method="PUT", headers=headers, params=params, data=data, json_body=json, timeout=timeout)

    def patch(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, data: Optional[Union[Dict[str, Any], str, bytes]] = None, json: Optional[Any] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint=endpoint, method="PATCH", headers=headers, params=params, data=data, json_body=json, timeout=timeout)

    def delete(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint=endpoint, method="DELETE", headers=headers, params=params, timeout=timeout)

    def head(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint=endpoint, method="HEAD", headers=headers, params=params, timeout=timeout)

    def options(self, endpoint: str, headers: Optional[Mapping[str, str]] = None, params: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None) -> requests.Response:
        return self.make_request(endpoint=endpoint, method="OPTIONS", headers=headers, params=params, timeout=timeout)


def _resolve_config_path() -> Path:
    """
    Resolve config.yml path located in the same directory as this conftest.py.
    The instruction requires using os.path.join to find it, while also leveraging pathlib.
    """
    here = Path(__file__).resolve().parent
    # Use os.path.join as requested to construct the path
    cfg_path_str = os.path.join(str(here), "config.yml")
    return Path(cfg_path_str)


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load user config from config.yml and expand ${ENV:-default} placeholders.
    Expected structure:
      api:
        host: '"${API_HOST:-https://api.weatherapi.com}"'
    """
    cfg_path = _resolve_config_path()
    try:
        cfg = _load_yaml_config(cfg_path)
    except (FileNotFoundError, ValueError, TypeError) as e:
        raise pytest.UsageError(f"Unable to load configuration: {e}") from e

    # Validate minimal expected keys based on provided structure
    # Follow strictly same KEY and do not assume any custom key.
    if "api" not in cfg or not isinstance(cfg["api"], dict):
        raise pytest.UsageError("Configuration must include 'api' mapping.")
    if "host" not in cfg["api"]:
        raise pytest.UsageError("Configuration must include 'api.host'.")

    # Normalize host (strip whitespace)
    host_val = cfg["api"]["host"]
    if isinstance(host_val, str):
        cfg["api"]["host"] = host_val.strip()

    return cfg


@pytest.fixture(scope="session")
def api_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provides the 'api' subsection of config.
    """
    return config["api"]


@pytest.fixture(scope="session")
def api_host(api_config: Dict[str, Any]) -> str:
    """
    Provides the API host/base URL from config.
    """
    host = api_config["host"]
    if not isinstance(host, str) or not host.strip():
        raise pytest.UsageError("The 'api.host' value must be a non-empty string.")
    return host.strip()


@pytest.fixture(scope="session")
def api_client(api_host: str) -> APIClient:
    """
    Provides an APIClient instance configured from config.
    Timeout and retry settings are configured with sane defaults.
    """
    # Defaults can optionally be influenced by environment variables if provided.
    # Not adding new config keys per requirement.
    timeout_env = os.environ.get("API_CLIENT_TIMEOUT")
    retries_env = os.environ.get("API_CLIENT_RETRIES")
    backoff_env = os.environ.get("API_CLIENT_BACKOFF")

    def _to_float(val: Optional[str], default: float) -> float:
        if val is None:
            return default
        try:
            return float(val)
        except ValueError:
            return default

    def _to_int(val: Optional[str], default: int) -> int:
        if val is None:
            return default
        try:
            return int(val)
        except ValueError:
            return default

    client = APIClient(
        base_url=api_host,
        timeout=_to_float(timeout_env, 10.0),
        retries=_to_int(retries_env, 3),
        backoff_factor=_to_float(backoff_env, 0.5),
    )
    return client
