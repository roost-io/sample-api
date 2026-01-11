Feature: Security and Access Control Functional Testing

  # UI Test Scenarios
  @ui
  Scenario: Agent Login with SSO and MFA
    Given I navigate to the login page
    When I enter "agent****" as username and proceed with SSO
    And I complete the MFA step using "****1234" as OTP
    Then I should see a success message and access the system dashboard

  @ui
  Scenario Outline: Supervisor Role-Based Access Control
    Given I log in as <role>
    When I attempt to access the supervisor dashboard
    Then I should see <access_message>

    Examples:
      | role      | access_message            |
      | supervisor | Access granted             |
      | agent      | Not authorized message     |

  # API Test Scenarios
  @api
  Scenario Outline: Customer Identity Verification via OTP
    Given the API base URL is "https://api.example.com"
    And the authorization token is set
    When I initiate a high-risk transaction for customer with phone "+1*****1234"
    And the system sends an OTP "****5678"
    Then I send a POST request to "/api/verifyOTP" with payload """
    {
      "otp": "<otp>"
    }
    """
    And the response status should be <status>
    And the response should contain "<message>"

    Examples:
      | otp       | status | message          |
      | ****5678  | 200    | Transaction successful |
      | wrongOTP  | 401    | Invalid OTP      |

  @api
  Scenario Outline: Access Control on Transaction Handling by Agents
    Given I log in as <user_type> with appropriate credentials
    When I navigate to the transaction handling section
    Then I attempt to access a transaction requiring supervisor approval
    And the response status should be <status>
    And the response should contain "<access_message>"

    Examples:
      | user_type | status | access_message     |
      | agent     | 403    | Not authorized     |
      | supervisor| 200    | Access granted     |

  @api
  Scenario Outline: Secure Password Reset Process
    Given the API base URL is "https://api.example.com"
    When I initiate password reset for "agent****@example.com"
    And I verify using "****1234" as OTP
    Then I send a PATCH request to "/api/passwordReset" with payload """
    {
      "newPassword": "<new_password>"
    }
    """
    And the response status should be <status>
    And the response should contain "<message>"

    Examples:
      | new_password | status | message            |
      | ****1234     | 200    | Password reset successful |
      | short        | 400    | Invalid password   |

  # Mixed UI and API Scenarios
  @ui @api
  Scenario Outline: Fraudulent Transaction Alerts and Blocking
    Given I execute a transaction with ID "TXN****" that violates fraud detection rules
    When the fraud detection system flags the transaction
    Then the transaction is blocked
    And an alert is sent to designated personnel with details "<alert_message>"

    Examples:
      | alert_message                        |
      | Alert: Excessive Amount Detected     |
      | Alert: Transaction Suspended         |
