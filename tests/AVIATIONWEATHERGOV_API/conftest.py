import os
import re
from pathlib import Path
import yaml
import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Pattern to replace ${VAR} and ${VAR:-default} in strings
_ENV_PATTERN = re.compile(r'\$\{([^}]+)\}')

def _expand_env_in_string(s: str) -> str:
    def _replace(match):
        inner = match.group(1)
        if ':-' in inner:
            var, default = inner.split(':-', 1)
            return os.environ.get(var, default)
        else:
            return os.environ.get(inner, '')
    if not isinstance(s, str):
        return s
    previous = s
    while True:
        expanded = _ENV_PATTERN.sub(_replace, previous)
        if expanded == previous:
            break
        previous = expanded
    return previous

def _load_config_yaml() -> dict:
    # Locate config.yml in the same directory as this file
    base_dir = Path(__file__).resolve().parent
    config_path = os.path.join(str(base_dir), 'config.yml')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.yml not found at expected location: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}
    except Exception as exc:
        raise RuntimeError(f"Error reading config.yml: {exc}")

    def _expand(obj):
        if isinstance(obj, dict):
            return {k: _expand(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_expand(v) for v in obj]
        if isinstance(obj, str):
            return _expand_env_in_string(obj)
        return obj

    try:
        return _expand(cfg)
    except Exception as exc:
        raise RuntimeError(f"Error expanding environment variables in config.yml: {exc}")

class APIClient:
    def __init__(self, config: dict, timeout: int = None, max_retries: int = None, backoff_factor: float = None):
        self.config = config or {}
        api_cfg = (self.config.get('api') or {}) if isinstance(self.config.get('api'), dict) else {}

        host = (api_cfg.get('host') or '').strip()
        if host.endswith('/'):
            host = host[:-1]
        self.host = host

        # Authentication headers (from config if provided)
        self.auth_headers = self._parse_auth_from_config(api_cfg.get('auth'))

        # Timeout and retry configuration
        self.timeout = int(timeout) if timeout is not None else int(api_cfg.get('timeout', 10))
        retries = int(max_retries) if max_retries is not None else int(api_cfg.get('max_retries', 3))
        backoff = float(backoff_factor) if backoff_factor is not None else float(api_cfg.get('backoff_factor', 0.3))

        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _full_url(self, endpoint: str) -> str:
        if not self.host:
            return endpoint
        return self.host.rstrip('/') + '/' + endpoint.lstrip('/')

    def _merge_headers(self, headers: dict = None) -> dict:
        merged = dict(self.default_headers)
        if self.auth_headers:
            merged.update(self.auth_headers)
        if headers:
            merged.update(headers)
        return merged

    def _parse_auth_from_config(self, auth_cfg):
        if not auth_cfg:
            return {}
        if isinstance(auth_cfg, dict):
            if 'Authorization' in auth_cfg:
                return {'Authorization': auth_cfg['Authorization']}
            if 'token' in auth_cfg:
                return {'Authorization': f"Bearer {auth_cfg['token']}"}
            if 'headers' in auth_cfg and isinstance(auth_cfg['headers'], dict):
                return dict(auth_cfg['headers'])
        return {}

    def make_request(self, endpoint: str, params: dict = None, headers: dict = None, method: str = 'GET', json=None, data=None, **kwargs):
        method = (method or 'GET').upper()
        url = self._full_url(endpoint)
        response = self.session.request(
            method,
            url,
            params=params,
            headers=self._merge_headers(headers),
            timeout=self.timeout,
            json=json,
            data=data,
            **kwargs
        )
        response.raise_for_status()
        return response

    def get(self, endpoint: str, headers: dict = None, params: dict = None):
        return self.make_request(endpoint, params=params, headers=headers, method='GET')

    def post(self, endpoint: str, headers: dict = None, params: dict = None, json=None, data=None):
        return self.make_request(endpoint, params=params, headers=headers, method='POST', json=json, data=data)

    def put(self, endpoint: str, headers: dict = None, params: dict = None, json=None, data=None):
        return self.make_request(endpoint, params=params, headers=headers, method='PUT', json=json, data=data)

    def delete(self, endpoint: str, headers: dict = None, params: dict = None):
        return self.make_request(endpoint, params=params, headers=headers, method='DELETE')

    def patch(self, endpoint: str, headers: dict = None, params: dict = None, json=None, data=None):
        return self.make_request(endpoint, params=params, headers=headers, method='PATCH', json=json, data=data)

@pytest.fixture(scope='session')
def config():
    # Load configuration once per test session
    return _load_config_yaml()

@pytest.fixture(scope='session')
def host(config):
    api_cfg = (config.get('api') or {}) if isinstance(config.get('api'), dict) else {}
    return str((api_cfg.get('host') or '').strip())

@pytest.fixture(scope='session')
def auth(config):
    api_cfg = (config.get('api') or {}) if isinstance(config.get('api'), dict) else {}
    return api_cfg.get('auth')

@pytest.fixture(scope='session')
def config_test_data(config):
    return config.get('test_data', {})

@pytest.fixture
def api_client(config, request) -> APIClient:
    # Instantiate API client with config-based settings
    api_cfg = (config.get('api') or {}) if isinstance(config.get('api'), dict) else {}
    timeout = api_cfg.get('timeout')
    max_retries = api_cfg.get('max_retries')
    backoff = api_cfg.get('backoff_factor')
    client = APIClient(config, timeout=timeout, max_retries=max_retries, backoff_factor=backoff)
    return client

def pytest_configure(config_pytest):
    config_pytest.addinivalue_line("markers", "smoke: mark test as smoke test")
