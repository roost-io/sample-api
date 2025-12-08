import os
import json
import re
from pathlib import Path

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


_ENV_VAR_PATTERN = re.compile(r"\$\{([^}:s]+):-([^}]+)\}")


def _expand_env_vars(value):
    def _expand_str(s: str) -> str:
        # Expand all ${VAR:-default} occurrences with environment or default
        def repl(match: re.Match) -> str:
            var_name = match.group(1)
            default_val = match.group(2)
            env_val = os.environ.get(var_name)
            if env_val is None or env_val == "":
                return default_val
            return env_val

        # Keep expanding until no further matches (handles nested expansions)
        prev = None
        current = s
        while prev != current and _ENV_VAR_PATTERN.search(current):
            prev = current
            current = _ENV_VAR_PATTERN.sub(repl, current)
        return current

    if isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env_vars(v) for v in value]
    if isinstance(value, str):
        return _expand_str(value)
    return value


def _load_yaml_config(file_path: Path) -> dict:
    if not file_path.exists():
        raise pytest.UsageError(f"config.yml not found at: {file_path}")
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise pytest.UsageError(f"Invalid YAML in config.yml: {e}") from e
    except Exception as e:
        raise pytest.UsageError(f"Could not read config.yml: {e}") from e
    return _expand_env_vars(data)


@pytest.fixture(scope="session")
def config():
    base_dir = Path(__file__).parent
    config_path = base_dir / "config.yml"
    return _load_yaml_config(config_path)


@pytest.fixture
def load_endpoint_test_data(request):
    def _loader(path):
        if isinstance(path, Path):
            candidate_paths = [path]
        else:
            path = str(path)
            candidate_paths = [
                Path(path),
                Path(request.fspath).parent.joinpath(path),
                Path(__file__).parent.joinpath(path),
                Path.cwd().joinpath(path),
            ]
        target = next((p for p in candidate_paths if p.exists() and p.is_file()), None)
        if target is None:
            raise pytest.UsageError(
                f"Endpoint test data JSON file not found. Tried: {', '.join(str(p) for p in candidate_paths)}"
            )
        try:
            with target.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise pytest.UsageError(f"Invalid JSON in {target}: {e}") from e
        except Exception as e:
            raise pytest.UsageError(f"Could not read JSON file {target}: {e}") from e

    return _loader


@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merge(path=None, data=None):
        base = config.get("test_data") or {}
        base = dict(base) if isinstance(base, dict) else {}
        endpoint_data = {}
        if path:
            endpoint_data = load_endpoint_test_data(path) or {}
        if data and isinstance(data, dict):
            # If both JSON and provided data have same keys, last one wins (data)
            endpoint_data.update(data)
        # Endpoint test data overrides config.yml test_data
        merged = dict(base)
        merged.update(endpoint_data)
        return merged

    return _merge


class APIClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist=None,
        default_headers=None,
    ):
        self.base_url = (base_url or "").strip().rstrip("/")
        if not self.base_url:
            raise pytest.UsageError("API base URL is empty. Check config['api']['host'].")
        self.timeout = timeout
        self.default_headers = default_headers or {}
        self.session = requests.Session()

        if status_forcelist is None:
            status_forcelist = [500, 502, 503, 504]

        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=backoff_factor,
            status_forcelist=tuple(status_forcelist),
            allowed_methods=frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        if not endpoint:
            return self.base_url
        if str(endpoint).startswith("http://") or str(endpoint).startswith("https://"):
            return str(endpoint)
        return f"{self.base_url}/{str(endpoint).lstrip('/')}"

    def make_request(self, endpoint, method="GET", headers=None, timeout=None, **kwargs):
        url = self._build_url(endpoint)
        req_headers = dict(self.default_headers)
        if headers:
            req_headers.update(headers)
        to = self.timeout if timeout is None else timeout
        response = self.session.request(method=method.upper(), url=url, headers=req_headers, timeout=to, **kwargs)
        return response

    def get(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="GET", **kwargs)

    def post(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="POST", **kwargs)

    def put(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="PUT", **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="PATCH", **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="DELETE", **kwargs)


@pytest.fixture
def api_client(config):
    api_cfg = config.get("api") or {}
    auth_cfg = config.get("auth") or {}

    host = str(api_cfg.get("host", "")).strip()
    timeout = api_cfg.get("timeout", 30.0)
    retries = api_cfg.get("retries", 3)
    backoff_factor = api_cfg.get("retry_backoff_factor", 0.3)
    status_forcelist = api_cfg.get("status_forcelist", [500, 502, 503, 504])

    default_headers = {}

    # Optional Authorization header if provided in config.auth.jwt_token (non-empty)
    jwt_token = auth_cfg.get("jwt_token")
    if isinstance(jwt_token, str) and jwt_token.strip():
        default_headers["Authorization"] = f"Bearer {jwt_token.strip()}"

    # Optional Cookie header if provided in config.auth.cookie_auth (non-empty)
    cookie_auth = auth_cfg.get("cookie_auth")
    if isinstance(cookie_auth, str) and cookie_auth.strip():
        # If a full cookie string is provided, set directly
        default_headers["Cookie"] = cookie_auth.strip()

    # Optional custom API key header if provided in config.auth.api_key_header and value
    # Example: auth: { api_key_header: "x-api-key", api_key: "foo" }
    api_key_header = auth_cfg.get("api_key_header")
    api_key_value = auth_cfg.get("api_key")
    if isinstance(api_key_header, str) and api_key_header.strip() and isinstance(api_key_value, str) and api_key_value.strip():
        default_headers[api_key_header.strip()] = api_key_value.strip()

    client = APIClient(
        base_url=host,
        timeout=timeout,
        retries=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        default_headers=default_headers,
    )
    return client


@pytest.fixture(scope="session")
def get_config(config):
    def _get(dotted_key: str, default=None):
        if not dotted_key:
            return default
        parts = str(dotted_key).split(".")
        cur = config
        for part in parts:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return cur

    return _get


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as part of the smoke test suite")
