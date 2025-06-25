Feature: Basic API Health Check and Connectivity

  Scenario: Verify API service is available and responding
    Given the API base URL is configured
    When I send a GET request to "/health"
    Then the response status code should be 200
    And the response should indicate the service is "UP"

  Scenario: Validate API authentication mechanism
    Given I have valid API credentials
    When I attempt to authenticate with the API
    Then I should receive a valid authentication token
    And the response status code should be 200

  Scenario: Handle invalid authentication attempts
    Given I have invalid API credentials
    When I attempt to authenticate with the API
    Then the response status code should be 401
    And the response should contain an error message "Invalid credentials"

  Scenario: Verify API rate limiting
    Given I have valid API credentials
    When I send multiple requests exceeding the rate limit threshold
    Then the response status code should be 429
    And the response should contain "Too Many Requests"
    And the response headers should include rate limit information
