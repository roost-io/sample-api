# conftest.py

import os
import re
from pathlib import Path
from typing import Any, Dict, Union, Iterable, Optional

import pytest
import yaml
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


_ENV_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*?))?\}")


def _expand_env_vars_in_string(value: str) -> str:
    def repl(match: re.Match) -> str:
        var_name = match.group(1)
        default_val = match.group(2)
        return os.environ.get(var_name, default_val if default_val is not None else "")
    return _ENV_VAR_PATTERN.sub(repl, value)


def _expand_env_vars(obj: Any) -> Any:
    if isinstance(obj, str):
        return _expand_env_vars_in_string(obj)
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_vars(v) for v in obj]
    return obj


def _normalize_base_url(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError("api.host must be a string")
    url = url.strip().strip('"').strip("'").strip()
    if url.endswith("/"):
        url = url[:-1]
    return url


def _normalize_endpoint(endpoint: str) -> str:
    ep = (endpoint or "").strip()
    if ep.startswith("http://") or ep.startswith("https://"):
        return ep
    if not ep.startswith("/"):
        ep = "/" + ep
    return ep


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise pytest.UsageError(f"Configuration file not found at: {config_path}")
    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise pytest.UsageError(f"Failed to parse YAML config at {config_path}: {e}") from e
    except OSError as e:
        raise pytest.UsageError(f"Failed to read config at {config_path}: {e}") from e

    # Expand ${VAR} and ${VAR:-default}
    expanded = _expand_env_vars(raw)

    # Validate required keys strictly as provided
    if not isinstance(expanded, dict) or "api" not in expanded or not isinstance(expanded["api"], dict):
        raise pytest.UsageError("Invalid config structure. Expected a top-level 'api' mapping.")
    if "host" not in expanded["api"]:
        raise pytest.UsageError("Invalid config structure. Missing 'api.host'.")

    # Normalize host (strip quotes/whitespace)
    try:
        expanded["api"]["host"] = _normalize_base_url(expanded["api"]["host"])
    except Exception as e:
        raise pytest.UsageError(f"Invalid api.host value in config: {e}") from e

    return expanded


class ApiClient:
    def __init__(
        self,
        base_url: str,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        status_forcelist: Optional[Iterable[int]] = None,
        default_headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = _normalize_base_url(base_url)
        self.timeout = float(os.environ.get("API_TIMEOUT", timeout if timeout is not None else 15))
        retries_val = int(os.environ.get("API_RETRIES", retries if retries is not None else 3))
        backoff_val = float(os.environ.get("API_BACKOFF", backoff_factor if backoff_factor is not None else 0.3))
        status_forcelist = tuple(status_forcelist or (429, 500, 502, 503, 504))

        self.session = requests.Session()
        self.session.headers.update(default_headers or {})

        retry = Retry(
            total=retries_val,
            connect=retries_val,
            read=retries_val,
            status=retries_val,
            backoff_factor=backoff_val,
            status_forcelist=status_forcelist,
            allowed_methods=frozenset({"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}),
            raise_on_status=False,
        )
        pool_maxsize = int(os.environ.get("API_POOL_MAXSIZE", "10"))
        adapter = HTTPAdapter(max_retries=retry, pool_maxsize=pool_maxsize)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        ep = _normalize_endpoint(endpoint)
        if ep.startswith("http://") or ep.startswith("https://"):
            return ep
        return f"{self.base_url}{ep}"

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = self._build_url(endpoint)
        req_headers = {}
        if headers:
            req_headers.update(headers)
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=req_headers,
            timeout=self.timeout,
        )
        return response

    def get(self, endpoint, headers=None, params=None):
        return self.make_request(endpoint=endpoint, params=params, headers=headers, method="GET")

    def post(self, endpoint, headers=None, params=None, json=None, data=None):
        url = self._build_url(endpoint)
        return self.session.request(
            method="POST",
            url=url,
            params=params,
            headers=headers or {},
            json=json,
            data=data,
            timeout=self.timeout,
        )

    def put(self, endpoint, headers=None, params=None, json=None, data=None):
        url = self._build_url(endpoint)
        return self.session.request(
            method="PUT",
            url=url,
            params=params,
            headers=headers or {},
            json=json,
            data=data,
            timeout=self.timeout,
        )

    def delete(self, endpoint, headers=None, params=None, json=None, data=None):
        url = self._build_url(endpoint)
        return self.session.request(
            method="DELETE",
            url=url,
            params=params,
            headers=headers or {},
            json=json,
            data=data,
            timeout=self.timeout,
        )

    def patch(self, endpoint, headers=None, params=None, json=None, data=None):
        url = self._build_url(endpoint)
        return self.session.request(
            method="PATCH",
            url=url,
            params=params,
            headers=headers or {},
            json=json,
            data=data,
            timeout=self.timeout,
        )

    def head(self, endpoint, headers=None, params=None):
        url = self._build_url(endpoint)
        return self.session.request(
            method="HEAD",
            url=url,
            params=params,
            headers=headers or {},
            timeout=self.timeout,
        )

    def options(self, endpoint, headers=None, params=None):
        url = self._build_url(endpoint)
        return self.session.request(
            method="OPTIONS",
            url=url,
            params=params,
            headers=headers or {},
            timeout=self.timeout,
        )

    def close(self):
        try:
            self.session.close()
        except Exception:
            pass


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    # Find config.yml in the same directory as this file using os.path.join with a pathlib base
    base_dir = Path(__file__).resolve().parent
    cfg_path_str = os.path.join(str(base_dir), "config.yml")
    cfg_path = Path(cfg_path_str)
    return _load_yaml_config(cfg_path)


@pytest.fixture(scope="session")
def host(config: Dict[str, Any]) -> str:
    return config["api"]["host"]


@pytest.fixture(scope="session")
def api_client(host: str) -> ApiClient:
    client = ApiClient(base_url=host)
    try:
        yield client
    finally:
        client.close()
