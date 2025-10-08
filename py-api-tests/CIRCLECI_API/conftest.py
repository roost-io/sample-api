import os
import pytest
import requests
import yaml
from pathlib import Path


def load_config():
    """Load configuration from config.yml file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")


class ApiHelper:
    """Helper class for making HTTP requests."""
    
    def __init__(self, base_url):
        self.base_url = base_url.strip()
    
    def make_request(self, endpoint, params=None, headers=None, method='GET', data=None, json=None):
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        method = method.upper()
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, params=params, headers=headers, data=data, json=json)
        elif method == 'PUT':
            response = requests.put(url, params=params, headers=headers, data=data, json=json)
        elif method == 'DELETE':
            response = requests.delete(url, params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response


class ApiClient:
    """Simple API client for making requests."""
    
    def __init__(self, api_helper):
        self.api_helper = api_helper
    
    def get(self, endpoint, headers=None, params=None):
        """Make a GET request to the API."""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')
    
    def post(self, endpoint, headers=None, params=None, data=None, json=None):
        """Make a POST request to the API."""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='POST', data=data, json=json)
    
    def put(self, endpoint, headers=None, params=None, data=None, json=None):
        """Make a PUT request to the API."""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='PUT', data=data, json=json)
    
    def delete(self, endpoint, headers=None, params=None):
        """Make a DELETE request to the API."""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='DELETE')


@pytest.fixture(scope="session")
def config():
    """Fixture to provide configuration from config.yml."""
    return load_config()


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture to provide an API helper instance."""
    base_url = config.get('api', {}).get('host')
    if not base_url:
        raise ValueError("API host URL not found in configuration")
    return ApiHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture to provide an API client instance."""
    return ApiClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture to provide a valid API key from configuration."""
    api_key = config.get('authentication', {}).get('api_key_header')
    if not api_key:
        raise ValueError("API key not found in configuration")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture to provide an invalid API key for testing."""
    return "invalid_api_key_for_testing_purposes"


@pytest.fixture(scope="session")
def valid_location():
    """Fixture to provide a test location parameter."""
    return "San Francisco, CA"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture to provide an OAuth2 token from configuration."""
    token = config.get('authentication', {}).get('oauth2_token')
    if not token:
        pytest.skip("OAuth2 token not found in configuration")
    return token
