Feature: Compliance and Security Testing for Agent and Customer Management

  # UI and API Test Scenarios for comprehensive testing

  @authentication @ui @api
  Scenario Outline: Agent Authentication with SSO and MFA
    Given the agent account is prepared with SSO and MFA
    When the agent navigates to the login page
    And enters a valid "<username>" and "<password>"
    And successfully inputs the MFA code "<mfa_code>"
    Then the agent should be logged in successfully
    And audit logs should contain user ID, timestamp, login attempts, and account lock status

    Examples:
      | username     | password   | mfa_code |
      | valid_user   | valid_pass | 123456   |
      | locked_user  | wrong_pass | 123456   |
  
  @authentication @ui
  Scenario Outline: Account Lockout after Failed Login Attempts
    Given the agent account is not locked
    When the agent repeatedly enters an invalid "<username>" or "<password>" for 5 attempts
    Then the account should be locked
    And any further login attempts should be prevented
    And audit logs should include the account lock status

    Examples:
      | username     | password   |
      | valid_user   | wrong_pass |
      | invalid_user | valid_pass |

  @rbac @ui
  Scenario: RBAC Enforcement for Supervisor Screens
    Given an agent logs in with basic permissions
    When the agent attempts to access a supervisor screen
    Then access should be denied and an error message displayed
    And audit logs should document the access attempt and role mismatch

  @kba @ui
  Scenario Outline: Customer Identification with KBA Verification
    Given a customer account exists with KBA setup
    When the agent initiates verification and enters the answer "<kba_answer>"
    Then the system should "<result>" the verification
    And audit the session including answer status

    Examples:
      | kba_answer | result    |
      | correct    | proceed   |
      | incorrect  | block     |
      | random     | additional |

  @pii @ui
  Scenario: PII/PCI Data Masking in Customer Profiles
    Given an agent is logged in with access to customer profiles
    When visiting a customer profile with PII/PCI data
    Then PAN should be partially masked, and CVV completely hidden
    And attempts to view masked details should be logged

  @session @ui
  Scenario: Session Timeout and Security Handling
    Given an agent is logged in with session timeout set to 10 minutes
    When the session is idle for over 10 minutes
    And the agent attempts any action post-timeout without re-logging
    Then the session should end automatically requiring a fresh login
    And audit logs must capture session timeout details

  @session @ui @api
  Scenario: Concurrent Session Management
    Given an agent account is active on Device A
    When the same agent logs in on Device B
    Then Device B login forces logout from Device A
    And an action on Device A should prompt a re-login
    And logs should include session terminations and login attempts
  
  @audit @ui
  Scenario: Sensitive Action Audit Trail Verification
    Given an agent has permission to change beneficiary details
    When a new beneficiary is added
    Then the audit log should record the action with full details
    And attempts without permissions should be logged for failures

  @fraud @api
  Scenario: Fraud Signal Detection and Additional Verification
    Given transaction rules are configured to identify high-risk actions
    When an agent attempts a transaction exceeding the threshold
    Then the system should identify it as high-risk and demand further verification
    And audit logs must record the fraud assessment and verification prompt

  @access_control @ui
  Scenario: Call Recording Access Control Verification
    Given recordings are accessible only by supervisors
    When a supervisor searches and plays a recording
    Then the action should be successful
    And an agent attempting the same should be denied with an error message
    And audit trails should log access attempts and roles

  @error_handling @ui
  Scenario Outline: Secure Error Handling and Message Consistency
    Given an agent has role-based access
    When "<action>" triggers a system error
    Then the error message should be generic and secure
    And should not expose internal system information

    Examples:
      | action                             |
      | accessing unauthorized section     |
      | entering invalid data              |
      | malicious input for error trigger  |
