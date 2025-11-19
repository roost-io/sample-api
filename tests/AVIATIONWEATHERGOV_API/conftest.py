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
        value: String containing environment variable patterns
        
    Returns:
        String with environment variables expanded
    """
    if not isinstance(value, str):
        return value
    
    # Pattern to match ${VAR:-default} or ${VAR}
    pattern = r'\$\{([^}:]+)(?::(-?)([^}]*))?\}'
    
    def replace_env(match):
        var_name = match.group(1)
        has_default = match.group(2) is not None
        default_value = match.group(3) if match.group(3) is not None else ''
        
        # Get environment variable value
        env_value = os.environ.get(var_name)
        
        if env_value is not None:
            return env_value
        elif has_default:
            return default_value
        else:
            return match.group(0)
    
    return re.sub(pattern, replace_env, value)


def _expand_env_in_config(config: Any) -> Any:
    """
    Recursively expand environment variables in configuration
    
    Args:
        config: Configuration object (dict, list, or primitive)
        
    Returns:
        Configuration with environment variables expanded
    """
    if isinstance(config, dict):
        return {key: _expand_env_in_config(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [_expand_env_in_config(item) for item in config]
    elif isinstance(config, str):
        return _expand_env_in_string(config)
    else:
        return config


@pytest.fixture(scope='session')
def config() -> Dict[str, Any]:
    """
    Load configuration from config.yml file
    
    Returns:
        Dictionary containing configuration data
    """
    # Get the directory where conftest.py is located
    config_dir = Path(__file__).parent
    config_file = os.path.join(str(config_dir), 'config.yml')
    
    try:
        with open(config_file, 'r') as f:
            raw_config = yaml.safe_load(f)
        
        # Expand environment variables in configuration
        expanded_config = _expand_env_in_config(raw_config)
        
        return expanded_config
    
    except FileNotFoundError:
        pytest.fail(f"Configuration file not found: {config_file}")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML configuration: {e}")
    except Exception as e:
        pytest.fail(f"Error loading configuration: {e}")


class APIClient:
    """
    Simple API client for making HTTP requests
    """
    
    def __init__(self, base_url: str, default_timeout: int = 30, max_retries: int = 3):
        """
        Initialize API client
        
        Args:
            base_url: Base URL for API requests
            default_timeout: Default timeout for requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.strip().rstrip('/')
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Configure retry strategy
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            method: HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
            params: Query parameters
            headers: Request headers
            data: Form data
            json: JSON payload
            timeout: Request timeout in seconds
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = timeout or self.default_timeout
        
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
            **kwargs
        )
        
        return response
    
    def get(
        self,
        endpoint: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make a GET request
        
        Args:
            endpoint: API endpoint
            headers: Request headers
            params: Query parameters
            timeout: Request timeout in seconds
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self.make_request(
            endpoint=endpoint,
            method='GET',
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs
        )
    
    def post(
        self,
        endpoint: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make a POST request
        
        Args:
            endpoint: API endpoint
            headers: Request headers
            params: Query parameters
            data: Form data
            json: JSON payload
            timeout: Request timeout in seconds
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self.make_request(
            endpoint=endpoint,
            method='POST',
            headers=headers,
            params=params,
            data=data,
            json=json,
            timeout=timeout,
            **kwargs
        )
    
    def put(
        self,
        endpoint: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make a PUT request
        
        Args:
            endpoint: API endpoint
            headers: Request headers
            params: Query parameters
            data: Form data
            json: JSON payload
            timeout: Request timeout in seconds
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self.make_request(
            endpoint=endpoint,
            method='PUT',
            headers=headers,
            params=params,
            data=data,
            json=json,
            timeout=timeout,
            **kwargs
        )
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make a DELETE request
        
        Args:
            endpoint: API endpoint
            headers: Request headers
            params: Query parameters
            timeout: Request timeout in seconds
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self.make_request(
            endpoint=endpoint,
            method='DELETE',
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs
        )
    
    def patch(
        self,
        endpoint: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make a PATCH request
        
        Args:
            endpoint: API endpoint
            headers: Request headers
            params: Query parameters
            data: Form data
            json: JSON payload
            timeout: Request timeout in seconds
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self.make_request(
            endpoint=endpoint,
            method='PATCH',
            headers=headers,
            params=params,
            data=data,
            json=json,
            timeout=timeout,
            **kwargs
        )
    
    def close(self):
        """Close the session"""
        self.session.close()


@pytest.fixture(scope='session')
def api_host(config) -> str:
    """
    Get API host from configuration
    
    Args:
        config: Configuration fixture
        
    Returns:
        API host URL
    """
    try:
        host = config['api']['host']
        return host.strip()
    except KeyError:
        pytest.fail("API host not found in configuration")


@pytest.fixture(scope='session')
def api_client(api_host) -> APIClient:
    """
    Create API client instance
    
    Args:
        api_host: API host URL
        
    Returns:
        APIClient instance
    """
    client = APIClient(base_url=api_host)
    yield client
    client.close()


@pytest.fixture(scope='function')
def api_client_function(api_host) -> APIClient:
    """
    Create function-scoped API client instance
    
    Args:
        api_host: API host URL
        
    Returns:
        APIClient instance
    """
    client = APIClient(base_url=api_host)
    yield client
    client.close()
