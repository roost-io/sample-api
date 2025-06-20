Feature: Query pets by status and tags

  Scenario: Retrieve pets by status
    Given I set request-param "status" to "available"
    When I send GET request to "/pet/findByStatus"
    Then the response status code should be 200
    And each item in response JSON array should have a "status" equal to "available"

  Scenario: Retrieve pets by tags
    Given I set request-param "tags" to "trial,test"
    When I send GET request to "/pet/findByTags"
    Then the response status code should be 200
    And the response JSON should be an array
