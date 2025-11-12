import os
import re
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import requests
import yaml


def _substitute_env_values(obj: Any) -> Any:
    """
    Recursively replace ${VAR} placeholders in strings with environment variables.
    If an environment variable is missing, it is replaced with an empty string and a warning is emitted.
    """
    pattern = re.compile(r"\$\{([^}]+)\}")

    def replace_in_string(s: str) -> str:
        def repl(match: re.Match) -> str:
            var_name = match.group(1)
            value = os.environ.get(var_name)
            if value is None:
                warnings.warn(f"Environment variable '{var_name}' not set; substituting empty string.", RuntimeWarning)
                return ""
            return value
        return pattern.sub(repl, s)

    if isinstance(obj, dict):
        return {k: _substitute_env_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_env_values(v) for v in obj]
    elif isinstance(obj, str):
        return replace_in_string(obj)
    else:
        return obj


def _normalize_base_url(url: str) -> str:
    if not isinstance(url, str):
        return url
    # Strip whitespace and remove trailing slashes
    return url.strip().rstrip("/")


def _build_url(base_url: str, endpoint: str) -> str:
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint.strip()
    base = _normalize_base_url(base_url)
    ep = endpoint.strip()
    if not ep.startswith("/"):
        ep = "/" + ep
    return f"{base}{ep}"


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load configuration from config.yml located in the same directory as this file.
    Substitutes ${VAR} occurrences using environment variables.
    """
    base_dir = Path(__file__).resolve().parent
    config_path = Path(os.path.join(str(base_dir), "config.yml"))  # intentionally using os.path.join as requested

    if not config_path.exists():
        pytest.fail(f"Configuration file not found: {config_path}", pytrace=False)

    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        pytest.fail(f"Failed to parse YAML config at {config_path}: {e}", pytrace=False)
    except OSError as e:
        pytest.fail(f"Error reading config file at {config_path}: {e}", pytrace=False)

    substituted = _substitute_env_values(data)

    # Validate required fields
    api_cfg = substituted.get("api", {})
    host = api_cfg.get("host", "")
    host = _normalize_base_url(host) if isinstance(host, str) else host

    if not host:
        pytest.fail("API host is not configured. Ensure 'api.host' and corresponding environment variable are set.", pytrace=False)

    substituted.setdefault("api", {})["host"] = host

    # Optional: normalize known authentication fields if present
    auth_cfg = substituted.get("authentication", {}) or {}
    # No hard failure on missing key/token here; dedicated fixtures can handle missing values contextually
    substituted["authentication"] = auth_cfg

    return substituted


class APIHelper:
    def __init__(self, base_url: str, session: Optional[requests.Session] = None, default_timeout: int = 30):
        self.base_url = _normalize_base_url(base_url)
        self.session = session or requests.Session()
        self.default_timeout = default_timeout

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
    ) -> requests.Response:
        method_upper = method.upper().strip()
        url = _build_url(self.base_url, endpoint)
        base_headers = {
            "Accept": "application/json",
            "User-Agent": "pytest-api-helper/1.0",
        }
        if headers:
            base_headers.update(headers)

        request_kwargs: Dict[str, Any] = {
            "url": url,
            "headers": base_headers,
            "timeout": self.default_timeout,
        }

        if method_upper in {"GET", "DELETE", "HEAD"}:
            request_kwargs["params"] = params
        else:
            # Send body for mutating requests as JSON
            request_kwargs["json"] = params

        response = self.session.request(method=method_upper, **request_kwargs)
        return response


class APIClient:
    def __init__(self, base_url: str, session: Optional[requests.Session] = None, default_timeout: int = 30):
        self.helper = APIHelper(base_url=base_url, session=session, default_timeout=default_timeout)

    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        return self.helper.make_request(endpoint=endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_helper(config: Dict[str, Any]) -> APIHelper:
    base_url = config.get("api", {}).get("host", "")
    return APIHelper(base_url=base_url)


@pytest.fixture(scope="session")
def api_client(config: Dict[str, Any]) -> APIClient:
    base_url = config.get("api", {}).get("host", "")
    return APIClient(base_url=base_url)


@pytest.fixture(scope="session")
def valid_api_key(config: Dict[str, Any]) -> str:
    key = (config.get("authentication") or {}).get("ApiKeyAuth", "")
    if not key:
        # Fall back to env var name suggested by config example
        key = os.environ.get("key", "")
    if not key:
        warnings.warn("Valid API key not found in config or environment.", RuntimeWarning)
    return key


@pytest.fixture(scope="session")
def invalid_api_key() -> str:
    return "INVALID_API_KEY_1234567890"


@pytest.fixture(scope="session")
def valid_location(config: Dict[str, Any]) -> str:
    # Prefer config test location, then env, then default
    location = (
        (config.get("test") or {}).get("location")
        or os.environ.get("TEST_LOCATION")
        or "San Francisco, CA"
    )
    return str(location).strip()


@pytest.fixture(scope="session")
def oauth2_token(config: Dict[str, Any]) -> Optional[str]:
    auth_cfg = config.get("authentication") or {}
    token = (
        auth_cfg.get("OAuth2Token")
        or auth_cfg.get("oauth2_token")
        or auth_cfg.get("OAuth2")
        or os.environ.get("OAUTH2_TOKEN")
    )
    token = str(token).strip() if token is not None else None
    if token == "":
        token = None
    return token
