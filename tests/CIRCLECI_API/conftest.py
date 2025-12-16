import os
import json
import re
from pathlib import Path
from typing import Any, Dict, Callable, Optional, Union

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Regex for environment variable expansion with default values: ${VAR:-default}
ENV_PATTERN = re.compile(r"\$\{([^}:\s]+):-([^}]+)\}")


def _expand_env_string(value: str) -> str:
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        default_val = match.group(2)
        env_val = os.environ.get(var_name, None)
        # Use default if env var is missing or empty
        if env_val is None or env_val == "":
            return default_val
        return env_val

    prev = None
    current = value
    # Re-run until no further substitutions are found (handles nested or repeated patterns)
    while prev != current:
        prev = current
        current = ENV_PATTERN.sub(replacer, current)
    return current


def _expand_env_vars(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _expand_env_vars(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_expand_env_vars(v) for v in data]
    if isinstance(data, str):
        return _expand_env_string(data)
    return data


def _deep_merge(base: Any, override: Any) -> Any:
    # If both are dicts, merge recursively; otherwise, override takes precedence.
    if isinstance(base, dict) and isinstance(override, dict):
        result = dict(base)
        for k, v in override.items():
            if k in result:
                result[k] = _deep_merge(result[k], v)
            else:
                result[k] = v
        return result
    return override


def _load_config_yaml() -> Dict[str, Any]:
    cfg_path = Path(__file__).resolve().parent / "config.yml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing required configuration file: {cfg_path}")
    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {cfg_path}: {e}") from e
    if not isinstance(raw, dict):
        raise TypeError(f"Top-level content of {cfg_path} must be a mapping (YAML dict)")
    return _expand_env_vars(raw)


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    try:
        return _load_config_yaml()
    except (FileNotFoundError, ValueError, TypeError) as e:
        raise pytest.UsageError(str(e))


@pytest.fixture
def load_endpoint_test_data(request) -> Callable[[Optional[Union[str, Path]]], Dict[str, Any]]:
    def _loader(path: Optional[Union[str, Path]]) -> Dict[str, Any]:
        if not path:
            return {}
        p = Path(path)
        candidate_paths = []
        if p.is_absolute():
            candidate_paths = [p]
        else:
            # Try multiple sensible roots for convenience
            candidate_paths = [
                Path.cwd() / p,
                Path(str(getattr(request, "fspath", Path.cwd())))  # type: ignore[arg-type]
                .parent.joinpath(p),
                Path(getattr(request.config, "rootpath", Path.cwd())).joinpath(p),
                Path(__file__).resolve().parent.joinpath(p),
            ]
        for cand in candidate_paths:
            if cand.exists() and cand.is_file():
                try:
                    with cand.open("r", encoding="utf-8") as fh:
                        data = json.load(fh)
                except json.JSONDecodeError as je:
                    raise pytest.UsageError(f"Invalid JSON in test data file '{cand}': {je}") from je
                if data is None:
                    return {}
                if not isinstance(data, dict):
                    raise pytest.UsageError(f"Endpoint test data in '{cand}' must be a JSON object")
                return data
        raise pytest.UsageError(f"Endpoint test data file not found: '{path}'")
    return _loader


@pytest.fixture
def merged_test_data(config, load_endpoint_test_data) -> Callable[[Optional[Union[str, Path]]], Dict[str, Any]]:
    def _merger(path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        base = config.get("test_data", {})
        if base is None:
            base = {}
        if not isinstance(base, dict):
            raise pytest.UsageError("config.yml 'test_data' must be a mapping (dict)")
        endpoint_data = load_endpoint_test_data(path) if path else {}
        if not isinstance(endpoint_data, dict):
            raise pytest.UsageError("Endpoint test data must be a mapping (dict)")
        # Values from endpoint_data override config.yml values
        return _deep_merge(base, endpoint_data)
    return _merger


class APIClient:
    def __init__(self, base_url: str, default_headers: Optional[Dict[str, str]] = None,
                 timeout: Optional[Union[int, float]] = None,
                 retries: int = 3, backoff_factor: float = 0.5,
                 status_forcelist: Optional[list] = None):
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("API base_url must be a non-empty string")
        self.base_url = base_url.strip().rstrip("/")
        self.default_headers = dict(default_headers or {})
        self.timeout = timeout if timeout is not None else 30
        self.session = requests.Session()
        status_forcelist = status_forcelist or [429, 500, 502, 503, 504]
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=frozenset(["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def make_request(self, endpoint: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        url = self._build_url(endpoint)
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)
        timeout = kwargs.pop("timeout", self.timeout)
        return self.session.request(method=method.upper(), url=url, headers=merged_headers, timeout=timeout, **kwargs)

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="GET", **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="POST", **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="PUT", **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="PATCH", **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.make_request(endpoint, method="DELETE", **kwargs)


def _build_default_headers_from_config(cfg: Dict[str, Any]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    auth_cfg = cfg.get("auth", {})
    if isinstance(auth_cfg, dict):
        # Support header defined by auth.api_key_header with a value from common key names
        header_name = auth_cfg.get("api_key_header")
        if isinstance(header_name, str) and header_name.strip():
            value = None
            for k in ("api_key", "api_key_value", "value", "token"):
                if k in auth_cfg and auth_cfg.get(k) not in (None, ""):
                    value = str(auth_cfg.get(k))
                    break
            if value is not None:
                headers[header_name] = value
        # If explicit headers dict is provided under auth.headers, include them as-is
        explicit_headers = auth_cfg.get("headers")
        if isinstance(explicit_headers, dict):
            headers.update({str(k): str(v) for k, v in explicit_headers.items()})
    return headers


@pytest.fixture(scope="session")
def api_client(config) -> APIClient:
    try:
        api_cfg = config.get("api", {})
        if not isinstance(api_cfg, dict):
            raise pytest.UsageError("config.yml 'api' must be a mapping (dict)")

        host = api_cfg.get("host")
        if not isinstance(host, str) or not host.strip():
            raise pytest.UsageError("config.yml must include 'api.host' as a non-empty string")

        timeout = api_cfg.get("timeout", None)
        retries = api_cfg.get("retries", 3)
        backoff_factor = api_cfg.get("backoff_factor", 0.5)
        status_forcelist = api_cfg.get("status_forcelist", [429, 500, 502, 503, 504])

        headers = _build_default_headers_from_config(config)
        return APIClient(
            base_url=host.strip(),
            default_headers=headers,
            timeout=timeout,
            retries=int(retries) if isinstance(retries, int) else 3,
            backoff_factor=float(backoff_factor) if isinstance(backoff_factor, (int, float)) else 0.5,
            status_forcelist=list(status_forcelist) if isinstance(status_forcelist, (list, tuple)) else [429, 500, 502, 503, 504],
        )
    except Exception as e:
        if isinstance(e, pytest.UsageError):
            raise
        raise pytest.UsageError(f"Failed to initialize API client: {e}") from e


@pytest.fixture
def get_config(config) -> Callable[[str, Any], Any]:
    def _getter(dotted_key: str, default: Any = None) -> Any:
        if dotted_key is None or dotted_key == "":
            return config
        current: Any = config
        for part in dotted_key.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    if default is not None:
                        return default
                    raise KeyError(f"Index out of range for key '{dotted_key}'")
            else:
                if default is not None:
                    return default
                raise KeyError(f"Key '{dotted_key}' not found at component '{part}'")
        return current
    return _getter


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: mark a test as a smoke test")
