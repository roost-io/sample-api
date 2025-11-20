import os
import re
import pytest
import yaml
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _expand_env_in_string(value: str) -> str:
    """
    Expand environment variables in string with format ${VAR:-default}.
    
    Args:
        value: String that may contain environment variable references
        
    Returns:
        String with environment variables expanded
    """
    if not isinstance(value, str):
        return value
    
    # Pattern to match ${VAR:-default} or ${VAR}
    pattern = r'\$\{([^}:]+)(?::-([^}]*))?\}'
    
    def replace_env(match):
        var_name = match.group(1)
        default_value = match.group(2) if match.group(2) is not None else ''
        return os.environ.get(var_name, default_value)
    
    return re.sub(pattern, replace_env, value)


def _expand_env_variables(data: Any) -> Any:
    """
    Recursively expand environment variables in configuration data.
    
    Args:
        data: Configuration data (dict, list, or primitive)
        
    Returns:
        Configuration data with environment variables expanded
    """
    if isinstance(data, dict):
        return {key: _expand_env_variables(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_expand_env_variables(item) for item in data]
    elif isinstance(data, str):
        return _expand_env_in_string(data)
    else:
        return data


class APIClient:
    """Simple API client for making HTTP requests with retry logic."""
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.strip()
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        headers: Optional[Dict] = None, 
        method: str = 'GET',
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make an HTTP request.
        
        Args:
            endpoint: API endpoint (will be joined with base_url)
            params: Query parameters
            headers: Request headers
            method: HTTP method
            data: Request body data
            json: Request body as JSON
            
        Returns:
            Response object
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=headers,
            data=data,
            json=json,
            timeout=self.timeout
        )
        
        return response
    
    def get(
        self, 
        endpoint: str, 
        headers: Optional[Dict] = None, 
        params: Optional[Dict] = None
    ) -> requests.Response:
        """Make a GET request."""
        return self.make_request(endpoint, params=params, headers=headers, method='GET')
    
    def post(
        self, 
        endpoint: str, 
        headers: Optional[Dict] = None, 
        params: Optional[Dict] = None,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None
    ) -> requests.Response:
        """Make a POST request."""
        return self.make_request(
            endpoint, params=params, headers=headers, method='POST', data=data, json=json
        )
    
    def put(
        self, 
        endpoint: str, 
        headers: Optional[Dict] = None, 
        params: Optional[Dict] = None,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None
    ) -> requests.Response:
        """Make a PUT request."""
        return self.make_request(
            endpoint, params=params, headers=headers, method='PUT', data=data, json=json
        )
    
    def patch(
        self, 
        endpoint: str, 
        headers: Optional[Dict] = None, 
        params: Optional[Dict] = None,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None
    ) -> requests.Response:
        """Make a PATCH request."""
        return self.make_request(
            endpoint, params=params, headers=headers, method='PATCH', data=data, json=json
        )
    
    def delete(
        self, 
        endpoint: str, 
        headers: Optional[Dict] = None, 
        params: Optional[Dict] = None
    ) -> requests.Response:
        """Make a DELETE request."""
        return self.make_request(endpoint, params=params, headers=headers, method='DELETE')
    
    def head(
        self, 
        endpoint: str, 
        headers: Optional[Dict] = None, 
        params: Optional[Dict] = None
    ) -> requests.Response:
        """Make a HEAD request."""
        return self.make_request(endpoint, params=params, headers=headers, method='HEAD')
    
    def options(
        self, 
        endpoint: str, 
        headers: Optional[Dict] = None, 
        params: Optional[Dict] = None
    ) -> requests.Response:
        """Make an OPTIONS request."""
        return self.make_request(endpoint, params=params, headers=headers, method='OPTIONS')
    
    def close(self):
        """Close the session."""
        self.session.close()


@pytest.fixture(scope='session')
def config() -> Dict[str, Any]:
    """
    Load and parse configuration from config.yml file.
    
    Returns:
        Dictionary containing configuration data with environment variables expanded
    """
    config_file = Path(__file__).parent / 'config.yml'
    
    if not config_file.exists():
        pytest.fail(f"Configuration file not found: {config_file}")
    
    try:
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        if config_data is None:
            pytest.fail(f"Configuration file is empty: {config_file}")
        
        # Expand environment variables in the configuration
        config_data = _expand_env_variables(config_data)
        
        return config_data
    
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML configuration: {e}")
    except Exception as e:
        pytest.fail(f"Error loading configuration: {e}")


@pytest.fixture(scope='session')
def host(config: Dict[str, Any]) -> str:
    """
    Get API host from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        API host URL
    """
    try:
        return config['api']['host']
    except KeyError:
        pytest.fail("API host not found in configuration (api.host)")


@pytest.fixture(scope='session')
def auth(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get authentication configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Authentication configuration or None if not present
    """
    return config.get('api', {}).get('auth')


@pytest.fixture(scope='session')
def api_client(host: str) -> APIClient:
    """
    Create an API client instance.
    
    Args:
        host: API host URL
        
    Returns:
        Configured APIClient instance
    """
    client = APIClient(base_url=host)
    yield client
    client.close()


@pytest.fixture(scope='session')
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load test data from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Test data dictionary
    """
    return config.get('test_data', {})


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "smoke: Mark test as smoke test for success scenarios"
    )
