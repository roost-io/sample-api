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
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.helper = APIHelper(base_url)
    
    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, params=params, headers=headers, method='GET')

@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    def replace_env_vars(data):
        if isinstance(data, dict):
            return {key: replace_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [replace_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith('${') and data.endswith('}'):
            env_var = data[2:-1]
            return os.getenv(env_var, data)
        else:
            return data
    
    return replace_env_vars(config_data)

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config['api']['host']
    return APIHelper(base_url)

@pytest.fixture(scope="session")
def api_client(config):
    base_url = config['api']['host']
    return APIClient(base_url)

@pytest.fixture(scope="session")
def valid_api_key(config):
    return config.get('authentication', {}).get('api_key')

@pytest.fixture
def invalid_api_key():
    return "invalid_api_key_12345"

@pytest.fixture
def valid_location():
    return "New York"

@pytest.fixture(scope="session")
def oauth2_token(config):
    return config.get('authentication', {}).get('oauth2_token')
