import pytest
import requests
import yaml
from pathlib import Path
import os

class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response

class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

@pytest.fixture(scope='session')
def config():
    config_path = Path(os.path.join(os.path.dirname(__file__), 'config.yml'))
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        pytest.fail(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML file: {e}")

@pytest.fixture(scope='session')
def api_helper(config):
    base_url = config['api']['host'].strip()
    return APIHelper(base_url)

@pytest.fixture(scope='session')
def api_client(api_helper):
    return APIClient(api_helper)

@pytest.fixture(scope='session')
def valid_api_key(config):
    return config['authentication'].get('valid_api_key', '')

@pytest.fixture(scope='session')
def invalid_api_key():
    return "invalid_api_key"

@pytest.fixture(scope='session')
def valid_location():
    return "Stockholm"

@pytest.fixture(scope='session')
def oauth2_token(config):
    return config['authentication'].get('oauth2_token', '')
