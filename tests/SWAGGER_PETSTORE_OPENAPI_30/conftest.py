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
    try:
        config_path = Path(__file__).parent / 'config.yml'
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            return {key: _expand_env_in_string(value) for key, value in config.items()}
    except FileNotFoundError:
        pytest.exit("config.yml file not found.")
    except yaml.YAMLError as exc:
        pytest.exit(f"Error in configuration file: {exc}")

@pytest.fixture(scope='session')
def config():
    return load_config()

@pytest.fixture(scope='session')
def api_host(config):
    return config['api']['host'].strip()

@pytest.fixture(scope='session')
def petstore_auth(config):
    return config['auth']['petstore_auth']

@pytest.fixture(scope='session')
def api_key(config):
    return config['auth']['api_key']

@pytest.fixture(scope='session')
def config_test_data(config):
    return config['test_data']

class APIClient:
    def __init__(self, host, petstore_auth, api_key):
        self.host = host
        self.petstore_auth = petstore_auth
        self.api_key = api_key
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        
    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.host}/{endpoint.lstrip('/')}"
        headers = headers or {}
        headers['Authorization'] = f"Bearer {self.petstore_auth}" if self.petstore_auth else headers.get('Authorization')
        headers['api_key'] = self.api_key if self.api_key else headers.get('api_key')
        
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
def api_client(api_host, petstore_auth, api_key):
    return APIClient(api_host, petstore_auth, api_key)

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as a smoke test.")
