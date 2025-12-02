import os
import pytest
import requests
import yaml
from pathlib import Path
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def _expand_env_in_string(value):
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value

def load_config():
    config_path = Path(__file__).parent / 'config.yml'
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            return {k: {ik: _expand_env_in_string(iv) for ik, iv in v.items()} for k, v in config.items()}
    except FileNotFoundError:
        raise RuntimeError("config.yml file not found.")
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Error parsing config.yml: {exc}")

@pytest.fixture(scope='session')
def config():
    return load_config()

@pytest.fixture(scope='session')
def host(config):
    return config['api']['host'].strip()

@pytest.fixture(scope='session')
def auth(config):
    return config['auth']

@pytest.fixture(scope='session')
def config_test_data(config):
    return config['test_data']

class APIClient:
    def __init__(self, host, auth):
        self.host = host
        self.auth = auth
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.host}{endpoint}"
        headers = headers or {}
        headers.update({'Authorization': f"Bearer {self.auth['petstore_auth']}"})
        response = self.session.request(method, url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response

    def get(self, endpoint, headers=None, params=None):
        return self.make_request(endpoint, params=params, headers=headers, method='GET')

    def post(self, endpoint, data=None, headers=None):
        return self.make_request(endpoint, params=data, headers=headers, method='POST')

    def put(self, endpoint, data=None, headers=None):
        return self.make_request(endpoint, params=data, headers=headers, method='PUT')

    def delete(self, endpoint, headers=None):
        return self.make_request(endpoint, headers=headers, method='DELETE')

    def patch(self, endpoint, data=None, headers=None):
        return self.make_request(endpoint, params=data, headers=headers, method='PATCH')

@pytest.fixture(scope='session')
def api_client(host, auth):
    return APIClient(host, auth)

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
