Feature: Capital Markets end-to-end trading, settlement, reconciliation, fees, tax and controls

  # UI Tests

  @ui @FDB-CM-022
  Scenario Outline: Pre-trade validation matrix for Stop and Stop-Limit with disclosed boundaries, calendar and jumbo approval
    Given I am logged into the Call Center and on Equity Order Entry Create for symbol '519017'
    And the market calendar shows '<market_phase>' with system time '<time>'
    When I choose order type '<order_type>' with total quantity '<total_qty>'
    And I set Quantity Type to '<qty_type>' with initial '<disclosed_initial>' and additional '<disclosed_additional>'
    And I set trigger price '<trigger_price>' and limit price '<limit_price>'
    And I tick Jumbo '<jumbo_flag>'
    And I click Place Order
    Then I should see '<expected_outcome>'
    And if a deviation warning appears I select '<deviation_decision>'
    And if authorization is required I assign to checker and it is '<auth_result>'

    Examples:
      | market_phase | time  | order_type  | total_qty | qty_type  | disclosed_initial | disclosed_additional | trigger_price | limit_price | jumbo_flag | expected_outcome                      | deviation_decision | auth_result |
      | Closed       | 16:45 | Stop        | 1000      | Disclosed | 400               | 500                  | 205.10        | 205.20      | No         | Error MarketClosed                    | N/A                | N/A         |
      | Open         | 12:10 | Stop        | 1000      | Disclosed | 400               | 500                  | 205.10        | 205.20      | No         | Error DisclosedSumMismatch            | N/A                | N/A         |
      | Open         | 12:15 | Stop-Limit  | 1000      | Regular   | 0                 | 0                    | 0.50          | 0.50        | No         | Error 31042 price out of threshold    | N/A                | N/A         |
      | Open         | 12:20 | Stop-Limit  | 1000      | Regular   | 0                 | 0                    | 205.11        | 205.20      | Yes        | Warning 610102 price deviation        | Yes                | Approved    |
      | Open         | 12:25 | Stop-Limit  | 1000      | Regular   | 0                 | 0                    | 205.11        | 205.20      | Yes        | Warning 610102 price deviation        | No                 | Rejected    |

  @ui @FDB-CM-007
  Scenario Outline: Self-transaction prevention and POA channel restriction across phases and channels
    Given there is an existing open Sell Limit order at 100.00 ILS qty 200 during '<phase>'
    And I am logged in as '<user_type>' on '<channel>'
    When I place a Buy order type '<buy_type>' at price '<buy_price>' qty 50 on the same BP and security
    Then I should see '<expected_result>'
    And no internal order id should be created when blocked

    Examples:
      | phase       | user_type     | channel  | buy_type | buy_price | expected_result                                 |
      | Continuous  | Retail        | CallCenter | Market   | 0.00      | Error Self-Transactions are not allowed in TASE |
      | Continuous  | Retail        | CallCenter | Limit    | 100.00    | Error Self-Transactions are not allowed in TASE |
      | Continuous  | Retail        | CallCenter | Limit    | 99.99     | Authorized and Placed with Market               |
      | Auction     | Retail        | CallCenter | Market   | 0.00      | Info order allowed in auction and Placed        |
      | Continuous  | POA           | Internet | Limit    | 99.50     | Error POAChannelRestricted                       |
      | Continuous  | POA           | FO       | Limit    | 99.50     | Authorized and Placed with Market               |

  @ui @FDB-CM-011
  Scenario Outline: ETF dual-path selection with alerts, fees, cut-off and idempotent settlement advice
    Given I am on the ETF List for symbol '<symbol>'
    When I choose '<path>' path and enter '<qty_or_units>' with price or NAV '<price_or_nav>'
    And I place the order handling any warning '<warning_handling>'
    And I preview and confirm the order
    Then I should see fee details reflect '<fee_profile>'
    And the order should progress to '<expected_lifecycle>'

    Examples:
      | symbol       | path    | qty_or_units | price_or_nav | warning_handling | fee_profile                          | expected_lifecycle                           |
      | KSM 2 BND1   | Equity  | 600          | 107.80       | Accept 610102    | Equity commission with min cap       | Placed -> Executed -> Settled                |
      | KSM 2 BND1   | MF      | 400          | 107.20       | Cut-off warning  | MF transaction fee and dist. flags   | Placed -> Allocated 1051 -> Settled via 1052 |

  @ui @FDB-CM-020
  Scenario Outline: Entitlements enforcement across Market Watch, Quotes, Depth and Order screens
    Given I am logged in with entitlement profile '<profile>'
    And I open Market Watch with local '<local_symbol>' and foreign '<foreign_symbol>'
    When I view quotes and attempt Level 2 depth for the foreign symbol
    Then I should see '<banner_local>' for local and '<banner_foreign>' for foreign
    And Level 2 depth access should be '<depth_access>'
    When I start an order for the foreign symbol and proceed to Preview
    Then the displayed quote should reflect '<preview_quote_mode>' and disclaimers shown

    Examples:
      | profile                          | local_symbol | foreign_symbol | banner_local | banner_foreign        | depth_access | preview_quote_mode |
      | Local live, Foreign delayed, no L2 | 519017       | VRCFD UV       | Live         | Prices are delayed    | Denied       | Delayed            |
      | Local live, Foreign live, L2      | 519017       | VRCFD UV       | Live         | Live                  | Allowed      | Live               |

  @ui @FDB-CM-028
  Scenario Outline: Makam yield calculator boundary, leap-year and error handling
    Given I am on the Makam Calculator
    When I enter Price '<price>', Days '<days>', Tax '<tax_rate>%', Buy fee '<buy_fee>%', Sell fee '<sell_fee>%', Custody fee '<custody_fee>%'
    And I submit the calculator
    Then I should see '<expected_result>'

    Examples:
      | price  | days | tax_rate | buy_fee | sell_fee | custody_fee | expected_result                                     |
      | 95.000 | 120  | 15       | 1       | 2        | 0.5         | Effective yields before/after fees within 0.01%     |
      | 95.000 | 366  | 15       | 1       | 2        | 0.5         | Info leap-year applied and yields computed          |
      | 1.00   | 1    | 0        | 0       | 0        | 0           | No overflow, yields displayed and rounded           |
      | 100.00 | 180  | 25       | 0       | 0        | 0           | Effective yield near 0; after-tax reduced           |
      | 0.50   | 120  | 15       | 1       | 2        | 0.5         | Error InvalidPriceRange                             |
      | 95.00  | 0    | 15       | 1       | 2        | 0.5         | Error InvalidDays                                   |

  @ui @FDB-CM-016
  Scenario Outline: Within bank transfer with multi-beneficiary percentages, Virtual Sell and MF restriction
    Given I open Security Transfer and Select Security for '<security_list>'
    And I set business date '<business_date_validity>'
    When I add beneficiaries '<beneficiaries>' with percentages '<percentages>' and transfer case '<transfer_case>'
    And I toggle Virtual Sell '<virtual_sell>'
    And I click Verify and then Release
    Then I should see '<expected_validation>'
    And upon authorization the order should settle at EOD without duplicates on re-run

    Examples:
      | security_list                      | business_date_validity | beneficiaries             | percentages | transfer_case               | virtual_sell | expected_validation                         |
      | TASE 570 qty 100.5; 519017 qty 50.25 | Valid                   | PortA,PortB               | 40,60       | Transfer between relatives  | No           | Error percentage not equal 100               |
      | TASE 570 qty 100.5; 519017 qty 50.25 | Valid                   | PortA,PortB               | 50,50       | Transfer between relatives  | No           | Accepted and Authorized                      |
      | TASE 570 qty 100.5                  | Valid                   | SourceOnly                | 100         | N/A                         | Yes          | Virtual Sell accepted                        |
      | Add MF 5118625                      | Valid                   | PortA (different entity)  | 100         | N/A                         | No           | Error MF cannot transfer to other entity     |

  @ui @FDB-CM-033
  Scenario Outline: Authorization workflow with pool assignment, reassignment, rejection and four-eyes
    Given I have submitted a transaction '<transaction_ref>' requiring authorization '<auth_flow>'
    When I assign it to '<assignment>' with remarks '<remarks>'
    And the assigned checker performs '<action_sequence>'
    Then the final authorization status should be '<final_status>'
    And E-Journal should show initiator, authorizer(s), remarks and timestamps

    Examples:
      | transaction_ref | auth_flow          | assignment     | remarks                    | action_sequence                         | final_status |
      | TransA          | Warning override   | Specific:Chk1  | Please approve             | Chk1 Approves                           | Approved     |
      | TransB          | Maker limit exceed | Pool           | Over limit, review         | Chk2 Rejects, Maker re-submits, Chk2 Approves | Approved     |
      | TransC          | Four-eyes          | Stage1:Chk1    | Correction portfolio used  | Chk1 Approves -> Pool:Chk2 Approves     | Approved     |
      | TransD          | Self-approval test | Specific:Maker | N/A                        | Maker Attempts Self-Approve             | Blocked      |

  @ui @FDB-CM-029
  Scenario: Portfolio fund balance formulas, valuation rounding and PII-masked export
    Given I open Fund Balance for the customer
    Then I should see Net 1000.00 ILS, Block 200.00 ILS, Receivables 100.00 ILS and OD Limit 400.00 ILS
    And Available Balance should be 1200.00 ILS, Trade Balance 1300.00 ILS and Free Balance 900.00 ILS
    When I open Portfolio Valuation Today
    Then USD holdings should be converted using USDILS close with 4 dp internal rounding and 2 dp display within 0.01 ILS tolerance
    When I switch to a prior business day
    Then historical holdings and totals should reflect that date
    And exports of Fund Balance and Valuation should mask PII

  @ui @FDB-CM-035
  Scenario: Order and trade monitoring views, filters and privacy-controlled exports
    Given I open Order Book and filter by Exchange TASE and Instrument Equity
    Then I should see pending, executed and cancelled orders with disclosed quantities where applicable
    When I open Trade Book and export to Excel
    Then portfolio and BP identifiers should be masked in the export
    When I search via Advanced Search by ISIN and place then cancel a small test order
    Then Order Book and Order History should reflect both actions
    And repeated refresh and export with same filters should yield identical row counts and totals

  @ui @FDB-CM-018
  Scenario: Tax Simulation to Sell order placement with band and deviation handling
    Given I open Tax Simulation for symbol 519017
    When I enter quantity 250 and price 205.10 and click Simulate
    Then I should see Profit/Loss, Taxable Amount, Tax Rate and Tax To Pay/Refund
    When I click Sell from Simulation and attempt to enter price 0.50
    Then I should see Error 31042 price out of threshold
    When I correct the price to 205.10, place the order and accept Warning 610102 if shown in Preview
    Then the order should be confirmed and ready for execution with audit captured

  @ui @FDB-CM-030
  Scenario Outline: Nostro cut-off enforcement and roll-forward policy
    Given I am logged in as FO Operator with Nostro profile and system time '<time>'
    When I place a Nostro buy limit order on symbol 519017 qty 5 price 205.10
    Then I should see '<expected>'
    And no open order should be present post cut-off unless roll-forward is configured

    Examples:
      | time  | expected                                  |
      | 16:40 | Authorized                                |
      | 16:46 | Error NostroCutoffExceeded                |
      | 16:46 | Info RolledToNextDay when policy enabled  |

  @ui @FDB-CM-004
  Scenario: Outside bank transfer UI validations including ex-date and MF restriction
    Given I open Security Transfer and Select Security for TASE 002810015 qty 12.0
    When I attempt to include a NASDAQ position with Outside Bank type
    Then I should see Error only TASE securities can be transferred Outside Bank
    When I set business date to a corporate action ex-date and click Verify
    Then I should see the ex-date blocking error
    When I add beneficiary bank 1245 branch 5124 and proceed to Preview then Release
    Then the transfer should be captured with audit and ready for authorization

  # API Tests

  @api @FDB-CM-001
  Scenario: Local equity buy post-trade processing with 1051 recon, 1052 idempotency, contractual settlement, GL and tax EOD
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/files/1051/load' with payload """
    {
      "fileName": "TASE1051_T.json",
      "fileHash": "abc1051hash",
      "records": [
        { "instrument":"519017","executionId":"EXEC-001","qty":120,"price":205.10,"tradeDate":"2026-01-10" }
      ]
    }
    """
    Then the response status should be 201
    And the response should contain 'loadedCount:1'
    When I send a POST request to '/api/settlement/customer/run?model=contractual' with payload """
    { "runId":"CUST-SET-001","valueDate":"2026-01-11" }
    """
    Then the response status should be 200
    And the response should contain 'posted:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    {
      "fileName": "TASE1052_Tplus1.json",
      "fileHash": "abc1052hash",
      "records": [
        { "custodian":"TASE","instrument":"519017","taseMovementId":"MV-001","eventId":"EV-001","qty":120,"price":205.10,"tradeDate":"2026-01-10","valueDate":"2026-01-11" }
      ]
    }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/files/1052/load' with payload """
    {
      "fileName": "TASE1052_Tplus1.json",
      "fileHash": "abc1052hash",
      "records": [
        { "custodian":"TASE","instrument":"519017","taseMovementId":"MV-001","eventId":"EV-001","qty":120,"price":205.10,"tradeDate":"2026-01-10","valueDate":"2026-01-11" }
      ]
    }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'
    When I send a GET request to '/api/gl/postings/query?orderId=LOCAL-BUY-001'
    Then the response status should be 200
    And the response should contain 'Customer Cash GL'
    And the response should contain 'Internal Street Payable GL'
    When I send a POST request to '/api/tax/outbound/send' with payload """
    { "batchDate":"2026-01-10","movements":[{"orderId":"LOCAL-BUY-001"}] }
    """
    Then the response status should be 200
    And the response should contain 'sent:true'

  @api @FDB-CM-031
  Scenario: 1052 manual matching with duplicate suppression, out-of-tolerance override, unmatch and re-match
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/files/1052/load' with payload """
    {
      "fileName":"1052_OD1.json",
      "fileHash":"h1052a",
      "records":[
        { "custodian":"TASE","instrument":"519017","taseMovementId":"MV-100","eventId":"EV-100","qty":200,"amount":41030.62,"tradeDate":"2026-01-10","valueDate":"2026-01-11" }
      ]
    }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/settlement/manual-match' with payload """
    {
      "openDeliveryId":"OD1",
      "adviceId":"ADV-MV-100",
      "override": { "amountToleranceOverride": true, "reason": "Price adjustment 0.62 ILS" }
    }
    """
    Then the response status should be 202
    And the response should contain 'pendingApproval:true'
    When I send a POST request to '/api/settlement/manual-match/approve' with payload """
    { "adviceId":"ADV-MV-100","approvedBy":"checker1" }
    """
    Then the response status should be 200
    And the response should contain 'matched:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    { "fileName":"1052_OD1.json","fileHash":"h1052a","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'
    When I send a POST request to '/api/settlement/unmatch' with payload """
    { "openDeliveryId":"OD1","reason":"Load corrected advice" }
    """
    Then the response status should be 200
    And the response should contain 'unmatched:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    {
      "fileName":"1052_OD1_fix.json",
      "fileHash":"h1052b",
      "records":[
        { "custodian":"TASE","instrument":"519017","taseMovementId":"MV-101","eventId":"EV-101","qty":200,"amount":41030.00,"tradeDate":"2026-01-10","valueDate":"2026-01-11" }
      ]
    }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/settlement/manual-match' with payload """
    { "openDeliveryId":"OD1","adviceId":"ADV-MV-101" }
    """
    Then the response status should be 200
    And the response should contain 'matched:true'

  @api @FDB-CM-008
  Scenario: Incoming 132 with To Be Repaired handling, authorization and idempotent reprocessing
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/files/132/load' with payload """
    {
      "fileName":"132_BOD.csv",
      "fileHash":"hash132a",
      "records":[
        { "externalRef":"REC-A","securityId":"002810015","qty":10.0,"beneficiaryPortfolio":"BP00XXX001","layers":[{"qty":5.0},{"qty":5.0}] },
        { "externalRef":"REC-B","securityId":"002810015","qty":12.0,"beneficiaryPortfolio":"PORT-NOT-FOUND","layers":[{"qty":5.0},{"qty":4.0}] }
      ]
    }
    """
    Then the response status should be 201
    And the response should contain 'authorized:1'
    And the response should contain 'toBeRepaired:1'
    When I send a PUT request to '/api/transfers/incoming/repair' with payload """
    {
      "externalRef":"REC-B",
      "beneficiaryPortfolio":"BP00XXX002",
      "layers":[{"qty":6.0},{"qty":6.0}],
      "sameEntity":true,
      "transferCase":"Relatives-Spouse-of-sister-brother"
    }
    """
    Then the response status should be 200
    And the response should contain 'repaired:true'
    When I send a POST request to '/api/transfers/incoming/authorize' with payload """
    { "externalRef":"REC-B","assignedTo":"checker1" }
    """
    Then the response status should be 200
    And the response should contain 'authorized:true'
    When I send a POST request to '/api/files/132/load' with payload """
    { "fileName":"132_BOD.csv","fileHash":"hash132a","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'

  @api @FDB-CM-009
  Scenario: Failed trades via 1054 with manual blocks, cancellation and idempotency
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/files/1054/load' with payload """
    {
      "fileName":"1054_EOD.json",
      "fileHash":"hash1054a",
      "records":[
        { "orderId":"OBUYXXX","side":"BUY","status":"FAILED" },
        { "orderId":"OSELLXXX","side":"SELL","status":"FAILED" }
      ]
    }
    """
    Then the response status should be 201
    And the response should contain 'failedCount:2'
    When I send a POST request to '/api/blocks/custody' with payload """
    { "orderId":"OBUYXXX","qty":150,"reason":"1054 failure" }
    """
    Then the response status should be 201
    And the response should contain 'blockApplied:true'
    When I send a POST request to '/api/blocks/cash' with payload """
    { "orderId":"OSELLXXX","amount":999999.99,"allowOverage":true,"reason":"1054 failure" }
    """
    Then the response status should be 201
    And the response should contain 'blockApplied:true'
    When I send a POST request to '/api/orders/cancel' with payload """
    { "orderIds":["OBUYXXX","OSELLXXX"],"reason":"Cancel after 1054 failure" }
    """
    Then the response status should be 202
    And the response should contain 'cancellationSubmitted:true'
    When I send a POST request to '/api/files/1054/load' with payload """
    { "fileName":"1054_EOD.json","fileHash":"hash1054a","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'

  @api @FDB-CM-015
  Scenario: Positions and cash reconciliation with partial/late files, duplicates, corrupted records and refunds
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/files/1053/load' with payload """
    { "fileName":"1053_partial.csv","fileHash":"h1053p","partial":true,"records":[{"security":"AAA","qty":100} ] }
    """
    Then the response status should be 202
    And the response should contain 'partial:true'
    When I send a POST request to '/api/files/1053/load' with payload """
    { "fileName":"1053_partial.csv","fileHash":"h1053p","partial":true,"records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'
    When I send a POST request to '/api/files/1053/load' with payload """
    { "fileName":"1053_full.csv","fileHash":"h1053f","partial":false,"records":[{"security":"AAA","qty":100},{"security":"BBB","qty":200}] }
    """
    Then the response status should be 201
    And the response should contain 'autoMatched:true'
    When I send a POST request to '/api/files/871/load' with payload """
    { "fileName":"871_late.csv","fileHash":"h871a","late":true,"records":[{"security":"FXY","qty":50}] }
    """
    Then the response status should be 201
    And the response should contain 'lateFile:true'
    When I send a POST request to '/api/files/1091/load' with payload """
    { "fileName":"1091_bad.csv","fileHash":"h1091bad","records":[{"security":"519017","amount":"NaN"}] }
    """
    Then the response status should be 207
    And the response should contain 'FileFormatError'
    When I send a POST request to '/api/files/1091/load' with payload """
    { "fileName":"1091_bad.csv","fileHash":"h1091bad","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'
    When I send a POST request to '/api/files/872/load' with payload """
    {
      "fileName":"872.csv",
      "fileHash":"h872a",
      "records":[{"customerRef":"CUST-XXX-01","feeType":"TAF","differenceUSD":-2.35,"symbol":"VRCFD UV"}]
    }
    """
    Then the response status should be 201
    And the response should contain 'loadedCount:1'
    When I send a POST request to '/api/refunds/create' with payload """
    { "customerRef":"CUST-XXX-01","feeType":"TAF","amountUSD":2.35,"usdils":3.7500,"reason":"Overcharge vs 872" }
    """
    Then the response status should be 201
    And the response should contain 'glPosting:created'

  @api @FDB-CM-023
  Scenario: Tax engine EOD failure, retry without duplicates and settlement-date tax posting
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/tax/outbound/send' with payload """
    { "batchDate":"2026-01-10","movements":[{"orderId":"OSELLTAXXXX"}],"simulateFailure":true }
    """
    Then the response status should be 500
    And the response should contain 'TaxOutboundFailed'
    When I send a POST request to '/api/tax/outbound/send' with payload """
    { "batchDate":"2026-01-10","movements":[{"orderId":"OSELLTAXXXX"}] }
    """
    Then the response status should be 200
    And the response should contain 'sent:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    {
      "fileName":"1052_tax.json",
      "fileHash":"h1052tax",
      "records":[{"instrument":"519017","taseMovementId":"TX-001","eventId":"TX-001","qty":220,"amount":45122.00,"tradeDate":"2026-01-10","valueDate":"2026-01-11"}]
    }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/tax/inbound/upload?type=tax' with payload """
    { "fileName":"tax_postings.csv","fileHash":"htax1","records":[{"orderId":"OSELLTAXXXX","taxILS":1234.56,"valueDate":"2026-01-11"}] }
    """
    Then the response status should be 201
    And the response should contain 'posted:true'
    When I send a POST request to '/api/tax/inbound/upload?type=counters' with payload """
    { "fileName":"counters.csv","fileHash":"hctr1","records":[{"customer":"BPXXX","pnl10d":100.12}] }
    """
    Then the response status should be 201
    And the response should contain 'loaded:true'
    When I send a POST request to '/api/tax/inbound/upload?type=counters' with payload """
    { "fileName":"counters.csv","fileHash":"hctr1","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'DuplicateInboundIgnored'

  @api @FDB-CM-024
  Scenario: Directive 414 A/B/C and TASE 814/815 generation, validation and duplicate-run suppression
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/reports/generate' with payload """
    { "period":"2025-12","type":"414A" }
    """
    Then the response status should be 201
    And the response should contain 'reportId'
    When I send a POST request to '/api/reports/generate' with payload """
    { "period":"2025-12","type":"414B" }
    """
    Then the response status should be 201
    And the response should contain 'reportId'
    When I send a POST request to '/api/reports/generate' with payload """
    { "period":"2025-12","type":"414C" }
    """
    Then the response status should be 201
    And the response should contain 'reportId'
    When I send a POST request to '/api/reports/generate' with payload """
    { "period":"2025-12","type":"814","validate":true,"injectError":true }
    """
    Then the response status should be 400
    And the response should contain 'RegFileValidationError'
    When I send a POST request to '/api/reports/generate' with payload """
    { "period":"2025-12","type":"814","validate":true }
    """
    Then the response status should be 201
    And the response should contain 'checksum'
    When I send a POST request to '/api/reports/generate' with payload """
    { "period":"2025-12","type":"814","validate":true }
    """
    Then the response status should be 200
    And the response should contain 'DuplicateRunIgnored'

  @api @FDB-CM-025
  Scenario: Accounting mapping suspense handling and re-post without duplication preserving value date
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/settlement/customer/run?model=contractual' with payload """
    { "runId":"CUST-SET-FEE","valueDate":"2026-01-11","simulateMissingFeeGL":true }
    """
    Then the response status should be 207
    And the response should contain 'MissingGLAccount'
    And the response should contain 'postedPrincipal:true'
    When I send a PUT request to '/api/accounting/rules' with payload """
    { "component":"FEE_INCOME","glAccount":"FEE-INCOME-GL","maker":"fin_maker","submitForApproval":true }
    """
    Then the response status should be 202
    And the response should contain 'pendingApproval:true'
    When I send a POST request to '/api/accounting/rules/approve' with payload """
    { "component":"FEE_INCOME","approvedBy":"fin_checker" }
    """
    Then the response status should be 200
    And the response should contain 'approved:true'
    When I send a POST request to '/api/gl/repost' with payload """
    { "batchId":"CUST-SET-FEE","reclassifyFrom":"SUSPENSE","to":"FEE-INCOME-GL" }
    """
    Then the response status should be 200
    And the response should contain 'reposted:true'
    When I send a POST request to '/api/gl/repost' with payload """
    { "batchId":"CUST-SET-FEE","reclassifyFrom":"SUSPENSE","to":"FEE-INCOME-GL" }
    """
    Then the response status should be 200
    And the response should contain 'RepostSkip'

  @api @FDB-CM-017
  Scenario Outline: Customer settlement model comparison and idempotency
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/settlement/customer/run?model=<model>' with payload """
    { "runId":"RUN-<model>-001","valueDate":"2026-01-11" }
    """
    Then the response status should be 200
    And the response should contain 'posted:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    {
      "fileName":"1052_<model>.json",
      "fileHash":"h1052<model>",
      "records":[{"instrument":"519017","taseMovementId":"MV-<model>-1","eventId":"EV-<model>-1","qty":300,"amount":63000.00,"tradeDate":"2026-01-10","valueDate":"2026-01-11"}]
    }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/settlement/customer/run?model=<model>' with payload """
    { "runId":"RUN-<model>-001","valueDate":"2026-01-11" }
    """
    Then the response status should be 200
    And the response should contain 'postedAgain:false'

    Examples:
      | model        |
      | contractual  |
      | actual       |

  @api @FDB-CM-014
  Scenario: ADR/GDR conversion two-leg settlement with linkage and idempotent advices
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/transfers/create' with payload """
    { "leg":"OUT","deliveryType":"LocalToADR","security":"LOCAL-SEC","qty":100,"externalRef2":"CONV-ADR-00045" }
    """
    Then the response status should be 201
    And the response should contain 'released:true'
    When I send a POST request to '/api/transfers/create' with payload """
    { "leg":"IN","deliveryType":"ADRToLocal","security":"ADR-SEC","qty":100,"externalRef2":"CONV-ADR-00045" }
    """
    Then the response status should be 201
    And the response should contain 'released:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    {
      "fileName":"1052_conv.json",
      "fileHash":"h1052conv",
      "records":[
        {"instrument":"ADR-SEC","taseMovementId":"C1","eventId":"C1","qty":100,"amount":0,"valueDate":"2026-01-11"},
        {"instrument":"LOCAL-SEC","taseMovementId":"C2","eventId":"C2","qty":100,"amount":0,"valueDate":"2026-01-11"}
      ]
    }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:2'
    When I send a POST request to '/api/files/1052/load' with payload """
    { "fileName":"1052_conv.json","fileHash":"h1052conv","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'
    When I send a POST request to '/api/settlement/match/batch' with payload """
    { "externalRef2":"CONV-ADR-00045","autoMatch":true }
    """
    Then the response status should be 200
    And the response should contain 'settled:true'

  @api @FDB-CM-019
  Scenario: Third-party transfer manual movement generation and idempotency
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/transfers/third-party/create' with payload """
    { "direction":"OUT","security":"US1234567890","qty":75,"externalCustodian":"CUSTOD-APEX-INTL","valueDate":"2026-01-10" }
    """
    Then the response status should be 201
    And the response should contain 'authorized:true'
    When I send a POST request to '/api/transfers/third-party/post' with payload """
    { "orderId":"TP-OUT-0001" }
    """
    Then the response status should be 200
    And the response should contain 'settled:true'
    When I send a POST request to '/api/transfers/third-party/post' with payload """
    { "orderId":"TP-OUT-0001" }
    """
    Then the response status should be 200
    And the response should contain 'duplicateSkipped:true'

  @api @FDB-CM-006
  Scenario: Security rates ingestion, invalid rows rollback, manual override approval and idempotency
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/marketdata/rates/load' with payload """
    {
      "source":"TASE",
      "fileName":"tase_close.csv",
      "fileHash":"hrates1",
      "records":[{"instrument":"519017","rateType":"CLOSE","rate":205.10}]
    }
    """
    Then the response status should be 201
    And the response should contain 'loadedCount:1'
    When I send a POST request to '/api/marketdata/rates/load' with payload """
    {
      "source":"MassUpload",
      "fileName":"mass.csv",
      "fileHash":"hrates2",
      "records":[
        {"instrument":"US1234567890","rateType":"","rate":98.7654},
        {"instrument":"519017","rateType":"CLOSE","rate":-0.01}
      ]
    }
    """
    Then the response status should be 400
    And the response should contain 'batchRolledBack:true'
    When I send a POST request to '/api/marketdata/override/submit' with payload """
    { "instrument":"519017","rateType":"CLOSE","newRate":236.00,"comment":">15% deviation" }
    """
    Then the response status should be 202
    And the response should contain 'pendingApproval:true'
    When I send a POST request to '/api/marketdata/override/approve' with payload """
    { "instrument":"519017","rateType":"CLOSE","approvedBy":"checker1" }
    """
    Then the response status should be 200
    And the response should contain 'approved:true'
    When I send a POST request to '/api/marketdata/rates/load' with payload """
    { "source":"TASE","fileName":"tase_close.csv","fileHash":"hrates1","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'

  @api @FDB-CM-010
  Scenario: Extranet off-floor trade mismatch, manual capture, block expiry and settlement
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/blocks/cash' with payload """
    { "orderCategory":"Extranet","security":"519017","qty":100,"price":210.00,"reason":"Extranet pre-block" }
    """
    Then the response status should be 201
    And the response should contain 'blockApplied:true'
    When I send a POST request to '/api/files/1051/load' with payload """
    {
      "fileName":"1051_extranet.json",
      "fileHash":"h1051ext",
      "records":[{"brokerRef":"EXT-2026-0001","instrument":"519017","qty":100,"avgPrice":210.00}]
    }
    """
    Then the response status should be 201
    And the response should contain 'mismatch:true'
    When I send a POST request to '/api/orders/manual-capture' with payload """
    {
      "brokerRef":"EXT-2026-0001",
      "instrument":"519017",
      "qty":100,
      "price":210.00,
      "orderCategory":"Extranet"
    }
    """
    Then the response status should be 201
    And the response should contain 'captured:true'
    When I send a POST request to '/api/blocks/release' with payload """
    { "reason":"Post-capture release","category":"Extranet" }
    """
    Then the response status should be 200
    And the response should contain 'released:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    { "fileName":"1052_extranet.json","fileHash":"h1052ext","records":[{"instrument":"519017","taseMovementId":"EX-1","eventId":"EX-1","qty":100,"amount":21000.00,"valueDate":"2026-01-11"}] }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/settlement/match/batch' with payload """
    { "category":"Extranet","autoMatch":true }
    """
    Then the response status should be 200
    And the response should contain 'settled:true'

  @api @FDB-CM-026
  Scenario: Foreign mutual fund redemption with T+2 settlement, price correction reversal and idempotency
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/files/1051/load' with payload """
    { "fileName":"1051_FRN_alloc.json","fileHash":"h1051frn","records":[{"fundId":"FRN-5118625","units":600,"nav":10.200,"allocationId":"ALC-1","tradeDate":"2026-01-10"}] }
    """
    Then the response status should be 201
    And the response should contain 'allocations:1'
    When I send a POST request to '/api/settlement/customer/run?model=contractual' with payload """
    { "runId":"CUST-FRN-SET","valueDate":"2026-01-12" }
    """
    Then the response status should be 200
    And the response should contain 'posted:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    { "fileName":"1052_FRN.json","fileHash":"h1052frn","records":[{"fundId":"FRN-5118625","taseMovementId":"FRN-1","eventId":"FRN-1","units":600,"amount":6120.00,"valueDate":"2026-01-12"}] }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/files/1051/load' with payload """
    { "fileName":"1051_FRN_corr.json","fileHash":"h1051frnc","records":[{"allocationId":"ALC-1","reversal":true},{"fundId":"FRN-5118625","units":600,"nav":10.160,"allocationId":"ALC-2"}] }
    """
    Then the response status should be 201
    And the response should contain 'reversed:1'
    And the response should contain 'allocations:1'
    When I send a POST request to '/api/files/1052/load' with payload """
    { "fileName":"1052_FRN_corr.json","fileHash":"h1052frnc","records":[{"taseMovementId":"FRN-1","reversal":true},{"fundId":"FRN-5118625","taseMovementId":"FRN-2","eventId":"FRN-2","units":600,"amount":6096.00,"valueDate":"2026-01-12"}] }
    """
    Then the response status should be 201
    And the response should contain 'reversals:1'
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/files/1052/load' with payload """
    { "fileName":"1052_FRN_corr.json","fileHash":"h1052frnc","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'

  @api @FDB-CM-021
  Scenario: Security product onboarding and reference data mapping with validations and idempotency
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/master/instruments/import' with payload """
    {
      "source":"TASE143",
      "fileName":"tase143.json",
      "fileHash":"h143",
      "instruments":[{"isin":"IL000MKM0001","typeCode":54,"currency":"ILS","precision":0.01}]
    }
    """
    Then the response status should be 201
    And the response should contain 'created:1'
    When I send a POST request to '/api/master/instruments/import' with payload """
    {
      "source":"Orbis",
      "fileName":"orbis.json",
      "fileHash":"horbis",
      "instruments":[{"isin":"US9999999999","typeCode":901,"currency":"USD","precision":0.0001,"poolFactor":97.345}]
    }
    """
    Then the response status should be 201
    And the response should contain 'created:1'
    When I send a POST request to '/api/master/instruments/import' with payload """
    {
      "source":"TASE143",
      "fileName":"tase143_bad.json",
      "fileHash":"h143bad",
      "instruments":[{"isin":"IL000MKM0001","typeCode":229,"currency":"ILS","precision":0.01}]
    }
    """
    Then the response status should be 400
    And the response should contain 'InvalidTypeMapping'
    When I send a POST request to '/api/master/instruments/import' with payload """
    { "source":"Orbis","fileName":"orbis.json","fileHash":"horbis","instruments":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'

  @api @FDB-CM-027
  Scenario: AML block prevents File 15 dispatch; release then 1051/1052 proceed with idempotency
    Given the API base URL is 'https://bank.example.com'
    And the authorization token is set
    When I send a POST request to '/api/transfers/outside-bank/create' with payload """
    { "orderId":"TO-AML-001","security":"002810015","qty":18.5,"bankCode":"1245","branchCode":"5124" }
    """
    Then the response status should be 201
    And the response should contain 'authorized:true'
    When I send a POST request to '/api/transfers/aml/block' with payload """
    { "orderId":"TO-AML-001","reason":"AML pending" }
    """
    Then the response status should be 200
    And the response should contain 'blocked:true'
    When I send a POST request to '/api/transfers/file15/generate' with payload """
    { "businessDate":"2026-01-11" }
    """
    Then the response status should be 200
    And the response should contain 'dispatchedCount:0'
    When I send a POST request to '/api/transfers/aml/release' with payload """
    { "orderId":"TO-AML-001","comments":"Cleared" }
    """
    Then the response status should be 200
    And the response should contain 'released:true'
    When I send a POST request to '/api/transfers/file15/generate' with payload """
    { "businessDate":"2026-01-11" }
    """
    Then the response status should be 200
    And the response should contain 'dispatchedCount:1'
    When I send a POST request to '/api/files/1051/load' with payload """
    { "fileName":"1051_TO_AML.json","fileHash":"h1051aml","records":[{"orderId":"TO-AML-001","matched":true}] }
    """
    Then the response status should be 201
    And the response should contain 'matched:true'
    When I send a POST request to '/api/files/1052/load' with payload """
    { "fileName":"1052_TO_AML.json","fileHash":"h1052aml","records":[{"orderId":"TO-AML-001","taseMovementId":"AML-1","eventId":"AML-1","qty":18.5,"amount":0,"valueDate":"2026-01-12"}] }
    """
    Then the response status should be 201
    And the response should contain 'advicesCreated:1'
    When I send a POST request to '/api/files/1052/load' with payload """
    { "fileName":"1052_TO_AML.json","fileHash":"h1052aml","records":[] }
    """
    Then the response status should be 200
    And the response should contain 'duplicateIgnored:true'
