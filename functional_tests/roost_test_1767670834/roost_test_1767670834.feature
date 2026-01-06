Feature: Security-Sensitive User Journeys and System Interactions in TCS BaNCS

  # UI Test Scenarios for Call Center System
  @ui @authentication @MFA
  Scenario Outline: User Login with MFA Process
    Given I am on the "Login" page of the Call Center
    When I enter "<username>" and "<password>"
    Then I should see an MFA prompt
    When I enter the MFA code "<mfa_code>"
    Then I should be logged into the dashboard
    And the successful login and MFA verification should be recorded

    Examples:
      | username   | password   | mfa_code   |
      | user1      | pass123    | 123456     |
      | user2      | pass456    | 654321     |

  @ui @authorization @RBAC
  Scenario: Role-Based Access for Supervisors
    Given I am logged in as a supervisor
    When I attempt to access management and report tools
    Then I should be granted access
    When I try to initiate high-privilege transactions
    Then access should be restricted
    
  # API Test Scenarios for Backend Core System
  @api @authentication @lockout
  Scenario Outline: Account Lockout after Multiple Failed Login Attempts
    Given the API base URL is '/api/auth'
    And the authorization token is set
    When I send a POST request to '/api/auth/login' with payload """
    { "username": "<username>", "password": "<wrong_password>" }
    """
    Then the response status should be 401
    And the response should contain 'account locked' after 3 attempts

    Examples:
      | username   | wrong_password |
      | user1      | wrongpass     |

  @api @customer_verification @OTP
  Scenario Outline: Customer OTP Verification
    Given the API base URL is '/api/verification'
    And the authorization token is set
    When I send a POST request to '/api/verification/otp' with payload """
    { "customerId": "<customer_id>", "otp": "<otp_code>" }
    """
    Then the response status should be <status>
    And the response should contain '<verification_message>'

    Examples:
      | customer_id | otp_code | status | verification_message           |
      | CUST001     | 111111   | 200    | otp verified successfully      |
      | CUST001     | 999999   | 403    | invalid otp, attempts exceeded |

  @api @profile_update @authorization
  Scenario: Update Sensitive Profile Information with Required Authorization
    Given the API base URL is '/api/customers'
    And the authorization token is auth_admin
    When I send a PUT request to '/api/customers/profile' with payload """
    { "customerId": "CUST001", "contactInfo": { "phone": "+972*****1234" } }
    """
    Then the response status should be 403
    And the request should be pending supervisor approval in logs

  # API Test for Security and Error Handling
  @api @secure_error_handling @PII_masking
  Scenario Outline: PII Masking in Error Messages
    Given the API base URL is '/api/errors'
    When I trigger an error with invalid data """
    { "cardNumber": "<invalid_card>" }
    """
    Then the error message should not contain "<sensitive_data>"
    And only a generic error code should be presented

    Examples:
      | invalid_card     | sensitive_data |
      | 1234-5678-8765   | 1234           |
      | 0000-0000-0000   | 0000           |

  # UI Test Scenarios for Session Management
  @ui @session_security @timeout
  Scenario: Ensure Session Timeout After Inactivity
    Given I am logged into the Call Center
    When I remain idle for the timeout period
    Then I should be prompted to re-login
    And the session timeout event should be logged

  # API Test for Unauthorized Access
  @api @access_control @audit_trail
  Scenario Outline: Unauthorized API Access Attempt
    Given the API base URL is '/api/admin'
    When I attempt a GET request without authorization
    Then the response status should be 401
    And the attempt should be recorded in the audit logs

    Examples:
      | endpoint         | method |
      | /api/admin/logs  | GET    |
      | /api/admin/users | GET    |

  # UI Test for Secure Logout and Session Termination
  @ui @session_management
  Scenario: Secure User Session Termination after Logout
    Given I am logged into the Call Center
    When I log out explicitly
    Then attempting to access the system with previous session data should fail
    And the session termination should be logged

  # API Test for Audit Log Integrity
  @api @audit_integrity @tamper_proof
  Scenario: Audit Log Integrity Check
    Given the API base URL is '/api/audit'
    When I attempt unauthorized modifications to audit logs
    Then modifications should be rejected
    And log integrity should remain intact, reflecting original activities
