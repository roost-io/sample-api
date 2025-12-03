import os
import pytest
import requests
import yaml
from pathlib import Path
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def _expand_env_in_string(value):
    if isinstance(value, str) and value.startswith("${") and ":-" in value:
        var_name, default_value = value[2:-1].split(":-")
        return os.getenv(var_name, default_value)
    return value

def load_config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            for section in config:
                for key, value in config[section].items():
                    config[section][key] = _expand_env_in_string(value)
            return config
    except FileNotFoundError:
        pytest.exit("Configuration file 'config.yml' not found.", returncode=1)
    except yaml.YAMLError as e:
        pytest.exit(f"Error parsing configuration file: {e}", returncode=1)

@pytest.fixture(scope="session")
def config():
    return load_config()

class APIClient:
    def __init__(self, base_url, auth_token=None, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        if auth_token:
            self.session.headers.update({"Authorization": f"Bearer {auth_token}"})
        if api_key:
            self.session.headers.update({"api_key": api_key})

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method=method, url=url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def get(self, endpoint, headers=None, params=None):
        return self.make_request(endpoint, params=params, headers=headers, method='GET')

    def post(self, endpoint, data=None, headers=None):
        return self.make_request(endpoint, headers=headers, method='POST', params=data)

    def put(self, endpoint, data=None, headers=None):
        return self.make_request(endpoint, headers=headers, method='PUT', params=data)

    def delete(self, endpoint, headers=None):
        return self.make_request(endpoint, headers=headers, method='DELETE')

    def patch(self, endpoint, data=None, headers=None):
        return self.make_request(endpoint, headers=headers, method='PATCH', params=data)

@pytest.fixture(scope="session")
def api_client(config):
    api_config = config['api']
    auth_config = config['auth']
    return APIClient(base_url=api_config['host'], auth_token=auth_config.get('petstore_auth'), api_key=auth_config.get('api_key'))

@pytest.fixture(scope="session")
def config_test_data(config):
    return config['test_data']

@pytest.fixture(scope="session")
def api_host(config):
    return config['api']['host']

@pytest.fixture(scope="session")
def petstore_auth(config):
    return config['auth']['petstore_auth']

@pytest.fixture(scope="session")
def api_key(config):
    return config['auth']['api_key']

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test for basic success scenarios")
