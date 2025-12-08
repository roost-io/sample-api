import pytest
import requests
import yaml
import json
import os
import re
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def _expand_env_vars(value):
    pattern = r"\${([^}:s]+):-([^}]+)}"
    def replacer(match):
        env_var, default = match.groups()
        return os.getenv(env_var, default)
    return re.sub(pattern, replacer, value)

def load_config():
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError("config.yml not found")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    def expand_dict(d):
        for k, v in d.items():
            if isinstance(v, dict):
                expand_dict(v)
            elif isinstance(v, str):
                d[k] = _expand_env_vars(v)
    
    expand_dict(config)
    return config

@pytest.fixture(scope='session')
def config():
    return load_config()

@pytest.fixture
def load_endpoint_test_data():
    def _load(path):
        with open(path, 'r') as file:
            return json.load(file)
    return _load

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merge(path):
        endpoint_data = load_endpoint_test_data(path)
        merged_data = config.get('test_data', {}).copy()
        merged_data.update(endpoint_data)
        return merged_data
    return _merge

class APIClient:
    def __init__(self, base_url, timeout=5, retries=3):
        self.base_url = base_url.strip()
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = timeout

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response

    def get(self, endpoint, **kwargs):
        return self.make_request(endpoint, "GET", **kwargs)

    def post(self, endpoint, **kwargs):
        return self.make_request(endpoint, "POST", **kwargs)

    def put(self, endpoint, **kwargs):
        return self.make_request(endpoint, "PUT", **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.make_request(endpoint, "PATCH", **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.make_request(endpoint, "DELETE", **kwargs)

@pytest.fixture
def api_client(config):
    base_url = config['api']['host']
    return APIClient(base_url)

@pytest.fixture
def get_config(config):
    def _get(key):
        keys = key.split('.')
        value = config
        for k in keys:
            value = value.get(k)
            if value is None:
                break
        return value
    return _get

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
