import os
import yaml
import pytest
import requests
from pathlib import Path


class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=params, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=params, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        return response


class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope='session')
def config():
    """Load configuration from config.yml"""
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML configuration: {e}")


@pytest.fixture(scope='session')
def api_helper(config):
    """Provide an APIHelper instance configured with the base URL"""
    base_url = config['api']['host']
    if not base_url:
        raise ValueError("API host is not defined in the configuration")
    return APIHelper(base_url)


@pytest.fixture(scope='session')
def api_client(api_helper):
    """Provide an APIClient instance wrapping the APIHelper"""
    return APIClient(api_helper)


@pytest.fixture(scope='session')
def valid_api_key(config):
    """Extract and provide the valid API key from the configuration"""
    api_key = config['authentication'].get('api_key')
    if not api_key:
        raise ValueError("API key is missing in the configuration")
    return api_key


@pytest.fixture(scope='session')
def invalid_api_key():
    """Provide a dummy invalid API key for testing"""
    return "invalid_api_key_123456"


@pytest.fixture(scope='session')
def valid_location():
    """Provide a test location parameter"""
    return "New York"


@pytest.fixture(scope='session')
def oauth2_token(config):
    """Extract and provide an OAuth2 token from the configuration (if available)"""
    return config['authentication'].get('oauth2_token', None)
