import os
import re
import pytest
import requests
import yaml
from pathlib import Path
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def _expand_env_in_string(value):
    pattern = r'\${([^}:]+):-([^}]+)}'
    def replacer(match):
        env_var, default = match.groups()
        return os.getenv(env_var, default)
    return re.sub(pattern, replacer, value)

def load_config():
    config_path = Path(__file__).parent / 'config.yml'
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            return {key: _expand_env_in_string(value) if isinstance(value, str) else value
                    for key, value in config.items()}
    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing YAML file: {e}")

@pytest.fixture(scope='session')
def config():
    return load_config()

@pytest.fixture(scope='session')
def api_host(config):
    return config['api']['host'].strip()

@pytest.fixture(scope='session')
def api_auth(config):
    return {
        'api_key_header': config['auth']['api_key_header'],
        'api_key_query': config['auth']['api_key_query']
    }

@pytest.fixture(scope='session')
def config_test_data(config):
    return config['test_data']

class APIClient:
    def __init__(self, host, auth):
        self.host = host
        self.auth = auth
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def make_request(self, endpoint, method='GET', headers=None, **kwargs):
        url = f"{self.host}/{endpoint.lstrip('/')}"
        headers = headers or {}
        headers.update({'Authorization': f"Bearer {self.auth['api_key_header']}"})
        response = self.session.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def get(self, endpoint, **kwargs):
        return self.make_request(endpoint, 'GET', **kwargs)

    def post(self, endpoint, **kwargs):
        return self.make_request(endpoint, 'POST', **kwargs)

    def put(self, endpoint, **kwargs):
        return self.make_request(endpoint, 'PUT', **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.make_request(endpoint, 'DELETE', **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.make_request(endpoint, 'PATCH', **kwargs)

@pytest.fixture(scope='session')
def api_client(api_host, api_auth):
    return APIClient(api_host, api_auth)

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
