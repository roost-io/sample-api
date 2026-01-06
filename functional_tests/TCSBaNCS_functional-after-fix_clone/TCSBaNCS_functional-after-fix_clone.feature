Feature: Secure Trading Platform - E2E Access, Trading, Transfers, Reconciliation, Fees, and Audit

  # Shared setup for both API and UI tests
  Background:
    Given the API base URL is set from environment 'BASE_URL'
    And the default headers include 'Content-Type: application/json'
    And the authorization token is available in environment 'AUTH_TOKEN'
    And the browser is launched with default locale 'en-US'

  # UI Tests
  @ui @security @sso @mfa @rbac
  Scenario Outline: Agent SSO login with MFA, language switch, RBAC menu enforcement and UI masking
    Given I am on the Call Center login page
    When I select language '<language>'
    And I start SSO login and complete MFA with a valid OTP
    Then I should see the home page with role-based menus visible and restricted tiles hidden
    And I should see all masked fields per policy on the screen
    And the web access log should contain a GET to the login URL without PII
    And the IdP audit should show an AuthnRequest and successful MFA with a correlationId
    And the backend audit should contain 'login_success' and a USER_SESSION row with expiry

    Examples:
      | language |
      | EN       |
      | HE       |

  @ui @security @session
  Scenario: Idle timeout redirects to login and expired token reuse is denied
    Given I am logged in as Agent via SSO with MFA
    And I remain idle for 15 minutes
    When I click any navigation item after idle timeout
    Then I should be redirected to the login page
    And the session store should show expiry and an 'idle_timeout' audit event
    When I open a bookmarked deep link using the expired token
    Then I should see a generic access denied error without stack trace or PII
    And the gateway logs should show a 401 with a correlationId and no sensitive details

  @ui @security @lockout
  Scenario: Account lockout after 5 failed password attempts shows generic message and audits
    Given I am on the Call Center login page
    When I enter an invalid password 5 times
    Then I should see a generic lockout message without reason codes
    And the IdP audit should show 'account_lockout'
    And a security event should be raised for SOC monitoring

  # API Tests
  @api @rbac
  Scenario Outline: RBAC menu API returns allowed tiles by role
    Given the authorization token is set for role '<role>'
    When I send a GET request to '/menu'
    Then the response status should be 200
    And the response should contain '<allowedTile>'
    And the response should not contain '<restrictedTile>'

    Examples:
      | role       | allowedTile     | restrictedTile  |
      | Agent      | trading_tiles   | admin_console   |
      | Supervisor | auth_queue      | user_mgmt_write |

  # API Tests - Outside Bank Security Transfer with dual approvals and file-based lifecycle
  @api @transfers @maker_checker @tase @idempotency
  Scenario: Outside Bank transfer - create, dual approvals, File 15/1051/1052 processing and duplicate SA suppression
    Given the authorization token is set
    When I send a POST request to '/transfer/create' with payload
      """
      {
        "portfolioId": "PORT001",
        "securities": [
          {"instrumentId": "TASE:AAA", "quantity": 10.50},
          {"instrumentId": "TASE:BBB", "quantity": 0.25}
        ],
        "beneficiary": {
          "type": "outside_bank",
          "bankCode": "012",
          "branchCode": "034",
          "accountNo": "12345678",
          "sameEntity": false
        },
        "case": {"code": "REL", "subCase": "SIB_SPOUSE"}
      }
      """
    Then the response status should be 201
    And the response should contain 'orderId'
    And the database 'SEC_TRANSFER_ORDER' should have status 'U' for the created order
    When I send a POST request to '/authorization/assign' with payload
      """
      { "orderId": "<created.orderId>", "assignee": "checker1" }
      """
    Then the response status should be 200
    When I send a POST request to '/authorization/approve' with payload
      """
      { "orderId": "<created.orderId>", "level": 1, "remarks": "L1 OK" }
      """
    Then the response status should be 200
    When I send a POST request to '/authorization/approve' with payload
      """
      { "orderId": "<created.orderId>", "level": 2, "remarks": "L2 OK" }
      """
    Then the response status should be 200
    And the AUTH_QUEUE should be closed for '<created.orderId>'
    When I send a POST request to '/files/15/send' with payload
      """
      { "businessDate": "2025-01-15", "orders": ["<created.orderId>"] }
      """
    Then the response status should be 202
    And the audit log should contain 'file15_sent' for '<created.orderId>'
    When I send a POST request to '/files/1051/ingest' with payload
      """
      { "fileName": "1051_20250115.dat", "checksum": "abc123", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    When I send a POST request to '/files/1052/ingest' with payload
      """
      { "fileName": "1052_20250116.dat", "checksum": "def456", "businessDate": "2025-01-16" }
      """
    Then the response status should be 202
    And a 'SETTLEMENT_ADVICE' should be created and matched to the open delivery
    When I re-ingest the same 1052 file with payload
      """
      { "fileName": "1052_20250116.dat", "checksum": "def456", "businessDate": "2025-01-16" }
      """
    Then the response status should be 200
    And the audit log should contain 'duplicate_sa_suppressed' for '<created.orderId>'
    And the UI Security Transfer History should show status 'Settled' and reconciliation 'Reconciled'

  # UI Tests - Equity Order validations
  @ui @orders @security
  Scenario Outline: Equity Buy - self-transaction prevention and maker limit exceeded authorization path
    Given I am in Order Entry for customer portfolio 'PORT001'
    When I enter side '<side>' for symbol '<symbol>' with quantity '<qty>' at price '<price>' and click Place Order
    Then I should see '<expectedMessage>'
    And the order status should be '<expectedStatus>'
    And the audit trail should include '<expectedAudit>'

    Examples:
      | side | symbol | qty  | price  | expectedMessage                              | expectedStatus        | expectedAudit                    |
      | Buy  | AAA    | 100  | 100.00 | Self-Transactions are not allowed in TASE    | Not Placed            | validation_blocked(self_txn)     |
      | Buy  | CCC    | 2000 | 250.00 | 610070 - Maker Limit Exceeded - Authorization Required | U - Authorization Pending | auth_requested(610070)         |

  # API Tests - Foreign SELL broker average price restatement and idempotency
  @api @foreign @fees @idempotency
  Scenario: Foreign SELL restated to average price at EOD with SEC/TAF and duplicate broker file suppression
    Given the authorization token is set
    When I send a POST request to '/order/place' with payload
      """
      { "portfolioId": "PORTFX1", "instrumentId": "NASDAQ:XYZ", "side": "Sell", "quantity": 120, "price": 10.00, "orderType": "Limit" }
      """
    Then the response status should be 201
    When I send a POST request to '/order/confirm' with payload
      """
      { "orderId": "<created.orderId>" }
      """
    Then the response status should be 200
    And DEALS should show partial executions for '<created.orderId>'
    When I send a POST request to '/files/broker/ingest' with payload
      """
      { "fileName": "broker_avg_20250115.csv", "checksum": "beef00", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    And the audit log should contain 'broker_avg_applied' for '<created.orderId>'
    And DEALS should contain one averaged deal with tags 'Comm','SEC','TAF'
    When I re-ingest the same broker file with payload
      """
      { "fileName": "broker_avg_20250115.csv", "checksum": "beef00", "businessDate": "2025-01-15" }
      """
    Then the response status should be 200
    And the audit log should contain 'duplicate_ingest_suppressed' for 'broker_avg_20250115.csv'

  # API Tests - Mutual Funds cut-off and price correction (auto and manual)
  @api @mutualfunds
  Scenario Outline: MF purchase lifecycle with auto price correction and after cut-off offline handling
    Given the authorization token is set
    When I send a POST request to '/mf/order/place' with payload
      """
      { "portfolioId": "PORTMF1", "fundSymbol": "MF:ABC", "action": "Purchase", "units": 100.000, "requestTime": "<requestTime>" }
      """
    Then the response status should be 201
    And the ORDERS row should have status '<expectedInitialStatus>'
    When I send a POST request to '/files/1051/ingest' with payload
      """
      { "fileName": "1051_MF_20250115.dat", "checksum": "1a2b3c", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    And allocations should be posted at NAV(T) if applicable
    When I send a POST request to '/files/1051/ingest' with payload
      """
      { "fileName": "1051_MF_CORR_20250116.dat", "checksum": "4d5e6f", "businessDate": "2025-01-16", "correction": true }
      """
    Then the response status should be 202
    And the audit log should contain '<expectedCorrectionAudit>'

    Examples:
      | requestTime        | expectedInitialStatus | expectedCorrectionAudit     |
      | 2025-01-15T15:30Z  | Pending/Transit       | mf_price_auto_corrected     |
      | 2025-01-15T17:00Z  | Offline/Pending Next  | mf_price_auto_corrected     |

  # UI Tests - Manual Matching for 1052 with tolerance and instrument enforcement
  @ui @recon @manualMatch
  Scenario Outline: Manual match passes within tolerance and blocks on instrument mismatch or tolerance exceed
    Given I open the Manual Matching screen
    When I select Open Delivery '<odRef>' and Settlement Advice '<saRef>' and click Match
    Then I should see '<expectedResult>'
    And the database should reflect '<expectedDbState>'

    Examples:
      | odRef     | saRef     | expectedResult                       | expectedDbState                    |
      | OD-1001   | SA-1001   | Match successful and nostro posted   | OPEN_DELIVERY/SA marked Matched    |
      | OD-2002   | SA-3003   | Instrument id mandatory error        | No DB changes                      |
      | OD-4004   | SA-4004   | Amount difference exceeds tolerance  | No match; specific error displayed |

  # UI Tests - Tax Simulation and Sell from results
  @ui @tax @matrix
  Scenario Outline: Tax Simulation returns results and optional Sell places an order; errors are secure
    Given I am in Tax Simulation for portfolio 'PORT001'
    When I simulate for symbol '<symbol>' with quantity '<qty>' and price '<simPrice>'
    Then I should see tax results with totals and rounding half-even
    And the audit should include 'tax_simulation_requested'
    When I click Sell on the simulation line and confirm
    Then the order should be created with source 'taxsim' or show '<expectedError>'

    Examples:
      | symbol | qty    | simPrice | expectedError                         |
      | AAA    | 10.000 | 100.12   |                                       |
      | BBB    | 9999   | 50.0000  | Quantity exceeds available validation |

  # UI Tests - Within Bank transfer with percent split and Same Entity logic
  @ui @transfers
  Scenario Outline: Within Bank transfer - multiple beneficiaries percent split validation and settlement
    Given I open Security Transfer and select two symbols with fractional quantities
    When I choose Within Bank, case 'Transfer between relatives', add two beneficiaries with percent split '<p1>' and '<p2>'
    And I click Verify, Preview and Release
    Then I should see '<expectedMessage>'
    And the order status should be '<expectedStatus>'

    Examples:
      | p1 | p2 | expectedMessage                                   | expectedStatus |
      | 50 | 50 | Authorization required popup and assign to checker | U - Authorization Required |
      | 60 | 40 | Percent split not equal to 100                     | Not Released   |

  # UI Tests - ETF path alert enforcement for Equity vs Funds lifecycles
  @ui @etf @fees
  Scenario Outline: ETF path alert forces selection; Equity and Funds paths diverge on fees and lifecycle
    Given I open the ETF List and search for symbol '<etf>'
    When I click an order link and the ETF Order Panel Alert is shown
    And I choose '<path>' path and place the order
    Then I should see preview with '<expectedFeeType>'
    And the lifecycle should be '<expectedLifecycle>'

    Examples:
      | etf  | path    | expectedFeeType | expectedLifecycle                        |
      | ETF1 | Equity  | ST Commission   | T trade -> Executed -> Reconciled (1051) |
      | ETF1 | Funds   | MF commission   | Allocated (1051) -> Settled (1052)       |

  @ui @etf @security
  Scenario: ETF path alert cannot be bypassed via deep link
    Given I previously chose the Funds path for an ETF
    When I attempt to open Equity Order Entry via deep link
    Then I should be re-prompted with the ETF Order Panel Alert
    And the gateway should log a 403 validation without stack trace

  # API Tests - Extranet off-floor trade capture and reconciliation
  @api @extranet @recon @idempotency
  Scenario: Extranet trade - blocks, 1051 mismatch, BO capture, block release, 1052 settlement and duplicate suppression
    Given the authorization token is set
    When I send a POST request to '/blocks/create' with payload
      """
      { "portfolioId": "PORT001", "type": "cash", "amount": 100000.00, "reason": "Extranet BUY estimate" }
      """
    Then the response status should be 201
    When I send a POST request to '/recon/ingest1051' with payload
      """
      { "fileName": "1051_20250115.dat", "checksum": "aa11", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    And the audit log should contain 'recon_mismatch_1051'
    When I send a POST request to '/bo/trade/capture' with payload
      """
      { "portfolioId": "PORT001", "instrumentId": "TASE:ZZZ", "side": "Buy", "quantity": 1000, "price": 95.00, "category": "EXTRANET" }
      """
    Then the response status should be 201
    When I send a POST request to '/files/1052/ingest' with payload
      """
      { "fileName": "1052_20250116.dat", "checksum": "bb22", "businessDate": "2025-01-16" }
      """
    Then the response status should be 202
    And settlement postings should be created and blocks released
    When I re-ingest '/files/1052/ingest' with the same payload
    Then the response status should be 200
    And the audit log should contain 'duplicate_sa_suppressed'

  # API Tests - Post-execution amendment requiring two approvals
  @api @amendment @maker_checker
  Scenario: Executed order amendment - dual approvals, reversal and reposting with correction portfolio
    Given the authorization token is set
    When I send a POST request to '/amendment/create' with payload
      """
      { "orderId": "ORD-EXEC-1001", "amendType": "Non-Derivative", "fields": {"price": 101.25, "portfolioId": "CORR-PORT"}, "remarks": "Correct price and move quantity" }
      """
    Then the response status should be 201
    And an AUTH_QUEUE entry should exist for 'ORD-EXEC-1001'
    When I send a POST request to '/authorization/approve' with payload
      """
      { "refId": "<created.amendmentId>", "level": 1, "remarks": "L1 OK" }
      """
    Then the response status should be 200
    When I send a POST request to '/authorization/approve' with payload
      """
      { "refId": "<created.amendmentId>", "level": 2, "remarks": "L2 OK" }
      """
    Then the response status should be 200
    And MOVEMENTS should include reversal and corrected postings
    And AUDIT_LOG should contain 'amendment_applied'

  # API Tests - Custody fee accrual daily and quarterly caps/leap-year
  @api @fees @custody
  Scenario Outline: Custody fee daily accrual and quarterly posting with exemptions and caps
    Given the authorization token is set
    When I send a POST request to '/fees/custody/runDaily' with payload
      """
      { "asOfDate": "<asOfDate>", "simulate": false }
      """
    Then the response status should be 202
    And AUDIT_LOG should contain '<expectedDailyAudit>'
    When I send a POST request to '/fees/custody/runQuarter' with payload
      """
      { "quarterEnd": "<quarterEnd>" }
      """
    Then the response status should be 202
    And MOVEMENTS should show a single consolidated debit with caps applied '<capApplied>'

    Examples:
      | asOfDate    | quarterEnd   | expectedDailyAudit        | capApplied |
      | 2024-02-29  | 2024-03-31   | custody_fee_accrued       | false      |
      | 2025-06-15  | 2025-06-30   | custody_fee_accrued       | true       |

  # UI + API Tests - Market data entitlements and abuse prevention
  @ui @entitlements @marketdata
  Scenario Outline: Market data entitlement enforcement and indicators per agent profile
    Given I am logged into the Call Center as '<agentProfile>'
    When I open '<widget>'
    Then I should see '<indicator>'
    And unauthorized features should show a secure generic message

    Examples:
      | agentProfile | widget          | indicator                       |
      | Agent A      | Market Watch    | Prices are delayed for 20 minutes |
      | Agent A      | Index Watch     | Live                            |
      | Agent B      | Get Quote       | Access denied or delayed-only   |

  @api @entitlements @security
  Scenario: Attempt to force live market data via API is blocked and audited
    Given the authorization token is set for role 'Agent B'
    When I send a GET request to '/md/quote?symbol=TASE:AAA&live=true'
    Then the response status should be 403
    And the audit log should contain 'md_access_denied' with scope_mismatch

  # API Tests - Position reconciliation 1053/871, repair, duplicate suppression; auditor read-only
  @api @recon @positions @idempotency
  Scenario: Position recon detects, ages, repairs; duplicate file ingestion suppressed; auditor read-only enforced
    Given the authorization token is set
    When I send a POST request to '/files/1053/ingest' with payload
      """
      { "fileName": "1053_20250115.dat", "checksum": "c1", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    When I send a POST request to '/files/871/ingest' with payload
      """
      { "fileName": "871_20250115.dat", "checksum": "c2", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    When I send a POST request to '/recon/positions/run' with payload
      """
      { "asOfDate": "2025-01-15" }
      """
    Then the response status should be 202
    And a recon exception should be created for instrument with drift 0.001
    When I post a position adjustment to repair the drift
    Then the next run should move the item to Reconciled and retain exception history
    When I re-ingest '1053_20250115.dat' and '871_20250115.dat'
    Then duplicates should be suppressed with 'duplicate_ingest_suppressed' audit
    When an Auditor attempts a repair action via '/recon/positions/run'
    Then the response status should be 403 and RBAC_DENIED should be logged

  # API Tests - Net Settlement File 32 and Fee 1091 ingestion and recon with config toggle
  @api @recon @fees @file32 @1091 @ctrml
  Scenario Outline: File 32 and 1091 ingestion, reconciliation or extract, duplicate suppression and malformed alert
    Given the authorization token is set
    When I send a POST request to '/files/32/ingest' with payload
      """
      { "fileName": "32_20250115_D.dat", "checksum": "d1", "businessDate": "2025-01-15", "recordType": "D" }
      """
    Then the response status should be 202
    When I send a POST request to '/files/1091/ingest' with payload
      """
      { "fileName": "1091_20250115.dat", "checksum": "d2", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    When I send a POST request to '/recon/fees/run' with payload
      """
      { "businessDate": "2025-01-15", "taseFeeSetup": "<setup>" }
      """
    Then the response status should be 202
    And the system should '<expectedOutcome>'
    When I re-ingest the same '1091_20250115.dat' and '32_20250115_D.dat'
    Then duplicate_file_suppressed should be audited
    When I ingest a malformed 1091 with bad length
    Then CTRLM should alert and the file should be rejected without DB writes

    Examples:
      | setup | expectedOutcome                                           |
      | on    | reconcile fees and produce difference report              |
      | off   | generate CSV extract without automated match              |

  # API Tests - ADR/GDR dual-leg conversion with linkage and settlement
  @api @delivery @adr_gdr @maker_checker
  Scenario: ADR/GDR conversion legs linked by External Reference 2 and settled via 1052
    Given the authorization token is set
    When I send a POST request to '/delivery/create' with payload
      """
      { "type": "DeliveryOut", "deliveryKind": "LocalToADR", "portfolioId": "PORT001", "instrumentId": "TASE:AAA", "quantity": 100.000, "externalRef2": "LINK-ADR-001" }
      """
    Then the response status should be 201
    When I send a POST request to '/delivery/create' with payload
      """
      { "type": "DeliveryIn", "deliveryKind": "ADRToLocal", "portfolioId": "PORT001", "instrumentId": "ADR:AAA", "quantity": 100.000, "externalRef2": "LINK-ADR-001" }
      """
    Then the response status should be 201
    When I send a POST request to '/authorization/approve' with payload
      """
      { "refId": "<created.deliveryOutId>", "level": 1 }
      """
    Then the response status should be 200
    When I send a POST request to '/authorization/approve' with payload
      """
      { "refId": "<created.deliveryInId>", "level": 1 }
      """
    Then the response status should be 200
    When I send a POST request to '/files/1052/ingest' with payload
      """
      { "fileName": "1052_20250116.dat", "checksum": "ee55", "businessDate": "2025-01-16" }
      """
    Then the response status should be 202
    And both OPEN_DELIVERY rows should be matched and settled with nostro postings
    When I re-ingest the same 1052
    Then the audit should contain 'duplicate_sa_suppressed'
    And LOTS_UPDATE should be produced for the conversion

  # API Tests - Outside Bank transfer (Tax Event) with zero-cost receiver lots
  @api @transfers @tax
  Scenario: Outside Bank transfer with 'Transfer without Identification' tax event and zero-cost lots
    Given the authorization token is set
    When I send a POST request to '/transfer/create' with payload
      """
      {
        "portfolioId": "PORT001",
        "securities": [{"instrumentId": "TASE:AAA", "quantity": 10.25}],
        "beneficiary": {"type": "outside_bank", "bankCode": "012", "branchCode": "034", "accountNo": "12345678", "sameEntity": false},
        "case": {"code": "TAX_EVENT", "label": "Transfer without Identification"}
      }
      """
    Then the response status should be 201
    When I send a POST request to '/authorization/approve' with payload
      """
      { "orderId": "<created.orderId>", "level": 1 }
      """
    Then the response status should be 200
    When I send a POST request to '/files/15/send' with payload
      """
      { "businessDate": "2025-01-15", "orders": ["<created.orderId>"] }
      """
    Then the response status should be 202
    When I send a POST request to '/files/1051/ingest' with payload
      """
      { "fileName": "1051_20250115.dat", "checksum": "ff66", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    When I send a POST request to '/files/1052/ingest' with payload
      """
      { "fileName": "1052_20250116.dat", "checksum": "gg77", "businessDate": "2025-01-16" }
      """
    Then the response status should be 202
    When I send a POST request to '/eod/tax/postings' with payload
      """
      { "businessDate": "2025-01-16", "orderId": "<created.orderId>" }
      """
    Then the response status should be 202
    And MOVEMENTS should include tax postings and LOTS_UPDATE should show zero cost for receiver with taxIdentifier=2

  # UI Tests - POA restriction requires independent approval
  @ui @orders @poa @maker_checker
  Scenario: POA maker requires supervisor approval before execution
    Given I am logged in as an Agent who is POA on the target account
    And I open Order Entry and create a small BUY within maker limits
    When I click Place Order
    Then I should see a message 'Order requires authorization'
    And the order status should be 'U - Authorization Pending'
    And after a non-POA supervisor approves, the order should execute and reconcile (1051)
    And the audit should include 'poa_validation_blocked' and 'supervisor_approved'

  # UI Tests - Customer authentication across service modes and throttling
  @ui @auth @masking @throttle
  Scenario Outline: Customer authentication for multiple service modes and invalid/throttled attempts
    Given I am on the Customer Authentication screen
    When I select Service Mode '<serviceMode>' and Identification Type '<idType>' and enter '<idValue>'
    And I click Authenticate
    Then I should see '<expectedOutcome>'
    And masking should be applied to portfolio references
    And the audit should include '<expectedAudit>'

    Examples:
      | serviceMode | idType      | idValue      | expectedOutcome          | expectedAudit               |
      | Phone       | National ID | 123456789    | Portfolio List displayed | customer_lookup success     |
      | Fax         | Passport    | A1234567     | Portfolio List displayed | customer_lookup success     |
      | Phone       | National ID | 12X!         | Validation error shown   | customer_lookup failure     |

  @ui @auth @throttle
  Scenario: Throttle after 3 invalid authentication attempts
    Given I am on the Customer Authentication screen
    When I attempt invalid authentication 3 times within 10 minutes
    Then I should see a generic throttling message
    And the audit should include 'lookup_throttled'

  # API + UI Tests - Third Party Transfer (BO-only) with single-level approval and reporting
  @ui @transfers @rbac
  Scenario: Call Center denies Third Party Transfer initiation for foreign holdings (BO-only)
    Given I am in Security Transfer for a foreign holding
    When I choose Outside Bank and Transfer Case 'Third Party Transfer'
    Then I should see a message 'Third-party transfer handled by Back Office'
    And creation should be denied per RBAC and audited

  @api @transfers @thirdparty @maker_checker
  Scenario: BO creates Third Party Delivery Out/In, approves and settles without TASE files; report generated
    Given the authorization token is set
    When I send a POST request to '/delivery/create' with payload
      """
      { "type": "DeliveryOut", "deliveryKind": "ThirdParty", "portfolioId": "PORTFX1", "instrumentId": "NYSE:ABC", "quantity": 250.75, "custodianCode": "CUSTX" }
      """
    Then the response status should be 201
    When I send a POST request to '/authorization/approve' with payload
      """
      { "refId": "<created.deliveryOutId>", "level": 1 }
      """
    Then the response status should be 200
    When I send a POST request to '/settlement/run' with payload
      """
      { "asOfDate": "2025-01-15", "mode": "third_party" }
      """
    Then the response status should be 202
    And MOVEMENTS and POSITION should be updated without any 1051/1052
    When I send a POST request to '/reports/export' with payload
      """
      { "reportId": "ThirdPartyTransfer", "businessDate": "2025-01-15" }
      """
    Then the response status should be 200
    And REPORT_ARCHIVE should contain the generated report

  # API Tests - Fractional residual transit deal creation and 1052-driven settlement
  @api @fractional @batch @idempotency
  Scenario: Fractional full-sell transit deal created at EOD and settled via 1052; duplicate SA suppressed
    Given the authorization token is set
    When I send a POST request to '/batch/fraction/run' with payload
      """
      { "asOfDate": "2025-01-15" }
      """
    Then the response status should be 202
    And DEALS should contain a transit deal category 'TRANSIT' between client and fraction portfolio
    When I send a POST request to '/files/1052/ingest' with payload
      """
      { "fileName": "1052_20250116.dat", "checksum": "hh88", "businessDate": "2025-01-16" }
      """
    Then the response status should be 202
    And settlement postings should be generated for the fractional leg
    When I re-ingest the same 1052
    Then the audit should include 'duplicate_sa_suppressed'

  # API Tests - Failed/Pending trades via 1054, manual blocks, cancellation, alerts and idempotency
  @api @1054 @blocks @ctrml @idempotency
  Scenario: 1054 failures and pending - create blocks, cancel or settle, alert on malformed, suppress duplicates
    Given the authorization token is set
    When I send a POST request to '/files/1054/ingest' with payload
      """
      { "fileName": "1054_20250115.dat", "checksum": "ii99", "businessDate": "2025-01-15" }
      """
    Then the response status should be 202
    And RECON_STATUS should mark a BUY as Failed and a SELL as Pending
    When I send a POST request to '/blocks/create' with payload
      """
      { "portfolioId": "PORT001", "type": "custody", "instrumentId": "TASE:BUYFAIL", "quantity": 100, "reason": "1054 failed BUY" }
      """
    Then the response status should be 201
    When I send a POST request to '/orders/cancel' with payload
      """
      { "orderId": "ORD-BUY-FAIL-1", "reason": "1054 failure" }
      """
    Then the response status should be 200
    And MOVEMENTS should show block releases on cancellation
    When I re-ingest the same 1054
    Then 'duplicate_file_suppressed' should be audited
    When I ingest a malformed 1054 with bad record length
    Then CTRLM should alert and no partial writes should occur
