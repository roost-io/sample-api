Feature: Store inventory and error scenario

  Scenario: Get inventory counts by status
    When I send GET request to "/store/inventory"
    Then the response status code should be 200
    And the response JSON should contain integer values for keys "available", "pending", "sold"

  Scenario: Request order with invalid ID
    When I send GET request to "/store/order/999999"
    Then the response status code should be 404
    And the response JSON.code should be 1
    And the response JSON.message should contain "not found"
