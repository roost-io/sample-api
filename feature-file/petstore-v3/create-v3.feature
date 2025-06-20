Feature: Create and retrieve a pet

  Background:
    Given the Petstore API is available at https://petstore3.swagger.io/api/v3

  Scenario: Successfully create a new pet and retrieve it by ID
    Given I set request-header "Content-Type" to "application/json"
    And I set request-body to:
      """
      {
        "name": "Fluffy",
        "tag": "cat"
      }
      """
    When I send POST request to "/pet"
    Then the response status code should be 200
    And the response JSON should include:
      | name | Fluffy |
      | tag  | cat    |
    And the response JSON should include an integer value for "id"
    When I extract the value of "id" as petId
    And I send GET request to "/pet/{petId}"
    Then the response status code should be 200
    And the response JSON.name should be "Fluffy"
    And the response JSON.tag should be "cat"
