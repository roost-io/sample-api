import pytest
import requests
import yaml
import os
import re
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def _expand_env_in_string(value):
    pattern = r'\${([^}:]+):-([^}]+)}'
    matches = re.findall(pattern, value)
    for var, default in matches:
        value = value.replace(f'${{{var}:-{default}}}', os.getenv(var, default))
    return value

def load_config():
    config_path = Path(__file__).parent / 'config.yml'
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            # Expand environment variables in the config
            for section in config:
                for key, value in config[section].items():
                    config[section][key] = _expand_env_in_string(value)
            return config
    except FileNotFoundError:
        raise Exception("Config file not found")
    except yaml.YAMLError as e:
        raise Exception(f"Error parsing config file: {e}")

class APIClient:
    def __init__(self, base_url, auth_token=None, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
        if api_key:
            self.session.headers.update({'api_key': api_key})
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def make_request(self, endpoint, method='GET', headers=None, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, headers=headers, timeout=10, **kwargs)
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
def config():
    return load_config()

@pytest.fixture(scope='session')
def api_client(config):
    api_config = config['api']
    auth_config = config['auth']
    return APIClient(base_url=api_config['host'], auth_token=auth_config['petstore_auth'], api_key=auth_config['api_key'])

@pytest.fixture(scope='session')
def config_test_data(config):
    return config['test_data']

@pytest.fixture(scope='session')
def host(config):
    return config['api']['host']

@pytest.fixture(scope='session')
def auth(config):
    return config['auth']['petstore_auth']

@pytest.fixture(scope='session')
def api_key(config):
    return config['auth']['api_key']

@pytest.mark.smoke
def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
