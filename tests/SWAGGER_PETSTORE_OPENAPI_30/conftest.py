import os
import re
import requests
import pytest
import yaml
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Helper function to expand environment variables in strings
def _expand_env_in_string(string):
    pattern = r'\${([^}:]+):-([^}]+)}'
    def replacer(match):
        env_var, default_value = match.groups()
        return os.getenv(env_var, default_value)
    return re.sub(pattern, replacer, string)

# Load configuration from config.yml
def load_config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        # Expand environment variables in all config strings
        for key in config:
            for sub_key in config[key]:
                config[key][sub_key] = _expand_env_in_string(config[key][sub_key])
        return config
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")

# API Client class
class APIClient:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = self.config['api']['host'].strip() + endpoint
        response = self.session.request(method, url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response

    def get(self, endpoint, headers=None, params=None):
        return self.make_request(endpoint, headers=headers, params=params, method='GET')

    def post(self, endpoint, headers=None, params=None, data=None):
        return self.make_request(endpoint, headers=headers, params=params, method='POST', data=data)

    def put(self, endpoint, headers=None, params=None, data=None):
        return self.make_request(endpoint, headers=headers, params=params, method='PUT', data=data)

    def delete(self, endpoint, headers=None, params=None):
        return self.make_request(endpoint, headers=headers, params=params, method='DELETE')

    def patch(self, endpoint, headers=None, params=None, data=None):
        return self.make_request(endpoint, headers=headers, params=params, method='PATCH', data=data)

@pytest.fixture(scope='session')
def config():
    return load_config()

@pytest.fixture(scope='session')
def api_client(config):
    return APIClient(config)

@pytest.fixture(scope='session')
def config_test_data(config):
    return config['test_data']

@pytest.fixture(scope='session')
def host(config):
    return config['api']['host']

@pytest.fixture(scope='session')
def petstore_auth(config):
    return config['auth']['petstore_auth']

@pytest.fixture(scope='session')
def api_key(config):
    return config['auth']['api_key']

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test to run on production environments")
