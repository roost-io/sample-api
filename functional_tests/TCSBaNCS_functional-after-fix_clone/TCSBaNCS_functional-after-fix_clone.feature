Feature: Multi-market trading, settlement, transfers, fees, reconciliation and entitlements

  # UI Tests
  @ui @callcentre @tase @equity @buy
  Scenario Outline: Place a local TASE equity Buy via Call Centre and authorize
    Given I am logged in via SSO as 'Call Centre Agent' with entitlements for live local data
    And I have selected customer with masked ID '****' and an active portfolio with sufficient buying power
    And I am on the Order Entry (Equity) screen
    When I select exchange 'TASE' and enter symbol '<symbol>'
    And I set side 'Buy', price condition 'Limit' with price '<price>' ILS, quantity '<qty>', validity 'Good For Day'
    And I click 'Place Order'
    Then I should see pre-trade validation result '<validationOutcome>'
    And on Preview I see estimated and detailed commission
    When I tick 'I Agree' for commission and order and I click 'Confirm'
    Then the order status should be 'Authorized'
    And the Order Book should show the new order with status 'Placed with Market' or 'Authorized' as per routing
    And the audit trail should capture 'OrderId' and 'SessionId'

    Examples:
      | symbol | price  | qty  | validationOutcome     |
      | ABCD   | 105.10 | 1000 | Passed with Info/Warn |
      | ABCD   | 105.10 | 1000 | Passed                |

  # API Tests
  @api @tase @equity @buy @execution @recon @settlement @gl @tax
  Scenario Outline: TASE Buy lifecycle - executions, 1051/1052 recon, OD-SA matching under tolerance and idempotence
    Given the API base URL is '${BASE_URL}' and authorization token is set
    And a previously 'Authorized' order exists with orderId '${orderId}' for symbol 'ABCD' quantity '1000' limit '105.10' ILS
    When I send a POST request to '/api/market/executions' with payload:
      """
      {
        "orderId": "${orderId}",
        "fills": [
          { "qty": 400, "price": 104.90, "execId": "E1" },
          { "qty": 600, "price": 105.20, "execId": "E2" }
        ],
        "exchange": "TASE",
        "tradeDate": "<tradeDate>"
      }
      """
    Then the response status should be 200
    And the order status should be 'Executed' with averagePrice '105.08'
    And custody and cash blocks should be adjusted and released for executed portions
    When I send a POST request to '/api/files/ingest/1051' with payload:
      """
      {
        "businessDate": "<tradeDate>",
        "records": [
          { "symbol": "ABCD", "qty": 400, "price": 104.90, "execId": "E1" },
          { "symbol": "ABCD", "qty": 600, "price": 105.20, "execId": "E2" }
        ],
        "mode": "primary"
      }
      """
    Then the response status should be 202
    And the trade reconciliation status for order '${orderId}' should be 'Reconciled' using criteria 'Instrument,Quantity,ExecutionId,Price,TradeDate'
    When I re-send a POST request to '/api/files/ingest/1051' with the same payload
    Then the ingestion should be idempotent and no duplicate deals are created
    When I send a POST request to '/api/files/ingest/1052' with payload:
      """
      {
        "businessDate": "<settleDate>",
        "movements": [
          { "movementId": "M1", "eventId": "EV1", "symbol": "ABCD", "qty": 1000, "price": 105.08, "custodian": "LOCAL", "settlementType": "DVP", "currency": "ILS" }
        ]
      }
      """
    Then the system should create Settlement Advice and auto-match with Open Delivery within tolerance '0.50' ILS
    And OD and SA matching status should be 'Settled'
    When I run the 'Street Settlement Batch' and 'Customer Settlement Batch (Actual)'
    Then GL batch should post 'Debit Customer Cash','Credit Nostro Cash','Credit Fee Income' in ILS with correct TD/VD and no suspense
    When I send a POST request to '/api/tax/eod/send-movements' with payload:
      """
      { "businessDate": "<settleDate>", "orders": ["${orderId}"] }
      """
    Then the tax engine response status should be 200 and a 'TaxFileId' should be recorded
    When I re-send the same 1052 payload
    Then Settlement Advice creation should be idempotent and no duplicate postings occur
    And reports '1051 recon', '32/1091 store', 'RSP34290' should show no mismatches
    And the audit trail should include 'OrderId','DealId','OpenDeliveryId','SettlementAdviceId','GLBatchId','TaxFileId'

    Examples:
      | tradeDate  | settleDate  |
      | 2026-01-02 | 2026-01-05  |

  @api @nyse @equity @sell @averageRebook @fees @multiccy @settlement @tax
  Scenario Outline: Foreign Equity Sell - broker cancel-and-average rebook, fees segregation, T+1 settlement and FX
    Given the API base URL is '${BASE_URL}' and authorization token is set
    And a SELL order exists on NYSE for 'KMT.N' qty 500 with partial executions on '<tradeDate>'
    When I send a POST request to '/api/files/ingest/broker-order-summary' with payload:
      """
      {
        "businessDate": "<tradeDate>",
        "orders": [
          {
            "brokerOrderRef": "B123",
            "symbol": "KMT.N",
            "side": "SELL",
            "avgPrice": 56.05,
            "currency": "USD",
            "fees": { "brokerCommission": 12.34, "SEC": 1.23, "TAF": 0.75 }
          }
        ]
      }
      """
    Then original executions should be cancelled and one average deal rebooked
    And OD status should be 'Matched'
    And fee handling should post SEC to Third Party Payable, customer ST Commission to Fee Income, brokerCommission and TAF to Fee Expense
    When I run the 'Foreign Street Settlement Batch' for '<settleDate>'
    Then street-side cash movements should post in USD and FX translation to ILS should be recorded per rules
    When I run the 'Customer Settlement Batch' for '<settleDate>'
    Then postings should occur on value date with TD/VD stamps and correct FX conversions
    And recon vs broker file should be 'Reconciled after rebook'
    And reports include broker commission with SEC and TAF
    And TAF cap differences are flagged for refund workflow (no auto cap)
    When I send a POST request to '/api/tax/eod/send-movements' with payload:
      """
      { "businessDate": "<settleDate>", "orders": ["${orderIdSell}"] }
      """
    Then SELL tax should be calculated on settlement date and positions align in tax-engine reconciliation

    Examples:
      | tradeDate  | settleDate  |
      | 2026-01-07 | 2026-01-08  |

  @ui @backoffice @transfer @outsideBank @makerChecker
  Scenario Outline: UI - Security Transfer Outside Bank with relatives split and maker-checker
    Given I am logged in as 'Branch Maker' at the home MU and on Transfers > Security Transfer
    And I select TASE positions for symbol '<symbol>' and default full available quantity
    When I click 'Add Beneficiary' and choose 'Outside Bank'
    And I add two beneficiaries with splits '60' and '40' and bank/branch codes and accounts provided
    And I uncheck 'Same Entity' and select Transfer Case 'Transfer between relatives' subcase 'Spouse of a sister/brother'
    And I click 'Verify'
    Then validations should pass: only TASE allowed, branch filtered, fractional permitted, order date read-only today
    When I Preview, print commission quote, tick 'I Agree' and click 'Release'
    Then the transaction is routed to Checker1 with remarks and appears in Authorization Queue
    When 'Checker1' approves and escalates to 'Checker2' and 'Checker2' approves
    Then the status becomes 'U-Authorized' and audit trail shows 'TransferOrderId' and 'AuthorizationIds'

    Examples:
      | symbol |
      | ABCD   |

  @api @tase @transfer @files @recon @settlement @lots @tax
  Scenario Outline: Transfer Outside Bank - File 15 to 1051 recon to 1052 settlement and lots movement
    Given the API base URL is '${BASE_URL}' and authorization token is set
    And a U-Authorized transfer order exists with two split legs for symbol 'ABCD'
    When I run the 'BOD File 15' generator for '<bodDate>'
    Then a File15Id should be produced and sent to TASE
    When I ingest 1051 on '<bodDatePlus1>'
    Then reconciliationStatus should be 'Reconciled' at order level
    When I ingest 1052 on '<settleDate>'
    Then Settlement Advice should be created and auto-matched with Open Delivery within tolerance '1.00' ILS and statuses set to 'Settled'
    And custody blocks are removed and DR movements written
    And lots/layers moved to beneficiaries and taxIdentifierFlag set to 1
    When I send a POST request to '/api/tax/eod/send-movements' with payload:
      """
      { "businessDate": "<settleDate>", "transfers": ["${TransferOrderId}"] }
      """
    Then GL postings should reflect 'Debit Transfer Fee','Credit Fee Income','Security DR/CR between internal transfer accounts' with proper TD/VD

    Examples:
      | bodDate    | bodDatePlus1 | settleDate  |
      | 2026-01-02 | 2026-01-03   | 2026-01-03  |

  @api @mutualfund @tase @autoPriceCorrection @allocation @recon @settlement @tax
  Scenario Outline: Mutual Fund purchase with auto price correction via 1051 Reverse and Reallocate
    Given the API base URL is '${BASE_URL}' and authorization token is set
    And an MF order exists for fund 'XYZ' with units 1000
    When I ingest 1051 allocation for '<tradeDate>' at NAV_T 10.000
    Then allocation should be created and contractual customer cash settlement scheduled for T+1 at 17:30
    When I run 'Customer Settlement Batch' on '<contractualDate>'
    Then cash debit principal + commission should be posted with TD/VD
    When I ingest 1051 price correction on '<contractualDate>' with new NAV 10.050 and reverse+reallocate
    Then the prior allocation is reversed (movements only) and a new allocation booked at corrected NAV without duplication
    When I ingest 1052 on '<contractualDate>'
    Then street side settlement completes and OD/SA are 'Settled'
    And GL and tax reflect corrected price and idempotence prevents duplicate SA
    And MF Order Book shows 'Allocation','Reversed','Reallocated','Settled'

    Examples:
      | tradeDate  | contractualDate |
      | 2026-01-05 | 2026-01-06      |

  @ui @backoffice @amendment @makerChecker
  Scenario Outline: UI - Order Amendment on executed local equity with reversal and rebook
    Given I am logged in as 'Back Office Operator' and on BO > Order Amendment
    When I set Amendment Type 'Non-Derivative' and Amendment For 'ExistingOrder'
    And I enter executed Order Id '<origOrderId>' and source portfolio '<sourcePortfolio>'
    And I select checkboxes 'Price' and 'Portfolio' and set corrected limit price '104.80' and Correction Portfolio '<targetPortfolio>'
    And I provide remarks and click 'Save' to trigger workflow
    Then exceptions route to Checker1 and I assign to Checker1
    When Checker1 approves and limits escalate to Checker2 and Checker2 approves if required
    Then amendment status should be 'Completed' with audit links to original and amended entities

    Examples:
      | origOrderId | sourcePortfolio | targetPortfolio |
      | ORD-12345   | P-1111          | P-9999          |

  @api @backoffice @amendment @reversal @rebook @tax
  Scenario Outline: API - Verify amendment reversal and rebook postings and idempotence
    Given the API base URL is '${BASE_URL}' and authorization token is set
    When I GET '/api/orders/<origOrderId>/amendment/status'
    Then the response status should be 200 and 'state' should equal 'Completed'
    When I GET '/api/orders/<origOrderId>/postings'
    Then I should see reversal entries exactly negating principal, fees and tax with correct TD/VD
    When I GET '/api/orders/<newOrderId>/postings'
    Then I should see new postings for corrected deal hitting GLs 'Customer Cash','Nostro Cash','Fee Income/Expense'
    When I re-apply amendment via POST '/api/orders/<origOrderId>/amend' with identical payload
    Then the response status should be 409 and error 'idempotent' and no duplicate reversals or rebookings are created
    When I POST '/api/tax/eod/send-movements' with payload:
      """
      { "businessDate": "<eodDate>", "orders": ["<newOrderId>","<origOrderId>"] }
      """
    Then tax postings should show prior items reversed and recomputed for corrected deal

    Examples:
      | origOrderId | newOrderId | eodDate    |
      | ORD-12345   | ORD-12345A | 2026-01-07 |

  @ui @entitlements @marketdata @profiles
  Scenario Outline: Market Data entitlement matrix enforcement for Live vs Delayed
    Given I am logged in via SSO as 'Call Centre Agent' using entitlement profile '<profile>'
    And I open Market Watch and add TASE 'ABCD' and NYSE 'KMT.N'
    When I 'Get Quote' for 'ABCD'
    Then I should see '<localTag>' and depth actions '<localDepth>'
    When I 'Get Quote' for 'KMT.N'
    Then I should see '<foreignTag>' and depth actions '<foreignDepth>'
    When I open Order Entry for 'KMT.N'
    Then the top-of-panel quote shows '<foreignPanelWatermark>'
    When I open Order Entry for 'ABCD'
    Then Order Quote and Depth are '<localPanelState>'
    And Index Watch shows indices 'Live' irrespective of profile
    And Top Gainers/Losers shows delayed list with footer 'Prices are delayed by 20 minutes'
    When I switch to entitlement profile '<profileSwitch>'
    Then foreign quotes and depth now show 'Live' and delayed banners disappear
    And E-Journal and audit entries exist for entitlement changes and widget access

    Examples:
      | profile   | localTag | localDepth | foreignTag | foreignDepth | foreignPanelWatermark | localPanelState | profileSwitch |
      | PROFILE-A | Live     | Enabled    | Delayed    | Disabled     | Delayed               | Live            | PROFILE-B     |

  @ui @negative @tase @selfTransaction
  Scenario Outline: Self-transaction prevention across portfolios at BP-level with price logic
    Given I am logged in as 'Call Centre Agent' and authenticated BP '****' with portfolios P1 and P2
    And in P1 I place a Buy Limit for 'ABCD' qty 1000 at 100.00 ILS and it is 'Authorized' then 'Placed with Market'
    When I switch to P2 and place a Sell '<sellType>' for 'ABCD' qty 200 with price '<sellPrice>' and click 'Confirm'
    Then I should see '<expectedResult>' and '<errorMsg>' if blocked
    When P1 order is partially executed 400 @ 100.00
    And in P2 I try Sell Limit at 99.90
    Then I should see 'Blocked' and 'Self-Transactions are not allowed in TASE'
    When P1 order is fully executed
    And in P2 I place a Sell Market for 200
    Then the order is accepted and sent to market
    And audit logs show single blockage attempts and BP-level application with no override workflow permitted

    Examples:
      | sellType | sellPrice | expectedResult | errorMsg                                  |
      | Market   | 0         | Blocked        | Self-Transactions are not allowed in TASE |
      | Limit    | 99.90     | Blocked        | Self-Transactions are not allowed in TASE |
      | Limit    | 101.00    | Accepted       |                                            |

  @api @tase @1054 @failPending @reversal @idempotence
  Scenario Outline: 1054 Failed/Pending settlement handling with manual blocks and cancellation
    Given the API base URL is '${BASE_URL}' and authorization token is set
    And an executed Buy deal exists for 'ABCD' with 'DealId' and 'OpenDeliveryId'
    When I ingest 1054 on '<tPlus1>' marking the trade as '<status1054>'
    Then reconciliationStatus on deal and OD updates to '<status1054>' and alerts raised
    When I create a manual custody block equal to executed quantity
    Then customer Actual settlement batch should not post client-side settlement for this OD
    When I initiate Cancel for the failed order via '/api/st-orders/<orderId>/cancel' and obtain Checker1 approval
    Then reversal movements for principal, fees, and tax are posted with TD/VD
    And OD/SA linkage is removed and OD excluded from future matching
    When I re-upload the same 1052 for this OD
    Then idempotence prevents SA creation
    When I re-ingest the same 1054 file
    Then no duplicate state changes occur and audit logs single processing instance
    And GL balances reflect net zero and tax engine reverses prior provisional items

    Examples:
      | tPlus1     | status1054 |
      | 2026-01-06 | Failed     |
      | 2026-01-06 | Pending    |

  @api @tase @fractions @transitDeal @batch
  Scenario Outline: Fractional orders batch settlement with transit deals and average price computation
    Given the API base URL is '${BASE_URL}' and authorization token is set
    And two SELL orders executed on '<tradeDate>' produced fractional leftovers totaling non-integer units
    When I ingest 1052 on '<tPlus1>'
    Then integer portions settle and fractions remain outstanding
    When I run 'Fractional Settlement Batch' post-1052
    Then a Transit Deal is created between customer and bank fraction portfolio for exact fractional quantities
    And average price equals weighted average execution price of sells on '<tradeDate>' in ILS with rounding per rules
    And GL posts 'Credit Customer Securities','Debit Internal Fraction Portfolio' with no suspense
    And duplicate prevention keys avoid multiple transit deals on reruns
    And RSP34400 reflects instrument, fractional quantity, average price, parent orders, and GL batch reference

    Examples:
      | tradeDate  | tPlus1     |
      | 2026-01-05 | 2026-01-06 |

  @api @fees @custody @accrual @quarterly @idempotence
  Scenario Outline: Custody fee daily accrual recompute and quarterly application with messaging
    Given the API base URL is '${BASE_URL}' and authorization token is set
    When I run 'Custody Daily Accrual' for '<dayD>'
    Then accruals are computed per security with tiering and caps and FX applied where required
    When a back-dated trade correction on '<dayDPlus2>' affects Day '<dayD>'
    And I run 'Custody Daily Accrual Recompute'
    Then Day '<dayD>' accrual is adjusted by delta without double-counting
    When I run 'Quarterly Aggregation' at quarter end '<quarterEnd>'
    And I execute 'Apply Custody Fees'
    Then customer cash is debited and Fee Income credited with TD/VD
    And messages '77' and '425' are generated and delivered
    And RSP34390 reconciles with GL
    When I rerun 'Apply Custody Fees' for the same quarter
    Then idempotence prevents duplicate debits

    Examples:
      | dayD       | dayDPlus2  | quarterEnd  |
      | 2026-01-03 | 2026-01-05 | 2026-03-31  |

  @ui @backoffice @instrumentSetup @makerChecker
  Scenario Outline: Instrument setup and type mapping - Makam and Foreign ETF CRUD validations
    Given I am logged in as 'Back Office Admin' and on Financial Instruments
    When I trigger auto-ingestion for TASE and select a new Makam
    Then the system maps to type '54' TBills with faceValue, poolFactor, couponType 'None', currency 'ILS'
    When I set rate type parameters (Price in Percentage, Clean vs Dirty) and CPI linkage and Save
    Then Checker1 approves and instrument status becomes 'Authorized' with InstrumentId and AuthorizationId captured
    When I create a new Foreign ETF manually (exchange NYSE, currency USD) with instrumentType '229', lotSize 1, priceDecimals 4, quantityDecimals 3 and route for approval
    Then Checker1 approves and ETF is Authorized
    When I attempt to create a duplicate instrument with same ISIN/Ticker
    Then I should see error 'INSTR_DUP_KEY'
    When I edit the ETF to change quantityDecimals to '6' and priceDecimals to '6'
    Then change is accepted
    When I set quantityDecimals to '7' or priceDecimals to '7'
    Then I should see error 'DEC_PRECISION_EXCEEDED'
    When I deactivate the ETF with no holdings and then reactivate
    Then both state changes are captured in E-Journal
    When I attempt to delete the Makam with a dummy reference present
    Then delete is blocked with 'INSTR_IN_USE' and only Deactivate permitted
    And in Call Centre Order Entry and Advanced Search authorized active instruments appear and Draft/Deactivated remain hidden

    Examples:
      |            |
      | placeholder|

  @api @marketInfo @rates @idempotence @manualOverride @valuation
  Scenario Outline: Market Information rates - automated feed, errors, manual entries, CPI and lock override
    Given the API base URL is '${BASE_URL}' and authorization token is set
    When I POST '/api/mi/feeds/ingest' with payload:
      """
      { "source": "TASE", "businessDate": "<bizDate>", "rows": [ { "symbol":"ABCD", "price": 101.23, "currency":"ILS" } ] }
      """
    Then feed loads with provenance 'Feed'
    When I re-upload the same feed file
    Then idempotence prevents duplicate rows and CTRLM logs 'Duplicate Ignored'
    When I POST '/api/mi/feeds/ingest' with payload missing price for a symbol
      """
      { "source": "TASE", "businessDate": "<bizDate>", "rows": [ { "symbol":"EFGH", "currency":"ILS" } ] }
      """
    Then bad record is rejected with error 'RATE_MISSING_FIELD' and others processed
    When I POST '/api/mi/feeds/ingest' with invalid currency for ETF
      """
      { "source": "Bloomberg", "businessDate": "<bizDate>", "rows": [ { "symbol":"KMT.N", "price": 56.2000, "currency":"EUR" } ] }
      """
    Then record fails with 'RATE_CCY_MISMATCH' and prior good rate is not overwritten
    When I POST '/api/mi/manual/single' with payload:
      """
      { "symbol": "MAKAM-XYZ", "cleanPrice": 99.876, "cpiIndex": 1.012, "provenance": "Manual Single" }
      """
    Then Portfolio Valuation should use CPI-adjusted value
    When I POST '/api/mi/manual/mass' with payload:
      """
      { "rows": [
        { "symbol": "ABCD", "price": 0.01 },
        { "symbol": "EFGH", "price": 0.00 },
        { "symbol": "KMT.N", "price": 9999999.01 }
      ] }
      """
    Then 0.00 and >9,999,999.00 should be rejected with 'PRICE_THRESHOLD_BREACH' and decimals validated per instrument rules
    When I POST '/api/mi/override/lock' with payload:
      """
      { "symbol": "ABCD", "price": 102.00, "lock": true }
      """
    And I ingest a new feed containing 'ABCD'
    Then locked manual price is not overwritten and provenance remains 'Manual Override'
    When I run 'valuation refresh' for '<bizDate>'
    Then affected portfolios reflect new rates in account currency using FX and TD/VD preserved
    When I POST '/api/mi/feeds/ingest' with prior-date file after EOD
      """
      { "source":"TASE", "businessDate":"<priorDate>", "rows":[ { "symbol":"ABCD","price": 100.00, "currency":"ILS" } ] }
      """
    Then rows go to historical table per policy without changing today's rates

    Examples:
      | bizDate    | priorDate  |
      | 2026-01-06 | 2025-12-30 |

  @ui @callcentre @extranet @blocks
  Scenario Outline: UI - Extranet off-floor pre-blocks and manual capture authorization
    Given I am logged in as 'Call Centre Agent' and on Fund Balance
    When I place a '<blockType>' block for expected extranet trade and record Block Reference
    Then block should be visible in balances
    Given I am logged in as 'Back Office Operator' on Manual Trade Capture
    When I select order category 'Extranet transaction out of exchange' and enter instrument, side, quantity, price and portfolio
    And I preview fees and confirm
    Then the trade is routed to Checker1 if limits exceeded
    When Checker1 approves
    Then deal and Open Delivery are created and trade trail indicates 'Extranet category'
    And I expire previously placed blocks and verify balances update

    Examples:
      | blockType |
      | Cash      |
      | Custody   |

  @api @tase @extranet @recon @settlement @idempotence
  Scenario Outline: API - Extranet recon and settlement with duplicate capture prevention
    Given the API base URL is '${BASE_URL}' and authorization token is set
    When I ingest 1051 for '<tradeDate>' showing extranet trade without corresponding order
    Then reconciliationStatus is 'Not Matched' and flagged on exception report
    When on '<tPlus1>' I confirm manual BO trade capture exists with 'ManualDealId'
    And I ingest 1052 for '<settleDate>'
    Then system creates SA and auto-matches OD and SA under tolerance and sets status 'Matched'
    When I run 'Street Settlement' and 'Customer Settlement'
    Then postings occur on settlement date with correct TD/VD, GL double-sided Nostro/Customer per business event
    When I attempt to capture the same extranet trade again with identical instrument/qty/price
    Then the API responds 409 with error 'EXTN_DUP_TRD' and no duplicate is created

    Examples:
      | tradeDate  | tPlus1     | settleDate  |
      | 2026-01-05 | 2026-01-06 | 2026-01-06  |

  @api @tase @transferIn @file132 @repair @settlement @idempotence
  Scenario Outline: Incoming Security Transfer via File 132 - To Be Repaired to settlement
    Given the API base URL is '${BASE_URL}' and authorization token is set
    When I ingest File 132 at BOD for '<bodDate>' containing one good and two error records
    Then Delivery In orders are created: one 'Authorized', two 'To Be Repaired'
    Given I open the Incoming Transfer Repair screen as 'Back Office Operator'
    When I repair record A by mapping missing security
    And I repair record B by aligning layers to order quantity
    And I repair record C by correcting beneficiary identifiers
    And I route for authorization and Checker1 approves
    Then state moves from 'To Be Repaired' to 'Authorized' and custody blocks applied
    When I ingest 1051 and then 1052
    Then SA is created and matched with OD and statuses are 'Settled'
    And lots are transferred and taxIdentifierFlag derived appropriately, and EOD tax feed sent
    When I retry ingesting the same File 132
    Then duplicates are ignored and no new postings occur

    Examples:
      | bodDate    |
      | 2026-01-05 |

  @ui @backoffice @delivery @conversion @linkedLegs
  Scenario Outline: Delivery In/Out - ADR to Local security conversion with linked legs
    Given I am logged in as 'Back Office Operator'
    When I create a Delivery Out with Delivery Type 'ADR to Local Sec Conversion' and External Reference 2 'CONV-REF-123'
    And I create a Delivery In with Delivery Type 'ADR to Local Sec Conversion' and External Reference 2 'CONV-REF-123'
    And I submit both legs for approval
    Then Checker1 approves and both orders become 'Authorized' and ODs created and linkage stored
    When I authorize/ingest Settlement Advice(s) or 1052
    And I auto-match or manually match OD/SA for both legs using 'Instrument,Custodian,Settlement Type,Quantity' and Amount zero/tolerance
    Then both legs 'Settled', ADR position reduced and local position increased by converted quantity
    And no duplicate SA/matching allowed when retrying with same External Reference 2
    And audit and reports show linkage by CONV-REF-123

    Examples:
      |            |
      | placeholder|

  @ui @negative @poa @channelRestrictions
  Scenario Outline: POA restriction - Call Centre blocked, Front Office allowed
    Given I am logged in as 'Call Centre Agent' acting as POA for a customer
    When I open Order Entry for 'ABCD' and set Buy Limit 100.00 ILS qty 200 and click 'Place Order'
    And I proceed to Confirm
    Then order placement is blocked with error 'POA_CC_BLOCK' and no order id or blocks are created
    And no authorization workflow can override this restriction
    When I log in as 'Front Office User' acting as the same POA and place the same order
    Then the order is 'Authorized' then 'Placed with Market' and appears in Order Book
    And audit shows channel='FO' role='POA' and user ids
    And PII is masked on screens and exports
    When I attempt an MF Purchase via Call Centre as POA
    Then the same restriction applies with 'POA_CC_BLOCK'

    Examples:
      |            |
      | placeholder|

  @ui @orderManagement @modifyCancel @disclosed @stoplimit @cutoff
  Scenario Outline: Pending order modification/cancellation matrix with disclosed qty and nostro cutoff
    Given I am logged in as 'Call Centre Agent'
    And I place a Buy Stoplimit order for 'ABCD' qty 1000, disclosed Initial 200 Additional 100, triggerPrice 99.80, limitPrice 100.00, validity 'Good For Month'
    Then status is 'Authorized' then 'Placed with Market'
    When I modify price condition to 'Market' keeping validity GFM and accept warning
    Then modification is saved and trail updated
    When I modify disclosed quantities to Initial 300 and Additional 200
    Then validations pass (Initial <= total, Initial+Additional <= total) and modification saved
    When a partial execution of 250 units occurs
    Then open quantity is 750 and blocks update proportionally
    When I attempt to increase total quantity to 1200 after partial fill
    Then I see error 'QTY_INC_AFTER_PARTIAL_NOT_ALLOWED' and no change applies
    When I modify validity to 'Good For Day' near end of trading
    Then expiry date updates and alerts shown
    When I cancel the order
    Then remaining open qty is cancelled and state changes to 'Cancelled'
    Given I create a Sell Limit and leave it pending beyond 'nostro open order cutoff'
    When the cutoff job runs
    Then the order is auto-cancelled or blocked per setup and an operational alert is logged
    And E-Journal and auditTrail show modifications, cancellations, cutoff action

    Examples:
      |            |
      | placeholder|

  @api @positions @recon @1053 @871 @tax @ageing @idempotence
  Scenario Outline: Positions reconciliation EOD - TASE 1053, APEX 871 and Tax Engine with ageing
    Given the API base URL is '${BASE_URL}' and authorization token is set
    When I ingest TASE 1053 for '<eodDate>' and APEX 871 and Tax Engine Open Positions
    And I execute Reconciliation job
    Then matched items move to 'Reconciled' and unmatched to 'Not Matched' and counts by source are captured
    When I introduce mismatches and rerun recon
    Then exceptions appear with state 'Failed' and ageing 'Day-0'
    When I advance business date and re-ingest the same files
    Then duplicates are ignored and ageing increments to 'Day-1'
    When I perform a manual position correction and mark exception 'Repaired' and rerun recon
    Then item moves to 'Reconciled' and audit logs include 'RepairActionId'
    When I mark an extra foreign position as 'External Only' or align via manual movement
    Then state transitions to 'Closed Manually' and excluded from further ageing
    When I re-ingest corrected tax positions file
    Then exceptions auto-resolve to 'Reconciled'
    And recon reports show states and ageing buckets with PII masking
    When I inject a late prior-date 1053 after EOD
    Then it posts to historical store without changing today's statuses

    Examples:
      | eodDate    |
      | 2026-01-06 |

  @api @fees @regulatory @814 @815 @414 @idempotence
  Scenario Outline: Regulatory commission and fee reporting with SELL-only third-party handling and publication
    Given the API base URL is '${BASE_URL}' and authorization token is set
    And settled trades exist across Equity, ETF, MF with various fee items for period '<period>'
    When I run 'Fee Aggregation' for '<period>'
    Then computed fees respect basis, min/max caps and tiers
    When I generate TASE 814 (and 815 if applicable)
    Then 'averages' match computed averages and 'price list' reflects configured tariffs and files stored with run ids
    When I generate BOI 414 A/B/C customer packets
    Then packets contain the correct data per type and 414-A is published to website with PII masking
    And SELL-only SEC/TAF appear only on SELL foreign equity marked Third Party and excluded from bank income totals with GL mapping to Third Party Payable
    When I include boundary trades below min and above max
    Then applied amounts equal min or max and reported consistently
    When I rerun reporting batches for the same period
    Then idempotence prevents duplicate files or versions without duplicate accounting (error 'DUP_PERIOD_IGNORED' or versioned)
    And totals reconcile with GL Fee Income and Third Party Payable

    Examples:
      | period     |
      | 2025-Q4    |

  @ui @backoffice @transfer @virtualSell @muRestriction @caExDate
  Scenario Outline: Within-bank Securities Transfer - Virtual Sell with MU restriction and CA ex-date block
    Given I am logged in as 'Branch Maker' at a non-home MU
    When I open Transfers > Security Transfer and attempt initiation
    Then I see 'MU_HOME_BRANCH_REQUIRED' and no draft is created
    When I log in at home MU and select a security on CA ex-date
    And I choose Within Bank and tick 'Virtual Sell'
    And I click 'Verify'
    Then I see 'CA_EXDATE_BLOCK' and no custody blocks applied
    When I select a different TASE security without CA ex-date and keep full quantity
    And I Preview, tick 'I Agree' and 'Release' assigning to Checker1
    Then Checker1 approves and status is 'U-Authorized'
    When EOD process runs
    Then transfer auto-settles within bank, custody blocks removed, only security movements via internal control posted
    And EOD tax sets taxIdentifierFlag=1 and audit shows MU ids and Virtual Sell flag

    Examples:
      |            |
      | placeholder|

  @ui @mutualfund @manualPriceCorrection @makerChecker
  Scenario Outline: UI - MF manual price correction (Reverse and Reallocate) and recompute
    Given I am logged in as 'Back Office Operator' on MF Allocation Reversal/Execution Handling
    When I search fund 'XYZ' and date '<tradeDate>' and view AllocationId and GLBatch reference
    And in Market Information I update rate to corrected NAV '<navCorr>' for '<tradeDate>' and note RateBatchId
    And I select action 'Reverse' (movements only) and submit for authorization
    Then Checker1 approves and allocation status sets to 'Reversed'
    When I initiate 'Reallocate' at corrected NAV, route for approval, and Checker1 approves
    Then AllocationId2 is created and idempotence prevents repeating without new rate change (error 'ALLOC_CORR_ALREADY_APPLIED')
    When 1052 is ingested on T+1
    Then street-side settlement posts once against the corrected allocation and duplicate SA is prevented
    And GL and tax recompute correctly and reports and Kafka events reflect correction

    Examples:
      | tradeDate  | navCorr |
      | 2026-01-05 | 10.050  |

  @api @tase @netSettlement @32 @1091 @storeOnly @toggle @idempotence
  Scenario Outline: TASE Net Settlement 32 and 1091 - store-only ingestion, recon toggle and late arrival
    Given the API base URL is '${BASE_URL}' and authorization token is set
    When I set 'ReconEnabledForTASEFees' to 'No'
    Then audit records the toggle and processing mode is 'Store Only'
    When I ingest File 32 interim (Type C) for '<bizDate>'
    Then rows are stored with FileBatchId32A and no recon executed
    When I ingest File 1091 for '<bizDate>'
    Then rows stored with FileBatchId1091A augmented with portfolio, type and subtype and no GL/fee recompute triggered
    When I generate 32 store report
    Then report is based on last file with INTERIM watermark and no reconciliation status
    When I re-ingest the same interim files
    Then idempotence logs 'DUP_FILE_IGNORED'
    When I ingest File 32 final (Type D) for '<bizDate>'
    Then prior interim is superseded for reporting and finalized with FileBatchId32B tagged FINAL
    When I set 'ReconEnabledForTASEFees' to 'Yes' and load fee schedule and run Recon job
    Then differences at trade level are computed using 1091 vs system and min/max cap cases highlighted
    When I upload a malformed 1091 with missing field
    Then bad rows rejected with 'FILE_FIELD_MISSING' and skip items created
    When I inject prior-date final 32 after EOD
    Then it is stored historically without changing today's reporting or recon outcomes
    And exported reports show PII masking and FINAL tags with run timestamp

    Examples:
      | bizDate    |
      | 2026-01-06 |

  @api @distributionFee @accrual @monthEnd @kafka @idempotence
  Scenario Outline: Distribution fee daily accrual and month-end packets with Kafka events
    Given the API base URL is '${BASE_URL}' and authorization token is set
    When I run 'Distribution Fee Daily Accrual' for day '<dayD>'
    Then accrual per fund uses NAV_D and FX to ILS and AccrualRunId stored and exemptions applied (money market zero, no-agreement not billed)
    And boundary cases (zero holdings = zero, large position capped) are applied and stored
    When I advance through the month including leap-day if applicable and run daily accruals
    Then weekend/holiday behavior follows config and totals maintain continuity
    When I run 'Month-End Packet Generator' for '<period>'
    Then per fund per manager CSV/PDF packets generated and delivered via secure email and Kafka events emitted with metadata and no PII
    And BO summary report reconciles with GL policy (Fee Income posted monthly or memo-only)
    When I rerun Month-End generator for the same period
    Then idempotence or versioning applies without duplicate accounting (error 'DUP_PERIOD_IGNORED' or new version)
    When I alter one day’s accrual by back-dated position correction and rerun recompute
    Then month total adjusts and a new packet version is generated with audit retained

    Examples:
      | dayD       | period  |
      | 2026-02-01 | 2026-02 |

  @ui @backoffice @thirdPartyTransfer @manualSettlement @makerChecker
  Scenario Outline: Third Party Transfers (Foreign custodian) - Delivery Out/In with reporting and manual settlement
    Given I am logged in as 'Back Office Operator' on Create Securities Transfer Order
    When I choose '<transferType>' for foreign instrument 'ABC.N' in USD with quantity including fractional if supported
    And I set Transfer Case 'Third party Transfer' and enter beneficiary custodian details in external reference
    And I tick 'I Agree' and 'Release' and assign to Checker1
    Then Checker1 approves and status is 'U-Authorized' and 'Not Sent to TASE' marker present and custody block applied
    When I generate Third Party Transfer report extract
    Then record shows masked PII with portfolio id, instrument, quantity, expected deliver date and beneficiary fields
    When custodian confirms off-system and I post Manual Settlement movements
    Then for Delivery Out: reduce customer securities and post to Internal Transfer Control with proper TD/VD and valuation FX if needed
    And for Delivery In: increase customer securities and reverse internal control and lots captured with Same Entity not applied
    When I attempt to repost manual settlement for the same external reference
    Then system blocks with 'DUP_EXT_REF' and no duplicate postings occur
    And Security Transfer History shows 'Settled' and audit entries for both legs

    Examples:
      | transferType |
      | Delivery Out |
      | Delivery In  |

  @ui @frontoffice @rePlacement @stoplimit @validity @expiry
  Scenario Outline: FO daily re-placement for GFM At the Opening Stoplimit across days to expiry
    Given I am logged in as 'Call Centre Agent' with FO–BO integration active
    When I place a Buy Stoplimit for 'ABCD' trigger 99.80, limit 100.00, qty 1200, validity 'Good For Month', release 'At the Opening'
    Then status is 'Authorized' then 'Placed with Market' (At the Opening Day 1) and cash block equals consideration + fees
    When Day 1 opens below trigger then rises above trigger but below limit with no fill
    Then order remains Pending and cash block remains
    When EOD occurs with no fills
    Then FO re-queues order for Day 2 At the Opening and trail shows 'Re-Placement by FO' with reference to child submission if applicable
    When on Day 2 partial execution 300 @ 99.95 occurs
    Then status 'Partially Executed' open qty 900 and block decreases proportionally and recon vs 1051 pending until file arrival
    When I modify trigger to 100.00 equal to limit
    Then decision-table allows equality or warning is accepted and FO uses updated trigger from next day
    When on Day 10 open price above limit 100.20 and 600 executes
    Then open qty 300 remains and state/history reflects multi-day partials
    When liquidity prevents remaining fills until expiry
    Then FO continues daily submission; on expiry the order auto-expires and blocks are released and E-Journal shows Auto-Expiry
    When I attempt to manually re-place the expired order
    Then the system requires a new order and blocks reuse with 'ORDER_EXPIRED_REUSE_NOT_ALLOWED'
    And auditTrail includes FO re-placement entries, modifications, executions and expiry

    Examples:
      |            |
      | placeholder|
