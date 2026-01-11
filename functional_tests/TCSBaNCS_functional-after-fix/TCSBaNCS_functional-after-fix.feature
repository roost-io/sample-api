Feature: Comprehensive Testing of Financial Trading and Security Systems

  # UI Test Scenarios for Agent Login and MFA Verification
  @ui
  Scenario Outline: Agent Login and MFA Verification
    Given I am on the agent login page
    When I enter '<username>' and '<password>' into the login form
    And I click the 'Login' button
    Then I should see the MFA prompt
    When I complete MFA using a registered device
    Then I should be redirected to the dashboard
    And I should see '<expected_dashboard_feature>'

    Examples:
      | username | password | expected_dashboard_feature |
      | agent1   | pass123  | Portfolio Overview         |
      | agent2   | pass456  | Recent Transactions        |

  # API Test Scenarios for Customer Verification via Call Center
  @api
  Scenario Outline: Customer Verification via Call Center
    Given the API base URL is 'https://api.financialservice.com'
    And the authorization token is set
    When I send a POST request to '/api/customer/verify' with payload:
      """
      {
        "identification_type": "National ID",
        "national_id": "<national_id>"
      }
      """
    Then the response status should be 200
    And the response should contain 'verified' with value 'true'
    And the response should contain 'customer_details'

    Examples:
      | national_id |
      | 123456789   |
      | 987654321   |

  # API Test Scenarios for Real-time Data Feed Integration
  @api
  Scenario: Real-time Data Feed Integration
    Given the API base URL is 'https://api.marketdata.com'
    When I send a GET request to '/api/data/real-time'
    Then the response status should be 200
    And the response should contain 'data'
    And the data should be up-to-date

  # API Test Scenarios for Transaction Execution and Settlement
  @api
  Scenario Outline: Transaction Execution and Settlement
    Given the API base URL is 'https://api.tradingplatform.com'
    And the authorization token is set
    When I send a POST request to '/api/transactions/execute' with payload:
      """
      {
        "transaction_type": "<type>",
        "amount": "<amount>",
        "account_id": "<account_id>"
      }
      """
    Then the response status should be 201
    And the response should contain 'transaction_status' with value 'completed'

    Examples:
      | type  | amount | account_id |
      | buy   | 1000   | acc123     |
      | sell  | 500    | acc456     |

  # API Test Scenarios for Compliance Report Generation
  @api
  Scenario: Compliance Report Generation
    Given the API base URL is 'https://api.complianceservice.com'
    When I send a POST request to '/api/reports/generate' with payload:
      """
      {
        "report_type": "compliance",
        "period": "2023-Q1"
      }
      """
    Then the response status should be 200
    And the response should contain 'report_id'
    And the report should meet regulatory standards

  # UI Test Scenarios for Session Timeout and Automatic Logout
  @ui
  Scenario: Session Timeout and Automatic Logout
    Given I am logged into the system
    And I perform no activity for the duration of the session timeout period
    When I attempt to perform an action after the timeout period
    Then I should be automatically logged out
    And I should be prompted to log in again

  # API Test Scenarios for Data Encryption Verification
  @api
  Scenario: Data Encryption Verification
    Given the API base URL is 'https://api.secureservice.com'
    And I start the network monitoring tool
    When I log in with valid credentials
    Then all sensitive data should be encrypted in the network data

  # API Test Scenarios for Real-time Data Accuracy
  @api
  Scenario: Real-time Data Accuracy
    Given the API base URL is 'https://api.marketdata.com'
    When I compare the real-time data displayed in the system with actual market data
    Then there should be no discrepancies

  # API Test Scenarios for Error Handling and Alert Management
  @api
  Scenario: Error Handling and Alert Management
    Given the system is operational with all modules active
    When I simulate various operational errors
    Then the system should handle errors gracefully
    And alert the user with understandable alerts
    And log the errors accurately

  # API Test Scenarios for Security Transfer Within and Between Banks
  @api
  Scenario Outline: Verify Security Transfer Within and Between Banks
    Given the API base URL is 'https://api.bankingservice.com'
    And the authorization token is set
    When I send a POST request to '/api/security/transfer' with payload:
      """
      {
        "transfer_type": "<transfer_type>",
        "source_account": "<source_account>",
        "target_account": "<target_account>",
        "securities": "<securities>"
      }
      """
    Then the response status should be 200
    And the response should contain 'transfer_status' with value 'successful'

    Examples:
      | transfer_type | source_account | target_account | securities |
      | Within Bank   | acc789         | acc987         | 50 shares  |
      | Outside Bank  | acc789         | ext123         | 30 bonds   |
