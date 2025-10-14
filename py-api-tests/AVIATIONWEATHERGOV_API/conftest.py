import pytest
import requests
import yaml
import os
from pathlib import Path

class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
    
    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
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
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed: {str(e)}")

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.helper = APIHelper(base_url)
    
    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, params=params, headers=headers, method='GET')

@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    
    if not config_path.exists():
        pytest.fail(f"Config file not found at: {config_path}")
    
    try:
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        
        if not config_data:
            pytest.fail("Config file is empty or invalid")
        
        return config_data
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML config: {str(e)}")
    except Exception as e:
        pytest.fail(f"Error loading config: {str(e)}")

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get('api', {}).get('host', '').strip()
    if not base_url:
        pytest.fail("API host not found in config")
    
    return APIHelper(base_url)

@pytest.fixture(scope="session")
def api_client(config):
    base_url = config.get('api', {}).get('host', '').strip()
    if not base_url:
        pytest.fail("API host not found in config")
    
    return APIClient(base_url)

@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get('authentication', {}).get('api_key')
    if not api_key:
        pytest.fail("Valid API key not found in config")
    
    return api_key

@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_12345"

@pytest.fixture(scope="session")
def valid_location():
    return "New York"

@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get('authentication', {}).get('oauth2_token')
    if not token:
        pytest.fail("OAuth2 token not found in config")
    
    return token
