Feature: BambooHR Okta Provisioning Constructor and Initialization
  As a system administrator
  I want to initialize the provisioning system with valid configurations
  So that I can establish connections to both BambooHR and Okta APIs

  Scenario: Valid Configuration Initialization
    Given I have valid BambooHR configuration with subdomain "testcompany" and apiKey "valid-api-key"
    And I have valid Okta configuration with domain "testcompany.okta.com" and apiToken "valid-token"
    When I create a new BambooHROktaProvisioning instance
    Then the instance should be created successfully
    And the BambooHR baseURL should be "https://api.bamboohr.com/api/gateway.php/testcompany/v1"
    And the Okta baseURL should be "https://testcompany.okta.com/api/v1"
    And the axios clients should be configured with correct headers and authentication

  Scenario: Missing Configuration Parameters
    Given I have incomplete BambooHR configuration with subdomain null and apiKey empty
    And I have incomplete Okta configuration with domain empty and apiToken null
    When I attempt to create a new BambooHROktaProvisioning instance
    Then the constructor should handle the error gracefully or throw an appropriate error message
