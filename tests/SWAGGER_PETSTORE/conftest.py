import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any

# Load configuration from YAML file
@pytest.fixture(scope='session')
def config():
    config_path = Path(__file__).parent / 'config.yml'
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    def replace_env_vars(value):
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, '')
        return value

    for section in config_data:
        for key, value in config_data[section].items():
            config_data[section][key] = replace_env_vars(value)
    
    return config_data

# API Helper class
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip()

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, params=params, headers=headers)
        return response

# API Client fixture
@pytest.fixture(scope='session')
def api_client(config):
    base_url = config['api']['host']
    return APIHelper(base_url)

# Valid API Key fixture
@pytest.fixture(scope='session')
def valid_api_key(config):
    return config['authentication']['api_key']

# Invalid API Key fixture
@pytest.fixture(scope='session')
def invalid_api_key():
    return "INVALID_API_KEY"

# Valid Location fixture
@pytest.fixture(scope='session')
def valid_location():
    return "test_location"

# OAuth2 Token fixture
@pytest.fixture(scope='session')
def oauth2_token(config):
    return config['authentication']['petstore_auth']

# Schema Validator class
class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    # Add more schema validation methods here as needed

# Example usage of SchemaValidator
@pytest.fixture(scope='session')
def schema_validator():
    return SchemaValidator()
