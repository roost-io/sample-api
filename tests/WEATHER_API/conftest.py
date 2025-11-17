import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import requests
import yaml


def _load_yaml_with_env_substitution(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    try:
        text = config_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise IOError(f"Failed to read config file: {config_path}") from exc

    # Replace ${VAR} with environment variable value if present; otherwise leave as-is
    pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

    def _repl(match: re.Match) -> str:
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))

    substituted = pattern.sub(_repl, text)

    try:
        data = yaml.safe_load(substituted) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in config file: {config_path}") from exc

    if not isinstance(data, dict):
        raise ValueError("Top-level YAML structure must be a mapping (dict)")

    return data


def _normalize_base_url(raw_host: Optional[str]) -> str:
    host = (raw_host or "").strip()
    if not host:
        return host

    # Ensure scheme; default to https if not provided
    if not re.match(r"^https?://", host, re.IGNORECASE):
        host = f"https://{host}"

    # Remove trailing slash for consistent joining
    host = host.rstrip("/")
    return host


class ApiHelper:
    def __init__(self, base_url: str, default_headers: Optional[Dict[str, str]] = None, timeout: int = 30):
        self.base_url = _normalize_base_url(base_url)
        self.default_headers = default_headers or {"Accept": "application/json"}
        self.timeout = timeout

    def _build_url(self, endpoint: str) -> str:
        endpoint = (endpoint or "").strip()
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        json: Any = None,
        data: Any = None,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        response = requests.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=merged_headers,
            timeout=self.timeout,
            json=json,
            data=data,
        )
        return response


class ApiClient:
    def __init__(self, helper: ApiHelper):
        self.helper = helper

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None):
        return self.helper.make_request(endpoint=endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    base_dir = Path(__file__).resolve().parent
    # Per requirement, use os.path.join to find config file in the same directory
    config_path_str = os.path.join(str(base_dir), "config.yml")
    config_path = Path(config_path_str)
    return _load_yaml_with_env_substitution(config_path)


@pytest.fixture(scope="session")
def api_helper(config: Dict[str, Any]) -> ApiHelper:
    api_cfg = config.get("api", {}) if isinstance(config, dict) else {}
    base_url = _normalize_base_url(api_cfg.get("host", ""))
    return ApiHelper(base_url=base_url)


@pytest.fixture
def api_client(api_helper: ApiHelper) -> ApiClient:
    return ApiClient(helper=api_helper)


@pytest.fixture
def valid_api_key(config: Dict[str, Any]) -> Optional[str]:
    api_cfg = config.get("api", {}) if isinstance(config, dict) else {}
    # Try common key names
    for key_name in ("api_key", "key", "apikey", "token"):
        if key_name in api_cfg and isinstance(api_cfg[key_name], str) and api_cfg[key_name].strip():
            return api_cfg[key_name].strip()
    return None


@pytest.fixture
def invalid_api_key() -> str:
    # A deterministic dummy invalid key for testing
    return "invalid_api_key_for_testing_purposes"


@pytest.fixture
def valid_location(config: Dict[str, Any]) -> str:
    api_cfg = config.get("api", {}) if isinstance(config, dict) else {}
    location = api_cfg.get("location") or os.environ.get("TEST_LOCATION") or "New York"
    return str(location).strip()


@pytest.fixture
def oauth2_token(config: Dict[str, Any]) -> Optional[str]:
    api_cfg = config.get("api", {}) if isinstance(config, dict) else {}
    for key_name in ("oauth2_token", "oauth_token", "access_token"):
        val = api_cfg.get(key_name)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None
