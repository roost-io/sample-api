import os
import re
import pytest
import yaml
import requests
from pathlib import Path
from typing import Any, Dict, Optional


def _expand_env_in_string(value: str) -> str:
    """
    Expand environment variables in string with format ${VAR:-default}
    
    Args:
        value: String potentially containing ${VAR:-default} patterns
        
    Returns:
        String with environment variables expanded
    """
    if not isinstance(value, str):
        return value
    
    pattern = r'\$\{([^}:]+)(?::-(.*?))?\}'
    
    def replace_env(match):
        env_var = match.group(1)
        default_value = match.group(2) if match.group(2) is not None else ""
        return os.environ.get(env_var, default_value)
    
    return re.sub(pattern, replace_env, value)


def _expand_env_vars(data: Any) -> Any:
    """
    Recursively expand environment variables in nested dictionary/list structures
    
    Args:
        data: Dictionary, list, or primitive value
        
    Returns:
        Data structure with all environment variables expanded
    """
    if isinstance(data, dict):
        return {key: _expand_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_expand_env_vars(item) for item in data]
    elif isinstance(data, str):
        return _expand_env_in_string(data)
    else:
        return data


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load configuration from config.yml file in the same directory as conftest.py
    and expand environment variables
    
    Returns:
        Dictionary containing configuration data
    """
    config_dir = Path(__file__).parent
    config_path = os.path.join(config_dir, "config.yml")
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        if config_data is None:
            config_data = {}
        
        # Expand environment variables
        expanded_config = _expand_env_vars(config_data)
        
        return expanded_config
    
    except FileNotFoundError:
        pytest.fail(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML configuration: {e}")
    except Exception as e:
        pytest.fail(f"Error loading configuration: {e}")


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    """
    Extract API host from configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        API host URL (stripped of whitespace)
    """
    try:
        host = config.get("api", {}).get("host", "")
        return host.strip()
    except Exception as e:
        pytest.fail(f"Error extracting API host from config: {e}")


@pytest.fixture(scope="session")
def api_auth(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract API authentication details from configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Authentication dictionary or None
    """
    return config.get("api", {}).get("auth")


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract test data from configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Test data dictionary
    """
    return config.get("test_data", {})


class APIClient:
    """
    Simple HTTP API client with support for common HTTP methods
    """
    
    def __init__(self, base_url: str, auth: Optional[Dict[str, Any]] = None, 
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialize API client
        
        Args:
            base_url: Base URL for API requests
            auth: Optional authentication configuration
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=max_retries,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Setup authentication if provided
        if auth:
            if auth.get("type") == "bearer":
                token = auth.get("token")
                if token:
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
            elif auth.get("type") == "basic":
                username = auth.get("username")
                password = auth.get("password")
                if username and password:
                    self.session.auth = (username, password)
            elif auth.get("type") == "api_key":
                key_name = auth.get("key_name", "X-API-Key")
                key_value = auth.get("key_value")
                if key_value:
                    self.session.headers.update({key_name: key_value})
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, method: str = 'GET',
                    data: Optional[Dict] = None, json: Optional[Dict] = None) -> requests.Response:
        """
        Make an HTTP request
        
        Args:
            endpoint: API endpoint (will be joined with base_url)
            params: Query parameters
            headers: Request headers
            method: HTTP method
            data: Form data
            json: JSON data
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=request_headers,
            data=data,
            json=json,
            timeout=self.timeout
        )
        
        return response
    
    def get(self, endpoint: str, headers: Optional[Dict] = None, 
            params: Optional[Dict] = None) -> requests.Response:
        """GET request"""
        return self.make_request(endpoint, params=params, headers=headers, method='GET')
    
    def post(self, endpoint: str, headers: Optional[Dict] = None, 
             params: Optional[Dict] = None, data: Optional[Dict] = None,
             json: Optional[Dict] = None) -> requests.Response:
        """POST request"""
        return self.make_request(endpoint, params=params, headers=headers, 
                                method='POST', data=data, json=json)
    
    def put(self, endpoint: str, headers: Optional[Dict] = None, 
            params: Optional[Dict] = None, data: Optional[Dict] = None,
            json: Optional[Dict] = None) -> requests.Response:
        """PUT request"""
        return self.make_request(endpoint, params=params, headers=headers, 
                                method='PUT', data=data, json=json)
    
    def patch(self, endpoint: str, headers: Optional[Dict] = None, 
              params: Optional[Dict] = None, data: Optional[Dict] = None,
              json: Optional[Dict] = None) -> requests.Response:
        """PATCH request"""
        return self.make_request(endpoint, params=params, headers=headers, 
                                method='PATCH', data=data, json=json)
    
    def delete(self, endpoint: str, headers: Optional[Dict] = None, 
               params: Optional[Dict] = None) -> requests.Response:
        """DELETE request"""
        return self.make_request(endpoint, params=params, headers=headers, method='DELETE')


@pytest.fixture(scope="session")
def api_client(api_host: str, api_auth: Optional[Dict[str, Any]]) -> APIClient:
    """
    Create API client instance with configuration
    
    Args:
        api_host: API host URL from config
        api_auth: API authentication from config
        
    Returns:
        Configured APIClient instance
    """
    return APIClient(base_url=api_host, auth=api_auth)


def pytest_configure(config):
    """
    Register custom pytest markers
    """
    config.addinivalue_line(
        "markers", "smoke: Mark test as smoke test for success scenarios"
    )
