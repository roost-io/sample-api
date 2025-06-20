Feature: Delete pet by ID

  Background:
    Given a pet exists with the following data:
      | name     | Rocky     |
      | tag      | bulldog   |
    And I have retrieved its petId

  Scenario: Successfully delete the pet
    When I send DELETE request to "/pet/{petId}"
    Then the response status code should be 204

  Scenario: Retrieving a deleted pet returns 404
    When I send GET request to "/pet/{petId}"
    Then the response status code should be 404
    And the response JSON.code should be 1
    And the response JSON.message should contain "not found"
