import os
import re
import requests
import yaml
import pytest
from pathlib import Path

def _expand_env_in_string(s):
    pattern = r'\${([^}:s]+):-([^}]+)}'
    def replacer(match):
        env_var, default = match.groups()
        return os.getenv(env_var, default)
    return re.sub(pattern, replacer, s)

@pytest.fixture(scope='session')
def config():
    config_path = Path(__file__).parent / 'config.yml'
    try:
        with open(config_path, 'r') as file:
            raw_config = yaml.safe_load(file)
        expanded_config = {
            key: {sub_key: _expand_env_in_string(value) for sub_key, value in sub_dict.items()}
            for key, sub_dict in raw_config.items()
        }
        return expanded_config
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration from {config_path}: {e}")

@pytest.fixture(scope='session')
def api_client(config):
    class APIClient:
        def __init__(self, base_url, auth, api_key):
            self.base_url = base_url.rstrip('/')
            self.auth = auth
            self.api_key = api_key
            self.session = requests.Session()

        def make_request(self, endpoint, params=None, headers=None, method='GET'):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = headers or {}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                raise RuntimeError(f"API request failed: {e}")

        def get(self, endpoint, headers=None, params=None):
            return self.make_request(endpoint, params=params, headers=headers, method='GET')

        def post(self, endpoint, headers=None, data=None, json=None):
            return self.make_request(endpoint, headers=headers, method='POST', params=data, json=json)

        def put(self, endpoint, headers=None, data=None):
            return self.make_request(endpoint, headers=headers, method='PUT', params=data)

        def delete(self, endpoint, headers=None):
            return self.make_request(endpoint, headers=headers, method='DELETE')

        def patch(self, endpoint, headers=None, data=None):
            return self.make_request(endpoint, headers=headers, method='PATCH', params=data)

    api_config = config['api']
    auth_config = config['auth']
    return APIClient(api_config['host'], auth_config['petstore_auth'], auth_config['api_key'])

@pytest.fixture(scope='session')
def config_test_data(config):
    return config['test_data']

@pytest.fixture(scope='session')
def host(config):
    return config['api']['host']

@pytest.fixture(scope='session')
def auth(config):
    return config['auth']

@pytest.mark.smoke
def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test for success scenarios")
