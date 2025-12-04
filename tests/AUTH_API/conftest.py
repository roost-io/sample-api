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


def pytest_configure(config: pytest.Config) -> None:
    # Register markers
    config.addinivalue_line("markers", "smoke: mark tests as smoke (success scenarios)")


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        pytest.exit(f"Configuration file not found at: {config_path}", returncode=2)
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                pytest.exit(f"Configuration file must contain a YAML mapping (dict) at root. Got: {type(data)}", 2)
            return data
    except yaml.YAMLError as e:
        pytest.exit(f"Failed to parse YAML configuration: {e}", returncode=2)
    except Exception as e:
        pytest.exit(f"Unexpected error reading configuration: {e}", returncode=2)


# Regex pattern: ${ENV_VAR:-defaultValue}
_ENV_WITH_DEFAULT_PATTERN = re.compile(r"\$\{([^}:\s]+):-([^}]+)\}")
# Regex pattern for simple ${ENV_VAR}
_ENV_SIMPLE_PATTERN = re.compile(r"\$\{([^}:\s]+)\}")


def _expand_env_in_string(value: str) -> str:
    # First expand ${VAR:-default}
    def repl_with_default(match: re.Match) -> str:
        var, default = match.group(1), match.group(2)
        return os.environ.get(var, default)

    expanded = _ENV_WITH_DEFAULT_PATTERN.sub(repl_with_default, value)

    # Then expand simple ${VAR} (if any)
    def repl_simple(match: re.Match) -> str:
        var = match.group(1)
        return os.environ.get(var, "")

    expanded = _ENV_SIMPLE_PATTERN.sub(repl_simple, expanded)
    return expanded


def _expand_env_in_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    if isinstance(obj, list):
        return [_expand_env_in_obj(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _expand_env_in_obj(v) for k, v in obj.items()}
    return obj


class APIClient:
    def __init__(
        self,
        base_url: str,
        timeout: Union[float, tuple] = 30.0,
        retries: Optional[Retry] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = (base_url or "").strip()
        self.timeout = timeout
        self.session = session or requests.Session()

        # Configure retries
        if retries is None:
            retries = Retry(
                total=3,
                connect=3,
                read=3,
                status=3,
                backoff_factor=0.3,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=frozenset(["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"]),
                raise_on_status=False,
            )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        # Robust URL join: avoid double slashes
        ep = (endpoint or "").strip()
        if not ep:
            return self.base_url
        if self.base_url.endswith("/") and ep.startswith("/"):
            return f"{self.base_url.rstrip('/')}/{ep.lstrip('/')}"
        if not self.base_url.endswith("/") and not ep.startswith("/"):
            return f"{self.base_url}/{ep}"
        return f"{self.base_url}{ep}"

    def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, tuple]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        req_headers = {
            "Accept": "application/json, */*;q=0.8",
        }
        if headers:
            req_headers.update(headers)

        # If timeout not provided per request, use default
        req_timeout = timeout if timeout is not None else self.timeout

        resp = self.session.request(method=method.upper(), url=url, headers=req_headers, timeout=req_timeout, **kwargs)
        return resp

    def get(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, method="GET", **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, method="POST", **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, method="PUT", **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, method="DELETE", **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, method="PATCH", **kwargs)

    def head(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, method="HEAD", **kwargs)

    def options(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.make_request(endpoint, method="OPTIONS", **kwargs)

    def close(self) -> None:
        try:
            self.session.close()
        except Exception:
            pass


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    # Locate config.yml in the same directory as this conftest.py (using os.path.join and pathlib)
    base_dir = Path(__file__).resolve().parent
    config_path = Path(os.path.join(str(base_dir), "config.yml"))
    raw = _load_yaml_config(config_path)
    expanded = _expand_env_in_obj(raw)

    # Ensure keys exist per provided structure, do not introduce new keys
    if "api" not in expanded or not isinstance(expanded["api"], dict):
        expanded["api"] = {}
    if "test_data" not in expanded:
        expanded["test_data"] = {}

    return expanded


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    # Strictly adhere to provided keys
    host = ""
    api_cfg = config.get("api") or {}
    if isinstance(api_cfg, dict):
        host = str(api_cfg.get("host") or "")
    return host.strip()


@pytest.fixture(scope="session")
def api_client(api_host: str) -> APIClient:
    # Defaults for timeout and retries; not assumed to be in config to respect key constraints
    default_timeout = 30.0  # seconds
    retries = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"]),
        raise_on_status=False,
    )
    client = APIClient(base_url=api_host, timeout=default_timeout, retries=retries)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    # Return test_data exactly as provided in config
    td = config.get("test_data")
    return td if isinstance(td, dict) else {}
