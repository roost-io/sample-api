# Auto-generated authentication tests
# Auto-generated authentication tests
# Generated from Swagger/OpenAPI spec
import pytest
import requests
from typing import Dict, Any


class TestAuthentication:
    """Test suite for API authentication scenarios"""

    @pytest.mark.parametrize("endpoint", ["/current.json","/forecast.json","/future.json","/history.json","/marine.json","/search.json","/ip.json","/timezone.json","/astronomy.json"])
    def test_valid_api_key_access(self, api_helper, valid_api_key, valid_location, endpoint):
        """Test valid API key allows access to all endpoints"""
        params = {"q": valid_location}
        if "query" == "query":
            params["key"] = valid_api_key
            response = api_helper.make_request(endpoint, params)
        else:
            headers = {"key": valid_api_key}
            response = api_helper.make_request(endpoint, params, headers=headers)

        assert response.status_code not in [401, 403]

    @pytest.mark.parametrize("endpoint", ["/current.json","/forecast.json","/future.json","/history.json","/marine.json","/search.json","/ip.json","/timezone.json","/astronomy.json"])
    def test_missing_api_key_denied(self, api_helper, valid_location, endpoint):
        """Test that requests without API key are denied"""
        params = {"q": valid_location}
        response = api_helper.make_request(endpoint, params)
        assert response.status_code == 401
        error_data = response.json()
        assert 'error' in error_data

    @pytest.mark.parametrize("endpoint", ["/current.json","/forecast.json","/future.json","/history.json","/marine.json","/search.json","/ip.json","/timezone.json","/astronomy.json"])
    def test_invalid_api_key_denied(self, api_helper, invalid_api_key, valid_location, endpoint):
        """Test invalid API key is denied with 401"""
        params = {"q": valid_location}
        if "query" == "query":
            params["key"] = invalid_api_key
            response = api_helper.make_request(endpoint, params)
        else:
            headers = {"key": invalid_api_key}
            response = api_helper.make_request(endpoint, params, headers=headers)

        assert response.status_code == 401
        error_data = response.json()
        assert 'error' in error_data
