import pytest
import requests
import yaml
import os
import re
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

#  Define a custom YAML loader with environment variable expansion
pattern = re.compile(r'.*?\${(\w+)}.*?')

class EnvVarLoader(yaml.SafeLoader):
    pass

def envvar_constructor(loader, node):
    value = loader.construct_scalar(node)
    match = pattern.findall(value)
    if match:
        for var in match:
            env_value = os.getenv(var, '')
            value = value.replace(f"${{{var}}}", env_value)
    return value

EnvVarLoader.add_implicit_resolver('!envvar', pattern, None)
EnvVarLoader.add_constructor('!envvar', envvar_constructor)

@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    with open(config_path, 'r') as file:
        try:
            config_data = yaml.load(file, Loader=EnvVarLoader)
            return config_data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML config file: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get('api', {}).get('host', '').strip()
    if not base_url:
        raise ValueError("API host not found in configuration")
    
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(config):
    base_url = config.get('api', {}).get('host', '').strip()
    if not base_url:
        raise ValueError("API host not found in configuration")
    
    return APIClient(base_url)


@pytest.fixture(scope="session")
def valid_api_key(config):
    auth_config = config.get('authentication', {})
    api_key = auth_config.get('api_key')
    
    if not api_key:
        raise ValueError("Valid API key not found in configuration")
    
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_12345"


@pytest.fixture(scope="session")
def valid_location():
    return "New York"


@pytest.fixture(scope="session")
def oauth2_token(config):
    auth_config = config.get('authentication', {})
    token = auth_config.get('oauth2_token')
    
    if not token:
        raise ValueError("OAuth2 token not found in configuration")
    
    return token
