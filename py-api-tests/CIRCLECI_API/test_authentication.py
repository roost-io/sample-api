# Auto-generated authentication tests
# Auto-generated authentication tests
# Generated from Swagger/OpenAPI spec
import pytest
import requests
from typing import Dict, Any


class TestAuthentication:
    """Test suite for API authentication scenarios"""

    @pytest.mark.parametrize("endpoint", ["/context","/context/test","/context/test/environment-variable","/context/test/environment-variable/test","/insights/pages/test/summary","/insights/time-series/test/workflows/test/jobs","/insights/test/summary","/insights/test/branches","/insights/test/flaky-tests","/insights/test/workflows","/insights/test/workflows/test","/insights/test/workflows/test/jobs","/insights/test/workflows/test/summary","/insights/test/workflows/test/test-metrics","/jobs/test/cancel","/me","/me/collaborations","/organization","/organization/test","/organization/test/project","/organization/test/url-orb-allow-list","/organization/test/url-orb-allow-list/test","/pipeline","/pipeline/continue","/pipeline/test","/pipeline/test/config","/pipeline/test/values","/pipeline/test/workflow","/project/test","/project/test/checkout-key","/project/test/checkout-key/test","/project/test/envvar","/project/test/envvar/test","/project/test/job/test","/project/test/job/test/cancel","/project/test/pipeline","/project/test/pipeline/mine","/project/test/pipeline/test","/project/test/schedule","/project/test/test/artifacts","/project/test/test/tests","/schedule/test","/user/test","/webhook","/webhook/test","/workflow/test","/workflow/test/approve/test","/workflow/test/cancel","/workflow/test/job","/workflow/test/rerun","/org/test/oidc-custom-claims","/org/test/project/test/oidc-custom-claims","/owner/test/context/test/decision","/owner/test/context/test/decision/settings","/owner/test/context/test/decision/test","/owner/test/context/test/decision/test/policy-bundle","/owner/test/context/test/policy-bundle","/owner/test/context/test/policy-bundle/test","/context/test/restrictions","/context/test/restrictions/test","/project/github/test/test","/project/github/test/test/settings","/organizations/test/usage_export_job","/organizations/test/usage_export_job/test","/project/github/test/test/pipeline/run","/projects/test/pipeline-definitions","/projects/test/pipeline-definitions/test","/projects/test/pipeline-definitions/test/triggers","/projects/test/triggers/test","/projects/test/rollback"])
    def test_valid_api_key_access(self, api_helper, valid_api_key, valid_location, endpoint):
        """Test valid API key allows access to all endpoints"""
        params = {"q": valid_location}
        if "header" == "query":
            params["Circle-Token"] = valid_api_key
            response = api_helper.make_request(endpoint, params)
        else:
            headers = {"Circle-Token": valid_api_key}
            response = api_helper.make_request(endpoint, params, headers=headers)

        assert response.status_code not in [401, 403]

    @pytest.mark.parametrize("endpoint", ["/context","/context/test","/context/test/environment-variable","/context/test/environment-variable/test","/insights/pages/test/summary","/insights/time-series/test/workflows/test/jobs","/insights/test/summary","/insights/test/branches","/insights/test/flaky-tests","/insights/test/workflows","/insights/test/workflows/test","/insights/test/workflows/test/jobs","/insights/test/workflows/test/summary","/insights/test/workflows/test/test-metrics","/jobs/test/cancel","/me","/me/collaborations","/organization","/organization/test","/organization/test/project","/organization/test/url-orb-allow-list","/organization/test/url-orb-allow-list/test","/pipeline","/pipeline/continue","/pipeline/test","/pipeline/test/config","/pipeline/test/values","/pipeline/test/workflow","/project/test","/project/test/checkout-key","/project/test/checkout-key/test","/project/test/envvar","/project/test/envvar/test","/project/test/job/test","/project/test/job/test/cancel","/project/test/pipeline","/project/test/pipeline/mine","/project/test/pipeline/test","/project/test/schedule","/project/test/test/artifacts","/project/test/test/tests","/schedule/test","/user/test","/webhook","/webhook/test","/workflow/test","/workflow/test/approve/test","/workflow/test/cancel","/workflow/test/job","/workflow/test/rerun","/org/test/oidc-custom-claims","/org/test/project/test/oidc-custom-claims","/owner/test/context/test/decision","/owner/test/context/test/decision/settings","/owner/test/context/test/decision/test","/owner/test/context/test/decision/test/policy-bundle","/owner/test/context/test/policy-bundle","/owner/test/context/test/policy-bundle/test","/context/test/restrictions","/context/test/restrictions/test","/project/github/test/test","/project/github/test/test/settings","/organizations/test/usage_export_job","/organizations/test/usage_export_job/test","/project/github/test/test/pipeline/run","/projects/test/pipeline-definitions","/projects/test/pipeline-definitions/test","/projects/test/pipeline-definitions/test/triggers","/projects/test/triggers/test","/projects/test/rollback"])
    def test_missing_api_key_denied(self, api_helper, valid_location, endpoint):
        """Test that requests without API key are denied"""
        params = {"q": valid_location}
        response = api_helper.make_request(endpoint, params)
        assert response.status_code == 401
        error_data = response.json()
        assert 'error' in error_data

    @pytest.mark.parametrize("endpoint", ["/context","/context/test","/context/test/environment-variable","/context/test/environment-variable/test","/insights/pages/test/summary","/insights/time-series/test/workflows/test/jobs","/insights/test/summary","/insights/test/branches","/insights/test/flaky-tests","/insights/test/workflows","/insights/test/workflows/test","/insights/test/workflows/test/jobs","/insights/test/workflows/test/summary","/insights/test/workflows/test/test-metrics","/jobs/test/cancel","/me","/me/collaborations","/organization","/organization/test","/organization/test/project","/organization/test/url-orb-allow-list","/organization/test/url-orb-allow-list/test","/pipeline","/pipeline/continue","/pipeline/test","/pipeline/test/config","/pipeline/test/values","/pipeline/test/workflow","/project/test","/project/test/checkout-key","/project/test/checkout-key/test","/project/test/envvar","/project/test/envvar/test","/project/test/job/test","/project/test/job/test/cancel","/project/test/pipeline","/project/test/pipeline/mine","/project/test/pipeline/test","/project/test/schedule","/project/test/test/artifacts","/project/test/test/tests","/schedule/test","/user/test","/webhook","/webhook/test","/workflow/test","/workflow/test/approve/test","/workflow/test/cancel","/workflow/test/job","/workflow/test/rerun","/org/test/oidc-custom-claims","/org/test/project/test/oidc-custom-claims","/owner/test/context/test/decision","/owner/test/context/test/decision/settings","/owner/test/context/test/decision/test","/owner/test/context/test/decision/test/policy-bundle","/owner/test/context/test/policy-bundle","/owner/test/context/test/policy-bundle/test","/context/test/restrictions","/context/test/restrictions/test","/project/github/test/test","/project/github/test/test/settings","/organizations/test/usage_export_job","/organizations/test/usage_export_job/test","/project/github/test/test/pipeline/run","/projects/test/pipeline-definitions","/projects/test/pipeline-definitions/test","/projects/test/pipeline-definitions/test/triggers","/projects/test/triggers/test","/projects/test/rollback"])
    def test_invalid_api_key_denied(self, api_helper, invalid_api_key, valid_location, endpoint):
        """Test invalid API key is denied with 401"""
        params = {"q": valid_location}
        if "header" == "query":
            params["Circle-Token"] = invalid_api_key
            response = api_helper.make_request(endpoint, params)
        else:
            headers = {"Circle-Token": invalid_api_key}
            response = api_helper.make_request(endpoint, params, headers=headers)

        assert response.status_code == 401
        error_data = response.json()
        assert 'error' in error_data

    def test_basic_auth_valid(self, api_client, basic_auth):
        """Test valid basic authentication"""
        response = api_client.get("/me", auth=basic_auth)
        assert response.status_code == 200

    def test_basic_auth_invalid(self, api_client):
        """Test invalid basic authentication"""
        response = api_client.get("/me", auth=('invalid', 'credentials'))
        assert response.status_code == 401

    @pytest.mark.parametrize("endpoint", ["/context","/context/test","/context/test/environment-variable","/context/test/environment-variable/test","/insights/pages/test/summary","/insights/time-series/test/workflows/test/jobs","/insights/test/summary","/insights/test/branches","/insights/test/flaky-tests","/insights/test/workflows","/insights/test/workflows/test","/insights/test/workflows/test/jobs","/insights/test/workflows/test/summary","/insights/test/workflows/test/test-metrics","/jobs/test/cancel","/me","/me/collaborations","/organization","/organization/test","/organization/test/project","/organization/test/url-orb-allow-list","/organization/test/url-orb-allow-list/test","/pipeline","/pipeline/continue","/pipeline/test","/pipeline/test/config","/pipeline/test/values","/pipeline/test/workflow","/project/test","/project/test/checkout-key","/project/test/checkout-key/test","/project/test/envvar","/project/test/envvar/test","/project/test/job/test","/project/test/job/test/cancel","/project/test/pipeline","/project/test/pipeline/mine","/project/test/pipeline/test","/project/test/schedule","/project/test/test/artifacts","/project/test/test/tests","/schedule/test","/user/test","/webhook","/webhook/test","/workflow/test","/workflow/test/approve/test","/workflow/test/cancel","/workflow/test/job","/workflow/test/rerun","/org/test/oidc-custom-claims","/org/test/project/test/oidc-custom-claims","/owner/test/context/test/decision","/owner/test/context/test/decision/settings","/owner/test/context/test/decision/test","/owner/test/context/test/decision/test/policy-bundle","/owner/test/context/test/policy-bundle","/owner/test/context/test/policy-bundle/test","/context/test/restrictions","/context/test/restrictions/test","/project/github/test/test","/project/github/test/test/settings","/organizations/test/usage_export_job","/organizations/test/usage_export_job/test","/project/github/test/test/pipeline/run","/projects/test/pipeline-definitions","/projects/test/pipeline-definitions/test","/projects/test/pipeline-definitions/test/triggers","/projects/test/triggers/test","/projects/test/rollback"])
    def test_valid_api_key_access(self, api_helper, valid_api_key, valid_location, endpoint):
        """Test valid API key allows access to all endpoints"""
        params = {"q": valid_location}
        if "query" == "query":
            params["circle-token"] = valid_api_key
            response = api_helper.make_request(endpoint, params)
        else:
            headers = {"circle-token": valid_api_key}
            response = api_helper.make_request(endpoint, params, headers=headers)

        assert response.status_code not in [401, 403]

    @pytest.mark.parametrize("endpoint", ["/context","/context/test","/context/test/environment-variable","/context/test/environment-variable/test","/insights/pages/test/summary","/insights/time-series/test/workflows/test/jobs","/insights/test/summary","/insights/test/branches","/insights/test/flaky-tests","/insights/test/workflows","/insights/test/workflows/test","/insights/test/workflows/test/jobs","/insights/test/workflows/test/summary","/insights/test/workflows/test/test-metrics","/jobs/test/cancel","/me","/me/collaborations","/organization","/organization/test","/organization/test/project","/organization/test/url-orb-allow-list","/organization/test/url-orb-allow-list/test","/pipeline","/pipeline/continue","/pipeline/test","/pipeline/test/config","/pipeline/test/values","/pipeline/test/workflow","/project/test","/project/test/checkout-key","/project/test/checkout-key/test","/project/test/envvar","/project/test/envvar/test","/project/test/job/test","/project/test/job/test/cancel","/project/test/pipeline","/project/test/pipeline/mine","/project/test/pipeline/test","/project/test/schedule","/project/test/test/artifacts","/project/test/test/tests","/schedule/test","/user/test","/webhook","/webhook/test","/workflow/test","/workflow/test/approve/test","/workflow/test/cancel","/workflow/test/job","/workflow/test/rerun","/org/test/oidc-custom-claims","/org/test/project/test/oidc-custom-claims","/owner/test/context/test/decision","/owner/test/context/test/decision/settings","/owner/test/context/test/decision/test","/owner/test/context/test/decision/test/policy-bundle","/owner/test/context/test/policy-bundle","/owner/test/context/test/policy-bundle/test","/context/test/restrictions","/context/test/restrictions/test","/project/github/test/test","/project/github/test/test/settings","/organizations/test/usage_export_job","/organizations/test/usage_export_job/test","/project/github/test/test/pipeline/run","/projects/test/pipeline-definitions","/projects/test/pipeline-definitions/test","/projects/test/pipeline-definitions/test/triggers","/projects/test/triggers/test","/projects/test/rollback"])
    def test_missing_api_key_denied(self, api_helper, valid_location, endpoint):
        """Test that requests without API key are denied"""
        params = {"q": valid_location}
        response = api_helper.make_request(endpoint, params)
        assert response.status_code == 401
        error_data = response.json()
        assert 'error' in error_data

    @pytest.mark.parametrize("endpoint", ["/context","/context/test","/context/test/environment-variable","/context/test/environment-variable/test","/insights/pages/test/summary","/insights/time-series/test/workflows/test/jobs","/insights/test/summary","/insights/test/branches","/insights/test/flaky-tests","/insights/test/workflows","/insights/test/workflows/test","/insights/test/workflows/test/jobs","/insights/test/workflows/test/summary","/insights/test/workflows/test/test-metrics","/jobs/test/cancel","/me","/me/collaborations","/organization","/organization/test","/organization/test/project","/organization/test/url-orb-allow-list","/organization/test/url-orb-allow-list/test","/pipeline","/pipeline/continue","/pipeline/test","/pipeline/test/config","/pipeline/test/values","/pipeline/test/workflow","/project/test","/project/test/checkout-key","/project/test/checkout-key/test","/project/test/envvar","/project/test/envvar/test","/project/test/job/test","/project/test/job/test/cancel","/project/test/pipeline","/project/test/pipeline/mine","/project/test/pipeline/test","/project/test/schedule","/project/test/test/artifacts","/project/test/test/tests","/schedule/test","/user/test","/webhook","/webhook/test","/workflow/test","/workflow/test/approve/test","/workflow/test/cancel","/workflow/test/job","/workflow/test/rerun","/org/test/oidc-custom-claims","/org/test/project/test/oidc-custom-claims","/owner/test/context/test/decision","/owner/test/context/test/decision/settings","/owner/test/context/test/decision/test","/owner/test/context/test/decision/test/policy-bundle","/owner/test/context/test/policy-bundle","/owner/test/context/test/policy-bundle/test","/context/test/restrictions","/context/test/restrictions/test","/project/github/test/test","/project/github/test/test/settings","/organizations/test/usage_export_job","/organizations/test/usage_export_job/test","/project/github/test/test/pipeline/run","/projects/test/pipeline-definitions","/projects/test/pipeline-definitions/test","/projects/test/pipeline-definitions/test/triggers","/projects/test/triggers/test","/projects/test/rollback"])
    def test_invalid_api_key_denied(self, api_helper, invalid_api_key, valid_location, endpoint):
        """Test invalid API key is denied with 401"""
        params = {"q": valid_location}
        if "query" == "query":
            params["circle-token"] = invalid_api_key
            response = api_helper.make_request(endpoint, params)
        else:
            headers = {"circle-token": invalid_api_key}
            response = api_helper.make_request(endpoint, params, headers=headers)

        assert response.status_code == 401
        error_data = response.json()
        assert 'error' in error_data
