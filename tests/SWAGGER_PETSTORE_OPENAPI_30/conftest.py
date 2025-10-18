import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any

class ApiHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.strip()}"
        response = requests.request(method, url, headers=headers, params=params)
        return response

class ApiClient:
    def __init__(self, api_helper: ApiHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_category(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema"""
        required_fields = []
        return all(field in category_data for field in required_fields)

    def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema"""
        required_fields = []
        return all(field in user_data for field in required_fields)

    def validate_schema_tag(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema"""
        required_fields = []
        return all(field in tag_data for field in required_fields)

    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema"""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        if 'category' in pet_data:
            category_validator = self.validate_schema_category
            if not category_validator(pet_data['category']):
                return False
        return True

    def validate_schema_api_response(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = []
        return all(field in api_response_data for field in required_fields)

@pytest.fixture(scope='session')
def config():
    config_path = Path(__file__).parent / 'config.yml'
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    for key, value in config_data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str) and sub_value.startswith('${') and sub_value.endswith('}'):
                    env_var = sub_value[2:-1]
                    config_data[key][sub_key] = os.getenv(env_var, '')
    return config_data

@pytest.fixture(scope='session')
def api_helper(config):
    base_url = config['api']['host'].strip()
    return ApiHelper(base_url)

@pytest.fixture(scope='session')
def api_client(api_helper):
    return ApiClient(api_helper)

@pytest.fixture(scope='session')
def valid_api_key(config):
    return config['authentication']['api_key']

@pytest.fixture(scope='session')
def invalid_api_key():
    return "INVALID_API_KEY"

@pytest.fixture(scope='session')
def valid_location():
    return "test_location"

@pytest.fixture(scope='session')
def oauth2_token(config):
    return config['authentication']['petstore_auth']
