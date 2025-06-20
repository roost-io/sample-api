Feature: Update an existing pet

  Background:
    Given a pet exists with the following data:
      | name     | Buddy     |
      | tag      | dog       |
    And I have retrieved its petId

  Scenario: Update pet's name and tag
    Given I set request-header "Content-Type" to "application/json"
    And I set request-body to:
      """
      {
        "id": "<petId>",
        "name": "BuddyUpdated",
        "tag": "dog-updated"
      }
      """
    When I send PUT request to "/pet"
    Then the response status code should be 200
    And the response JSON.id should equal <petId>
    And the response JSON.name should be "BuddyUpdated"
    And the response JSON.tag should be "dog-updated"
