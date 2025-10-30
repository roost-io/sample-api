Feature: Bank Loan Prepayment System API Testing
  
  Background:
    Given the API base URL is set from environment variable "API_BASE_URL"
    And the authorization header is set with valid bearer token from environment variable "AUTH_TOKEN"
    And the content type is "application/json"
    And the system is configured with test loan accounts and customer data

  Scenario: View Prepayment Options for Active Loan
    Given a customer with ID "CUST001" has an active loan account "LOAN12345"
    When I send a GET request to "/api/v1/loans/LOAN12345/prepayment-options"
    Then the response status should be 200
    And the response should contain:
      """
      {
        "loanId": "LOAN12345",
        "prepaymentOptions": {
          "fullPrepayment": {
            "available": true,
            "totalPayoffAmount": 45000.00
          },
          "partialPrepayment": {
            "available": true,
            "minimumAmount": 1000.00,
            "maximumAmount": 44000.00
          }
        }
      }
      """

  Scenario: Prepayment Simulation for Partial Payment
    Given a customer has an active loan with outstanding principal of 50000.00
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayment-simulation"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 5000.00
      }
      """
    Then the response status should be 200
    And the response should contain "interestSavings"
    And the response should contain "newEmiAmount"
    And the response should contain "tenureReduction"
    And the response should contain "prepaymentPenalty"

  Scenario: Prepayment Simulation for Full Payment
    Given a customer has an active loan account "LOAN12345"
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayment-simulation"
    With request body:
      """
      {
        "prepaymentType": "full"
      }
      """
    Then the response status should be 200
    And the response should contain:
      """
      {
        "totalPayoffAmount": 45000.00,
        "outstandingPrincipal": 43500.00,
        "accruedInterest": 1200.00,
        "prepaymentPenalty": 300.00
      }
      """

  Scenario: Initiate Partial Prepayment Transaction
    Given a customer has sufficient funds in their linked account
    And the loan "LOAN12345" is eligible for prepayment
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayments"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 3000.00,
        "paymentMethod": "ONLINE_BANKING",
        "sourceAccountId": "ACC98765"
      }
      """
    Then the response status should be 201
    And the response should contain "transactionId"
    And the response should contain "confirmationNumber"
    And the response should contain "status": "COMPLETED"

  Scenario: Automatic Prepayment Penalty Calculation for Fixed Rate Loan
    Given a customer has a fixed-rate loan "LOAN12345" with penalty terms defined
    When I send a POST request to "/api/v1/loans/LOAN12345/penalty-calculation"
    With request body:
      """
      {
        "prepaymentAmount": 10000.00,
        "loanType": "FIXED_RATE"
      }
      """
    Then the response status should be 200
    And the response should contain "penaltyAmount"
    And the response should contain "penaltyPercentage"
    And the response should contain "calculationBasis"
    And the penalty amount should be calculated based on loan terms and regulations

  Scenario: View Updated Loan Schedule After Prepayment
    Given a partial prepayment of 5000.00 has been completed for loan "LOAN12345"
    When I send a GET request to "/api/v1/loans/LOAN12345/amortization-schedule"
    Then the response status should be 200
    And the response should contain updated principal balance
    And the response should contain recalculated EMI or tenure
    And the response should show payment schedule starting from next due date

  Scenario: Bank Staff Account Lookup
    Given I have bank staff authorization with appropriate permissions
    When I send a GET request to "/api/v1/staff/customers/search"
    With query parameters:
      """
      customerId=CUST001&loanAccountNumber=LOAN12345
      """
    Then the response status should be 200
    And the response should contain complete loan details
    And the response should contain outstanding balance
    And the response should contain payment history
    And the response should contain prepayment options

  Scenario: Manual Prepayment Entry by Bank Staff
    Given I have bank staff authorization
    And customer loan account "LOAN12345" is located
    When I send a POST request to "/api/v1/staff/loans/LOAN12345/manual-prepayment"
    With request body:
      """
      {
        "prepaymentAmount": 2500.00,
        "paymentMethod": "CHECK",
        "transactionReference": "CHK789456",
        "staffId": "STAFF001",
        "receiptDate": "2024-01-15"
      }
      """
    Then the response status should be 201
    And the response should contain transaction record with audit trail
    And the loan balance should be updated
    And applicable charges should be calculated and applied

  Scenario: Prepayment History Tracking
    Given loan account "LOAN12345" has multiple prepayment transactions
    When I send a GET request to "/api/v1/loans/LOAN12345/prepayment-history"
    With query parameters:
      """
      fromDate=2023-01-01&toDate=2024-01-31&pageSize=10&pageNumber=1
      """
    Then the response status should be 200
    And the response should contain chronological list of prepayment transactions
    And each transaction should include date, amount, penalties, and reference
    And the response should support pagination

  Scenario: Rule Engine - Prepayment Eligibility Check
    Given the system has configured prepayment rules for different loan types
    When I send a GET request to "/api/v1/loans/LOAN12345/prepayment-eligibility"
    Then the response status should be 200
    And the response should contain:
      """
      {
        "eligible": true,
        "loanType": "FLOATING_RATE",
        "loanAge": 24,
        "lockInPeriod": false,
        "restrictions": [],
        "allowedPrepaymentTypes": ["partial", "full"]
      }
      """

  Scenario: Rule Engine - Prepayment Restriction for Lock-in Period
    Given a newly originated loan "LOAN54321" within lock-in period
    When I send a GET request to "/api/v1/loans/LOAN54321/prepayment-eligibility"
    Then the response status should be 200
    And the response should contain:
      """
      {
        "eligible": false,
        "reason": "LOCK_IN_PERIOD_ACTIVE",
        "lockInExpiryDate": "2024-06-15",
        "message": "Prepayment not allowed during lock-in period"
      }
      """

  Scenario: Principal Balance Reduction Accuracy
    Given loan "LOAN12345" has outstanding principal balance of 40000.00
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayments"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 8000.00,
        "paymentMethod": "ONLINE_BANKING"
      }
      """
    Then the response status should be 201
    And I send a GET request to "/api/v1/loans/LOAN12345/balance"
    Then the response status should be 200
    And the outstanding principal should be reduced accurately
    And interest calculations should be updated based on new balance

  Scenario: Amortization Schedule Recalculation with Tenure Reduction
    Given a partial prepayment has been completed for loan "LOAN12345"
    When I send a PUT request to "/api/v1/loans/LOAN12345/recalculate-schedule"
    With request body:
      """
      {
        "recalculationOption": "REDUCE_TENURE",
        "keepSameEmi": true
      }
      """
    Then the response status should be 200
    And the response should contain new amortization schedule
    And the tenure should be reduced while maintaining same EMI
    And mathematical accuracy should be verified

  Scenario: Performance Test - Prepayment Processing Speed
    Given the system is under normal operational load
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayment-simulation"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 5000.00
      }
      """
    Then the response status should be 200
    And the response time should be less than 5000 milliseconds
    And the simulation results should be displayed correctly

  Scenario: Security - Data Encryption Verification
    Given I attempt to access prepayment API without proper authentication
    When I send a GET request to "/api/v1/loans/LOAN12345/prepayment-options"
    Without authorization header
    Then the response status should be 401
    And the response should contain "Unauthorized access"
    And sensitive data should not be exposed in error messages

  Scenario: Security - Invalid Authentication Token
    Given I have an invalid or expired authentication token
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayments"
    With authorization header "Bearer invalid_token_123"
    And request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 1000.00
      }
      """
    Then the response status should be 401
    And the response should contain error message about invalid token

  Scenario: Data Integrity and Audit Trail Verification
    Given I process a prepayment transaction
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayments"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 2000.00,
        "paymentMethod": "ONLINE_BANKING"
      }
      """
    Then the response status should be 201
    And I send a GET request to "/api/v1/loans/LOAN12345/audit-trail"
    Then the response status should be 200
    And the audit trail should contain complete transaction details
    And data consistency should be maintained across all system components

  Scenario: Regulatory Compliance - Disclosure Requirements
    Given the system is configured with current regulatory requirements
    When I send a GET request to "/api/v1/loans/LOAN12345/prepayment-disclosures"
    Then the response status should be 200
    And the response should contain complete fee disclosure
    And regulatory warnings should be included
    And all applicable prepayment terms should be clearly stated

  Scenario: Error Handling - Invalid Prepayment Amount
    Given a customer attempts prepayment with invalid amount
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayments"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": -1000.00,
        "paymentMethod": "ONLINE_BANKING"
      }
      """
    Then the response status should be 400
    And the response should contain:
      """
      {
        "error": "INVALID_AMOUNT",
        "message": "Prepayment amount must be positive and within allowed limits"
      }
      """

  Scenario: Error Handling - Insufficient Account Balance
    Given a customer has insufficient funds in their linked account
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayments"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 50000.00,
        "paymentMethod": "ONLINE_BANKING",
        "sourceAccountId": "ACC98765"
      }
      """
    Then the response status should be 400
    And the response should contain:
      """
      {
        "error": "INSUFFICIENT_FUNDS",
        "message": "Insufficient balance in source account"
      }
      """

  Scenario: Error Handling - Loan Not Found
    Given a non-existent loan account number
    When I send a GET request to "/api/v1/loans/INVALID123/prepayment-options"
    Then the response status should be 404
    And the response should contain:
      """
      {
        "error": "LOAN_NOT_FOUND",
        "message": "Loan account not found"
      }
      """

  Scenario: Scalability Test - Concurrent Prepayment Requests
    Given multiple concurrent users attempt prepayment operations
    When I send 100 concurrent POST requests to "/api/v1/loans/LOAN12345/prepayment-simulation"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 1000.00
      }
      """
    Then all responses should have status 200
    And response times should remain within acceptable limits
    And system should handle concurrent requests without data corruption

  Scenario: Integration Test - Core Banking System Update
    Given a prepayment transaction is processed successfully
    When I send a POST request to "/api/v1/loans/LOAN12345/prepayments"
    With request body:
      """
      {
        "prepaymentType": "partial",
        "prepaymentAmount": 3000.00,
        "paymentMethod": "ONLINE_BANKING"
      }
      """
    Then the response status should be 201
    And the core banking system should be updated with transaction details
    And account balances should be synchronized across all systems
    And transaction should appear in customer's account statement
