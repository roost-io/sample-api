# Auto-generated authentication tests
# Auto-generated authentication tests
# Generated from Swagger/OpenAPI spec
import pytest
import requests
from typing import Dict, Any


class TestAuthentication:
    """Test suite for API authentication scenarios"""

    def test_oauth2_auth(self, api_client, oauth2_token):
        """Test OAuth2 authentication"""
        headers = {"Authorization": f"Bearer {oauth2_token}"}
        response = api_client.get("/me", headers=headers)
        assert response.status_code in [200, 401]

    @pytest.mark.parametrize("endpoint", ["/pet","/pet/findByStatus","/pet/findByTags","/pet/123","/pet/123/uploadImage","/store/inventory","/store/order","/store/order/123","/user","/user/createWithList","/user/login","/user/logout","/user/test"])
    def test_valid_api_key_access(self, api_helper, valid_api_key, valid_location, endpoint):
        """Test valid API key allows access to all endpoints"""
        params = {"q": valid_location}
        if "header" == "query":
            params["api_key"] = valid_api_key
            response = api_helper.make_request(endpoint, params)
        else:
            headers = {"api_key": valid_api_key}
            response = api_helper.make_request(endpoint, params, headers=headers)

        assert response.status_code not in [401, 403]

    @pytest.mark.parametrize("endpoint", ["/pet","/pet/findByStatus","/pet/findByTags","/pet/123","/pet/123/uploadImage","/store/inventory","/store/order","/store/order/123","/user","/user/createWithList","/user/login","/user/logout","/user/test"])
    def test_missing_api_key_denied(self, api_helper, valid_location, endpoint):
        """Test that requests without API key are denied"""
        params = {"q": valid_location}
        response = api_helper.make_request(endpoint, params)
        assert response.status_code == 401
        error_data = response.json()
        assert 'error' in error_data

    @pytest.mark.parametrize("endpoint", ["/pet","/pet/findByStatus","/pet/findByTags","/pet/123","/pet/123/uploadImage","/store/inventory","/store/order","/store/order/123","/user","/user/createWithList","/user/login","/user/logout","/user/test"])
    def test_invalid_api_key_denied(self, api_helper, invalid_api_key, valid_location, endpoint):
        """Test invalid API key is denied with 401"""
        params = {"q": valid_location}
        if "header" == "query":
            params["api_key"] = invalid_api_key
            response = api_helper.make_request(endpoint, params)
        else:
            headers = {"api_key": invalid_api_key}
            response = api_helper.make_request(endpoint, params, headers=headers)

        assert response.status_code == 401
        error_data = response.json()
        assert 'error' in error_data
