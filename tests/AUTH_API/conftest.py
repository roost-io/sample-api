# conftest.py
import json
import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Union

import pytest
import requests
import yaml
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ----------------------------
# Utilities
# ----------------------------

_ENV_WITH_DEFAULT_PATTERN = re.compile(r"\$\{([^}:s]+):-([^}]+)\}")
_ENV_NO_DEFAULT_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _expand_env_in_string(value: str) -> str:
    """
    Expand environment variables in the given string using patterns:
    - ${VAR:-default}
    - ${VAR}

    The first uses default when VAR is unset or empty. The second uses
    empty string when VAR is unset.
    """

    def repl_with_default(match: re.Match) -> str:
        var = match.group(1)
        default = match.group(2)
        env_val = os.environ.get(var)
        if env_val is None or env_val == "":
            return default
        return env_val

    def repl_no_default(match: re.Match) -> str:
        var = match.group(1)
        return os.environ.get(var, "")

    # Handle ${VAR:-default}
    value = _ENV_WITH_DEFAULT_PATTERN.sub(repl_with_default, value)
    # Handle ${VAR}
    value = _ENV_NO_DEFAULT_PATTERN.sub(repl_no_default, value)
    return value


def _expand_env(obj: Any) -> Any:
    """
    Recursively expand environment variables in strings within
    dictionaries and lists.
    """
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(i) for i in obj]
    if isinstance(obj, str):
        return _expand_env_in_string(obj).strip()
    return obj


def _load_yaml(path: Path) -> Dict[str, Any]:
    """
    Load a YAML file from the given path with error handling.
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML config at {path}: {e}") from e

    if not isinstance(data, dict):
        raise TypeError(f"Expected YAML root to be a mapping/dict, got: {type(data).__name__}")

    return data


def load_test_data_json(path: Union[Path, str]) -> Any:
    """
    Load and return JSON test data from a file path.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Test data JSON file not found: {p}")
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in test data file {p}: {e}") from e


# ----------------------------
# API Client
# ----------------------------

class ApiClient:
    def __init__(
        self,
        base_url: str,
        session: Optional[Session] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        timeout: Union[int, float] = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: Optional[tuple] = (429, 500, 502, 503, 504),
    ) -> None:
        base_url = (base_url or "").strip().rstrip("/")
        if not base_url:
            raise ValueError("Base URL for ApiClient cannot be empty.")
        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = dict(default_headers) if default_headers else {}

        self.session = session or requests.Session()
        # Configure retries for robust HTTP communication
        retry = Retry(
            total=max_retries,
            read=max_retries,
            connect=max_retries,
            status=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=None,  # retry on all methods by default
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        endpoint = (endpoint or "").strip()
        if not endpoint:
            return self.base_url
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint.strip()
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[Union[int, float]] = None,
        allow_redirects: bool = True,
        **kwargs: Any,
    ) -> Response:
        url = self._build_url(endpoint)
        req_headers = self.default_headers.copy()
        if headers:
            req_headers.update(headers)

        # Respect per-call timeout; fallback to client default
        effective_timeout = timeout if timeout is not None else self.timeout

        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=req_headers,
            timeout=effective_timeout,
            allow_redirects=allow_redirects,
            **kwargs,
        )
        return response

    def get(self, endpoint: str, **kwargs: Any) -> Response:
        return self.make_request(endpoint, method="GET", **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> Response:
        return self.make_request(endpoint, method="POST", **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> Response:
        return self.make_request(endpoint, method="PUT", **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> Response:
        return self.make_request(endpoint, method="PATCH", **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        return self.make_request(endpoint, method="DELETE", **kwargs)

    def head(self, endpoint: str, **kwargs: Any) -> Response:
        return self.make_request(endpoint, method="HEAD", **kwargs)

    def options(self, endpoint: str, **kwargs: Any) -> Response:
        return self.make_request(endpoint, method="OPTIONS", **kwargs)


# ----------------------------
# Pytest hooks
# ----------------------------

def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: mark test as smoke for success scenarios")


# ----------------------------
# Fixtures
# ----------------------------

@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load configuration from config.yml located in the same directory as this file.
    Supports environment variable expansion within string values.
    """
    # per requirement: use os.path.join to find config in same directory
    cfg_path_str = os.path.join(os.path.dirname(__file__), "config.yml")
    cfg_path = Path(cfg_path_str).resolve()

    try:
        raw = _load_yaml(cfg_path)
    except Exception as e:
        pytest.fail(f"Failed to load config.yml at {cfg_path}: {e}")

    expanded = _expand_env(raw)

    # Validate expected structure strictly as provided
    # Configuration Structure:
    # api:
    #   host: "${AUTH_API_API_HOST:-}"
    # test_data: {}
    if "api" not in expanded or not isinstance(expanded["api"], dict):
        pytest.fail("Invalid config.yml: missing 'api' mapping.")
    if "host" not in expanded["api"]:
        pytest.fail("Invalid config.yml: missing 'api.host' key.")
    if "test_data" not in expanded:
        pytest.fail("Invalid config.yml: missing 'test_data' key.")

    return expanded


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    """
    Provides the API host string, stripped of whitespace and trailing slash.
    """
    host = (config["api"]["host"] or "").strip().rstrip("/")
    if host == "":
        pytest.fail("Config 'api.host' is empty. Ensure AUTH_API_API_HOST is set or default is provided.")
    return host


@pytest.fixture(scope="session")
def api_client(api_host: str) -> ApiClient:
    """
    Provides a configured ApiClient using the host from config.
    """
    client = ApiClient(base_url=api_host)
    return client


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Any:
    """
    Provides test_data loaded from the configuration.
    """
    return config.get("test_data", {})


@pytest.fixture(scope="session")
def load_test_data() -> Callable[[Union[Path, str]], Any]:
    """
    Provides a helper to load JSON test data from a given path.
    """
    return load_test_data_json
