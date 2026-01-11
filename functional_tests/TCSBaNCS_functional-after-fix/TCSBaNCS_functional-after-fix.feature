Feature: Comprehensive System Testing for Trading and Security Operations

  # UI Test Scenarios
  @ui
  Scenario Outline: Agent Login with MFA and Handling Lockout Scenarios
    Given I am on the login page
    When I enter '<username>' and '<password>'
    And I input the MFA code from the agent's MFA device
    And I submit the login form
    Then I should be directed to the dashboard
    And I should see a message '<expected_message>'

    Examples:
      | username | password | expected_message       |
      | agent1   | pass123  | "Successfully logged in" |
      | agent2   | pass456  | "Account locked after multiple failed attempts" |

  @ui
  Scenario Outline: Customer Verification via KBA/OTP
    Given I am on the customer verification page
    When I select the customer verification option
    And the system sends '<method>' to the customer
    And the customer provides correct '<response>'
    Then the system should verify the customer and allow progression to sensitive account actions

    Examples:
      | method | response |
      | KBA    | correct  |
      | OTP    | correct  |

  @ui
  Scenario: Session Timeout and Auto-Logout
    Given an agent is logged in and remains inactive
    When the session timeout period elapses
    Then the system should automatically log the agent out
    And require re-authentication

  # API Test Scenarios
  @api
  Scenario Outline: Audit Trail and Logging for Sensitive Actions
    Given the agent is authenticated and authorized to perform sensitive actions
    When the agent performs a '<transaction_type>' transaction
    Then the system should log the action with details including agent ID, timestamp, and transaction type

    Examples:
      | transaction_type       |
      | modifying customer info |
      | deleting customer info  |

  @api
  Scenario: Error Handling for Data Integration with External Systems
    Given external systems are configured to send data
    When the system receives incorrect data formats
    Then the system should log the error
    And not process the incorrect data

  @api
  Scenario Outline: Verify Order Placement and Execution for Equity Buy Orders
    Given a user is authenticated and has sufficient balance
    When the user places an order for '<equity>' with quantity '<quantity>' and price '<price>'
    Then the order should be validated and executed
    And the user should receive confirmation with order details

    Examples:
      | equity   | quantity | price |
      | Equity A | 10       | 100   |
      | Equity B | 5        | 200   |

  @api
  Scenario Outline: Real-Time Market Data Accuracy
    Given market data feeds from TASE and Bloomberg are active
    When the user accesses the market data section
    Then the displayed data for '<security>' should be accurate and match the data from external sources

    Examples:
      | security |
      | Security X |
      | Security Y |

  @api
  Scenario Outline: Comprehensive Audit Trail for Transactions
    Given a user performs various transactions on the platform
    When the system logs each transaction
    Then the audit logs should contain detailed information about each '<transaction_type>'

    Examples:
      | transaction_type |
      | trade           |
      | transfer        |

  @api
  Scenario Outline: Error Handling and Exception Management for Trading Operations
    Given the trading platform is operational
    When various trading errors such as '<error_type>' occur
    Then the system should handle the errors gracefully
    And provide clear error messages
    And log the incidents appropriately
    And ensure data integrity post-error

    Examples:
      | error_type       |
      | network failure  |
      | data format error|
