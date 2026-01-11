gherkin
Feature: Capital Markets E2E - Trading, Settlements, Transfers, Fees, Recon and Entitlements

  # API Tests

  @api @orders @validations @CMBO-TC-001
  Scenario Outline: Local equity buy - order capture validations (self-transaction prevention and price threshold correction)
    Given the API base URL is '<base_url>'
    And the authorization token is set to '<token>'
    And the content type is 'application/json'
    When I send a POST request to '/api/orders' with payload
      """
      {
        "portfolioId": "PF-XXXXXX01456",
        "bpId": "BP-XXXX024202",
        "accountId": "0413XXXXXXXILS",
        "exchange": "TASE",
        "instrumentType": "EquityInstrmnts",
        "symbol": "TASE:AAA",
        "side": "BUY",
        "orderType": "LIMIT",
        "validityType": "GFD",
        "price": <price>,
        "quantity": <qty>,
        "channel": "<channel>",
        "counterpartyAccountId": "<counterpartyAccountId>",
        "entitlements": { "liveLevel1": true, "level2": true }
      }
      """
    Then the response status should be <status>
    And the response body should contain "errorCode" = "<errorCode>"
    And the response body should contain "message" = "<message>"

    Examples:
      | base_url            | token     | price | qty | channel  | counterpartyAccountId | status | errorCode                 | message                                   |
      | https://api.bank/v1 | bearer123 | 10.00 | 10  | Internet | 0413XXXXXXXILS        | 400    | SELF-TRANSACTION-BLOCKED | Self-Transactions are not allowed in TASE |
      | https://api.bank/v1 | bearer123 | 1.00  | 10  | FO       |                       | 422    | 31042                     | price threshold error                     |

  @api @orders @recon @settlement @fees @tax @idempotency @CMBO-TC-001
  Scenario: Local equity buy - partial fills, 1051 recon, manual match within tolerance, 1052 idempotency, fees and tax
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'bearer123'
    And the content type is 'application/json'
    When I send a POST request to '/api/orders' with payload
      """
      {
        "portfolioId": "PF-XXXXXX01456",
        "bpId": "BP-XXXX024202",
        "accountId": "0413XXXXXXXILS",
        "exchange": "TASE",
        "instrumentType": "EquityInstrmnts",
        "symbol": "TASE:AAA",
        "side": "BUY",
        "orderType": "LIMIT",
        "validityType": "GFD",
        "price": 10.15,
        "quantity": 10,
        "channel": "FO"
      }
      """
    Then the response status should be 201
    And the response should contain 'orderId'
    When I send a POST request to '/api/orders/{orderId}/authorize' with payload
      """
      { "role": "Checker", "approvalLevel": 2 }
      """
    Then the response status should be 200
    And the response body should contain "status" = "PLACED_WITH_MARKET"
    When I send a POST request to '/api/executions' with payload
      """
      {
        "source": "ST-SP",
        "exchange": "TASE",
        "executions": [
          { "orderId": "{orderId}", "executionId": "E1", "quantity": 4, "price": 10.15, "tradeDate": "T" },
          { "orderId": "{orderId}", "executionId": "E2", "quantity": 6, "price": 10.20, "tradeDate": "T" }
        ]
      }
      """
    Then the response status should be 202
    And the response body should contain "partiallyExecuted" = true
    When I send a POST request to '/api/recon/1051/import' with payload
      """
      {
        "fileName": "1051",
        "exchange": "TASE",
        "records": [
          { "symbol": "TASE:AAA", "executionId": "E1", "quantity": 4, "price": 10.15, "tradeDate": "T" },
          { "symbol": "TASE:AAA", "executionId": "E2", "quantity": 6, "price": 10.20, "tradeDate": "T" }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "reconciledCount" = 2
    When I send a POST request to '/api/settlement/advice/import' with payload
      """
      {
        "fileName": "1052",
        "exchange": "TASE",
        "advices": [
          { "adviceId": "S1", "orderId": "{orderId}", "executionId": "E1", "netAmount": 40.58, "currency": "ILS" },
          { "adviceId": "S2", "orderId": "{orderId}", "executionId": "E2", "netAmount": 61.22, "currency": "ILS" }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "importedCount" = 2
    When I send a POST request to '/api/manual-matching/link' with payload
      """
      {
        "openDeliveryId": "OD-{orderId}",
        "adviceId": "S2",
        "tolerance": { "currency": "ILS", "amount": 2.00 }
      }
      """
    Then the response status should be 200
    And the response body should contain "matched" = true
    And the response body should contain "excludedFromAutoRecon" = true
    When I send a POST request to '/api/batches/StreetSideSettlementTASE/run' with payload
      """
      { "asOfDate": "T+1", "batchName": "StreetSideSettlementTASE" }
      """
    Then the response status should be 202
    When I send a GET request to '/api/orders/{orderId}/status'
    Then the response status should be 200
    And the response body should contain "status" = "SETTLED"
    When I send a POST request to '/api/settlement/advice/import' with payload
      """
      {
        "fileName": "1052",
        "exchange": "TASE",
        "advices": [
          { "adviceId": "S2", "orderId": "{orderId}", "executionId": "E2", "netAmount": 61.22, "currency": "ILS" }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "duplicatesIgnored" = 1
    When I send a POST request to '/api/fees/commissions/calculate' with payload
      """
      {
        "orderId": "{orderId}",
        "rules": {
          "tiers": [
            { "min": 0, "max": 100000, "ratePct": 0.12 },
            { "min": 100000, "max": 500000, "ratePct": 0.10 },
            { "min": 500000, "max": 999999999, "ratePct": 0.08 }
          ],
          "minFee": 5.00,
          "maxFee": 1500.00,
          "rounding": { "mode": "HALF_UP", "scale": 2 },
          "currency": "ILS"
        }
      }
      """
    Then the response status should be 200
    And the response body should contain "feeItems[0].name" = "ST Commission"
    And the response body should contain "feeItems[0].amount" rounded to 0.01
    When I send a POST request to '/api/integrations/tax/eod' with payload
      """
      { "tradeDate": "T+1", "portfolios": ["PF-XXXXXX01456"] }
      """
    Then the response status should be 202
    And the response body should contain "lotsUpdated" = true
    When I send a GET request to '/api/reports/file32?orderId={orderId}'
    Then the response status should be 200
    And the response body should contain "accountId" masked as "0413****"
    And the response body should contain "nationalId" masked

  @api @foreign @broker @avgprice @fees @settlement @idempotency @CMBO-TC-002
  Scenario: Foreign equity buy - broker EOD average-price recapture, fees mapping, settlement and idempotent re-upload
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'bearer123'
    And the content type is 'application/json'
    When I send a POST request to '/api/orders' with payload
      """
      {
        "portfolioId": "PF-XXXXXX01931",
        "bpId": "BP-XXXX773001",
        "accountId": "0413XXXXUSD",
        "exchange": "NYSE",
        "instrumentType": "EquityInstrmnts",
        "symbol": "NYSE:XYZ",
        "side": "BUY",
        "orderType": "MARKET",
        "validityType": "GFD",
        "quantity": 100,
        "channel": "FO"
      }
      """
    Then the response status should be 201
    And the response should contain 'orderId'
    When I send a POST request to '/api/executions' with payload
      """
      {
        "source": "MARKET",
        "exchange": "NYSE",
        "executions": [
          { "orderId": "{orderId}", "executionId": "E1", "quantity": 40, "price": 50.10, "tradeDate": "T" },
          { "orderId": "{orderId}", "executionId": "E2", "quantity": 60, "price": 49.90, "tradeDate": "T" }
        ]
      }
      """
    Then the response status should be 202
    When I send a POST request to '/api/broker/ordersummary/import' with payload
      """
      {
        "fileName": "Broker OrderSummary CSV",
        "records": [
          {
            "brokerOrderRef": "BREF-123",
            "symbol": "NYSE:XYZ",
            "side": "BUY",
            "tradeDate": "T",
            "avgPrice": 50.00,
            "quantity": 100,
            "fees": { "STCommission": 8.50, "SEC": 0.57, "TAF": 0.03, "BrokerCommission": 12.00 }
          }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "recaptured" = 1
    And the response body should contain "originalTradesCancelled" = 2
    When I send a POST request to '/api/settlement/client/run' with payload
      """
      { "asOfDate": "T+1", "market": "FOREIGN" }
      """
    Then the response status should be 202
    When I send a POST request to '/api/batches/StreetSideSettlementForeign/run' with payload
      """
      { "asOfDate": "T+2" }
      """
    Then the response status should be 202
    When I send a GET request to '/api/orders/{orderId}/fees'
    Then the response status should be 200
    And the response body should contain "SEC" = 0.57
    And the response body should contain "TAF" = 0.03
    And the response body should contain "BrokerCommission" = 12.00
    And the response body should contain "STCommission" >= 5.00
    When I send a POST request to '/api/broker/ordersummary/import' with payload
      """
      {
        "fileName": "Broker OrderSummary CSV",
        "records": [
          {
            "brokerOrderRef": "BREF-123",
            "symbol": "NYSE:XYZ",
            "side": "BUY",
            "tradeDate": "T",
            "avgPrice": 50.00,
            "quantity": 100,
            "fees": { "STCommission": 8.50, "SEC": 0.57, "TAF": 0.03, "BrokerCommission": 12.00 }
          }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "duplicatesIgnored" = 1

  @api @mutualfunds @allocation @reversal @settlement @tax @CMBO-TC-003
  Scenario: Mutual fund purchase - 1051 allocation then reversal/reallocation at corrected NAV, customer and street settlement, tax and accrual triggers
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'bearer123'
    And the content type is 'application/json'
    When I send a POST request to '/api/mf/orders' with payload
      """
      {
        "portfolioId": "PF-XXXXXX27087",
        "bpId": "BP-XXXX190031",
        "accountId": "04XXXXXXILS",
        "fundId": "TASE:MF001",
        "orderType": "PURCHASE",
        "units": 100.0000
      }
      """
    Then the response status should be 201
    And the response should contain 'mfOrderId'
    When I send a POST request to '/api/recon/1051/import' with payload
      """
      {
        "fileName": "1051",
        "records": [
          { "fundId": "TASE:MF001", "nav": 10.0000, "units": 100.0000, "tradeDate": "T", "action": "ALLOCATE" }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "allocated" = 1
    When I send a POST request to '/api/recon/1051/import' with payload
      """
      {
        "fileName": "1051",
        "records": [
          { "fundId": "TASE:MF001", "nav": 10.0500, "units": 99.5025, "tradeDate": "T+1", "action": "REVERSE_AND_REALLOCATE", "reversesTradeDate": "T" }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "reallocated" = 1
    When I send a POST request to '/api/settlement/client/run' with payload
      """
      { "asOfDate": "T+1", "market": "MF" }
      """
    Then the response status should be 202
    When I send a POST request to '/api/settlement/advice/import' with payload
      """
      { "fileName": "1052", "exchange": "TASE", "advices": [ { "fundId": "TASE:MF001", "tradeDate": "T+1", "units": 99.5025 } ] }
      """
    Then the response status should be 200
    And the response body should contain "importedCount" = 1
    When I send a POST request to '/api/integrations/tax/eod' with payload
      """
      { "tradeDate": "T+1", "portfolios": ["PF-XXXXXX27087"] }
      """
    Then the response status should be 202
    And the response body should contain "lotsUpdated" = true
    When I send a GET request to '/api/fees/distribution/accruals?portfolioId=PF-XXXXXX27087&fromDate=T&toDate=T+30'
    Then the response status should be 200
    And the response body should contain "accruals" array

  @api @externalTransfer @file15 @file132 @repair @recon @settlement @idempotency @CMBO-TC-005
  Scenario: Outside-bank transfer outbound (15) and inbound (132) with repair, recon, manual match tolerance and idempotent 1052
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'bearerBO'
    And the content type is 'application/json'
    When I send a POST request to '/api/transfers/outbound' with payload
      """
      {
        "sourcePortfolioId": "PF-XXXXXX19031",
        "securityId": "TASE:EQ123",
        "quantity": 100.0000,
        "market": "TASE",
        "transferType": "DELIVERY_OUT",
        "outsideBank": { "bankCode": "1245", "branchCode": "5124", "beneficiaryAccount": "*******" },
        "sameEntity": false,
        "transferCase": "Transfer to spouse"
      }
      """
    Then the response status should be 201
    And the response should contain 'transferOrderId'
    When I send a POST request to '/api/batches/File15OutboundBOD/run' with payload
      """
      { "asOfDate": "T+1" }
      """
    Then the response status should be 202
    When I send a POST request to '/api/transfers/inbound/132/import' with payload
      """
      {
        "fileName": "132",
        "records": [
          { "transferRef": "IN-001", "securityId": "TASE:EQ456", "quantity": 200.0000, "beneficiaryId": "", "lots": [ { "qty": 100.0000 }, { "qty": 90.0000 } ], "status": "TO_BE_REPAIRED" }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "toBeRepaired" = 1
    When I send a PUT request to '/api/transfers/inbound/IN-001/repair' with payload
      """
      {
        "beneficiaryId": "BP-XXXX990011",
        "lots": [ { "qty": 100.0000 }, { "qty": 100.0000 } ]
      }
      """
    Then the response status should be 200
    And the response body should contain "status" = "READY_FOR_AUTH"
    When I send a POST request to '/api/recon/1051/import' with payload
      """
      { "fileName": "1051", "records": [ { "transferRef": "IN-001", "securityId": "TASE:EQ456", "quantity": 200.0000 } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/settlement/advice/import' with payload
      """
      {
        "fileName": "1052",
        "exchange": "TASE",
        "advices": [ { "adviceId": "T-ADV-1", "transferRef": "IN-001", "securityId": "TASE:EQ456", "netAmount": 1998.50, "currency": "ILS" } ]
      }
      """
    Then the response status should be 200
    When I send a POST request to '/api/manual-matching/link' with payload
      """
      { "openDeliveryId": "OD-IN-001", "adviceId": "T-ADV-1", "tolerance": { "currency": "ILS", "amount": 2.00 } }
      """
    Then the response status should be 200
    And the response body should contain "excludedFromAutoRecon" = true
    When I send a POST request to '/api/settlement/advice/import' with payload
      """
      {
        "fileName": "1052",
        "exchange": "TASE",
        "advices": [ { "adviceId": "T-ADV-1", "transferRef": "IN-001", "securityId": "TASE:EQ456", "netAmount": 1998.50, "currency": "ILS" } ]
      }
      """
    Then the response status should be 200
    And the response body should contain "duplicatesIgnored" = 1

  @api @masterdata @validation @rates @idempotency @makerChecker @CMBO-TC-006
  Scenario Outline: Security product setup validations and MI rate ingestion idempotency
    Given the API base URL is '<base_url>'
    And the authorization token is set to '<token>'
    And the content type is 'application/json'
    When I send a POST request to '/api/products/securities' with payload
      """
      {
        "source": "<source>",
        "isin": "<isin>",
        "exchangeCode": "<exchange>",
        "symbol": "<symbol>",
        "securityType": "<secType>",
        "priceScale": <priceScale>
      }
      """
    Then the response status should be <createStatus>
    And the response body should contain "errorCode" = "<createErrorCode>"
    When I send a POST request to '/api/mi/rates/import' with payload
      """
      {
        "fileName": "MI-Rates CSV",
        "records": [
          { "securityKey": { "isin": "<isin>", "exchange": "<exchange>" }, "rateType": "CLOSE", "rateDate": "T", "price": <ratePrice> }
        ]
      }
      """
    Then the response status should be <rateStatus>
    And the response body should contain "importedCount" = <importedCount>
    When I send a POST request to '/api/mi/rates/import' with payload
      """
      {
        "fileName": "MI-Rates CSV",
        "records": [
          { "securityKey": { "isin": "<isin>", "exchange": "<exchange>" }, "rateType": "CLOSE", "rateDate": "T", "price": <ratePrice> }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "duplicatesIgnored" = <duplicates>

    Examples:
      | base_url            | token         | source  | isin         | exchange | symbol      | secType           | priceScale | createStatus | createErrorCode  | ratePrice | rateStatus | importedCount | duplicates |
      | https://api.bank/v1 | masterBearer  | TASE    | IL0000000229 | TASE     | ETF229      | ETF               | 4          | 201          |                  | 1234.1234 | 200        | 1             | 1          |
      | https://api.bank/v1 | masterBearer  | MANUAL  | IL0000000229 | TASE     | DUP-SEC     | EquityInstrmnts   | 2          | 409          | VAL-DUP-ISIN     | 50.12     | 200        | 0             | 0          |
      | https://api.bank/v1 | masterBearer  | MANUAL  | US0000000001 | NYSE     | TOO-LONG-13 | EquityInstrmnts   | 2          | 422          | VAL-SYMBOL-LEN   | 10.00     | 200        | 0             | 0          |
      | https://api.bank/v1 | masterBearer  | MANUAL  | US0000000002 | NYSE     | OK12SYMBOL  | EquityInstrmnts   | 2          | 422          | VAL-PRICE-SCALE  | 10.001    | 200        | 0             | 0          |

  @api @fees @custody @recompute @quarterly @messages @reports @CMBO-TC-010
  Scenario: Custody fee daily accrual, back-dated recompute, quarterly posting and messaging/reporting
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'feeBearer'
    And the content type is 'application/json'
    When I send a POST request to '/api/fees/custody/daily-run' with payload
      """
      { "asOfDate": "T" }
      """
    Then the response status should be 202
    And the response body should contain "accrualsCreated" >= 1
    When I send a POST request to '/api/corrections/backdated' with payload
      """
      { "portfolioId": "PF-XXXXXX88220", "tradeDate": "T-10", "effect": "HOLDING_ADJUSTMENT" }
      """
    Then the response status should be 200
    When I send a POST request to '/api/fees/custody/recompute' with payload
      """
      { "fromDate": "T-10", "toDate": "T" }
      """
    Then the response status should be 202
    And the response body should contain "flags" contains "FEE-RECOMPUTE-BACKDATE"
    When I send a POST request to '/api/fees/custody/quarterly-post' with payload
      """
      { "quarterEnd": "Q-END", "submitter": "Maker" }
      """
    Then the response status should be 202
    When I send a POST request to '/api/fees/custody/quarterly-approve' with payload
      """
      { "quarterEnd": "Q-END", "approver": "Checker" }
      """
    Then the response status should be 200
    And the response body should contain "postings" array
    When I send a GET request to '/api/messages/outbox?types=77,425'
    Then the response status should be 200
    And the response body should contain "masked" = true
    When I send a GET request to '/api/reports/RSP34390?quarter=Q-END'
    Then the response status should be 200
    And the response body should contain "totalsByPortfolio" array

  @api @tase1054 @failureHandling @blocks @reversals @idempotency @CMBO-TC-011
  Scenario: TASE 1054 failed/pending trades - enforce manual blocks, cancel with reversals, idempotent 1054 reprocessing
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'boBearer'
    And the content type is 'application/json'
    When I send a POST request to '/api/recon/1051/import' with payload
      """
      {
        "fileName": "1051",
        "records": [
          { "executionId": "S-EXEC-1", "symbol": "TASE:SELL", "side": "SELL", "quantity": 50, "price": 20.00, "tradeDate": "T" },
          { "executionId": "B-EXEC-1", "symbol": "TASE:BUY", "side": "BUY", "quantity": 50, "price": 10.00, "tradeDate": "T" }
        ]
      }
      """
    Then the response status should be 200
    When I send a POST request to '/api/tase/1054/import' with payload
      """
      {
        "fileName": "1054",
        "records": [
          { "executionId": "S-EXEC-1", "status": "FAILED", "reason": "CUSTODIAN_REJECT" },
          { "executionId": "B-EXEC-1", "status": "PENDING", "reason": "CASH_SHORT" }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "failed" = 1
    And the response body should contain "pending" = 1
    When I send a POST request to '/api/blocks' with payload
      """
      { "type": "CASH", "portfolioId": "PF-XXXXXX44221", "amount": 1000.00, "currency": "ILS", "reason": "Failed Sell proceeds" }
      """
    Then the response status should be 201
    When I send a POST request to '/api/blocks' with payload
      """
      { "type": "CUSTODY", "portfolioId": "PF-XXXXXX44221", "securityId": "TASE:BUY", "quantity": 50, "reason": "Pending Buy coverage" }
      """
    Then the response status should be 201
    When I send a POST request to '/api/orders/S-EXEC-1/cancel' with payload
      """
      { "reason": "1054 FAILED", "routeForApproval": true }
      """
    Then the response status should be 202
    When I send a POST request to '/api/orders/S-EXEC-1/approve-cancel' with payload
      """
      { "approver": "Checker" }
      """
    Then the response status should be 200
    And the response body should contain "reversalsPosted" = true
    When I send a POST request to '/api/tase/1054/import' with payload
      """
      {
        "fileName": "1054",
        "records": [
          { "executionId": "S-EXEC-1", "status": "FAILED", "reason": "CUSTODIAN_REJECT" },
          { "executionId": "B-EXEC-1", "status": "PENDING", "reason": "CASH_SHORT" }
        ]
      }
      """
    Then the response status should be 200
    And the response body should contain "duplicatesIgnored" = 2

  @api @fractional @transitDeal @avgPrice @settlement @idempotency @CMBO-TC-012
  Scenario: Fractional order processing - transit deal to bank fraction portfolio, average price, 1052 settlement and idempotency
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'boBearer'
    And the content type is 'application/json'
    When I send a POST request to '/api/orders' with payload
      """
      {
        "portfolioId": "PF-XXXXXX77551",
        "symbol": "TASE:FRAC",
        "side": "SELL",
        "orderType": "FULL_SELL",
        "quantity": 100,
        "executions": [
          { "quantity": 60.0000, "price": 10.00 },
          { "quantity": 39.9999, "price": 10.10 }
        ]
      }
      """
    Then the response status should be 201
    And the response should contain 'orderId'
    When I send a POST request to '/api/batches/FractionalSettlementTransit/run' with payload
      """
      { "asOfDate": "T" }
      """
    Then the response status should be 202
    When I send a GET request to '/api/fractional/transit?orderId={orderId}'
    Then the response status should be 200
    And the response body should contain "fractionQuantity" rounded to 0.0001
    And the response body should contain "averagePrice" rounded to 0.01
    When I send a POST request to '/api/settlement/advice/import' with payload
      """
      { "fileName": "1052", "exchange": "TASE", "advices": [ { "adviceId": "FR-1", "orderId": "{orderId}", "netAmount": 1000.00 } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/batches/FractionalSettlementTransit/run' with payload
      """
      { "asOfDate": "T" }
      """
    Then the response status should be 202
    And the response body should contain "duplicatesIgnored" >= 1

  @api @conversion @ADR @GDR @linkedLegs @settlement @idempotency @CMBO-TC-013
  Scenario: ADR/GDR conversion - linked Delivery Out/In via External Reference 2 and settlement
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'boBearer'
    And the content type is 'application/json'
    When I send a POST request to '/api/transfers' with payload
      """
      {
        "portfolioId": "PF-XXXXXX88002",
        "deliveryType": "LOCAL_TO_ADR",
        "securityId": "TASE:LOC123",
        "quantityLocal": 100,
        "externalRef2": "CONV-REF-001"
      }
      """
    Then the response status should be 201
    And the response should contain 'doId'
    When I send a POST request to '/api/transfers' with payload
      """
      {
        "portfolioId": "PF-XXXXXX88002",
        "deliveryType": "ADR_TO_LOCAL",
        "securityId": "ADR:LOC123",
        "quantityAdr": 200,
        "conversionRatio": "2:1",
        "externalRef2": "CONV-REF-001"
      }
      """
    Then the response status should be 201
    And the response should contain 'diId'
    When I send a POST request to '/api/custodian/foreign/advice/import' with payload
      """
      { "records": [ { "externalRef2": "CONV-REF-001", "securityId": "ADR:LOC123", "quantity": 200 } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/settlement/advice/import' with payload
      """
      { "fileName": "1052", "exchange": "TASE", "advices": [ { "externalRef2": "CONV-REF-001", "securityId": "TASE:LOC123", "quantity": 100, "netAmount": 0.00 } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/batches/StreetSideSettlementForeign/run' with payload
      """
      { "asOfDate": "T+1" }
      """
    Then the response status should be 202
    When I send a POST request to '/api/batches/StreetSideSettlementTASE/run' with payload
      """
      { "asOfDate": "T+1" }
      """
    Then the response status should be 202
    When I send a GET request to '/api/transfers/history?externalRef2=CONV-REF-001'
    Then the response status should be 200
    And the response body should contain "bothLegsSettled" = true
    When I send a POST request to '/api/settlement/advice/import' with payload
      """
      { "fileName": "1052", "exchange": "TASE", "advices": [ { "externalRef2": "CONV-REF-001", "securityId": "TASE:LOC123", "quantity": 100, "netAmount": 0.00 } ] }
      """
    Then the response status should be 200
    And the response body should contain "duplicatesIgnored" = 1

  @api @reconciliation @positions @cash @idempotency @manualResolve @reports @CMBO-TC-015
  Scenario: Positions and cash reconciliation vs 1053, 871/872, Tax Engine, and File 32 with scope removal and idempotency
    Given the API base URL is 'https://api.bank/v1'
    And the authorization token is set to 'reconBearer'
    And the content type is 'application/json'
    When I send a POST request to '/api/recon/1053/import' with payload
      """
      { "fileName": "1053", "records": [ { "portfolio": "PF-XXXXXX99210", "securityId": "TASE:EQ100", "quantity": 100 } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/recon/1053/run' with payload
      """
      { "asOfDate": "T" }
      """
    Then the response status should be 200
    And the response body should contain "posMismatches" >= 1
    When I send a POST request to '/api/recon/871/import' with payload
      """
      { "fileName": "871", "records": [ { "portfolio": "PF-XXXXXX99210", "securityId": "NYSE:ABC", "quantity": 50, "currency": "USD" } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/recon/taxpositions/import' with payload
      """
      { "fileName": "TaxPositions", "records": [ { "portfolio": "PF-XXXXXX99210", "securityId": "TASE:EQ100", "quantity": 100 } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/recon/cash32/import' with payload
      """
      { "fileName": "32", "records": [ { "nostro": "NOSTRO-ILS", "netAmount": 100000.00, "currency": "ILS" } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/recon/cash872/import' with payload
      """
      { "fileName": "872", "records": [ { "nostro": "NOSTRO-USD", "instrument": "NYSE:ABC", "side": "BUY", "netAmount": 5000.00, "currency": "USD" } ] }
      """
    Then the response status should be 200
    When I send a POST request to '/api/recon/cash32/run' with payload
      """
      { "asOfDate": "T" }
      """
    Then the response status should be 200
    And the response body should contain "cashDiffs" >= 1
    When I send a POST request to '/api/recon/manual-resolve' with payload
      """
      { "module": "positions", "key": { "portfolio": "PF-XXXXXX99210", "securityId": "TASE:EQ100" }, "action": "REMOVE_FROM_SCOPE", "reason": "Manual movement linked" }
      """
    Then the response status should be 200
    And the response body should contain "removedFromAutoRecon" = true
    When I send a POST request to '/api/recon/1053/run' with payload
      """
      { "asOfDate": "T" }
      """
    Then the response status should be 200
    And the response body should contain "idempotent" = true
    When I send a GET request to '/api/reports/recon/exceptions?modules=positions,cash'
    Then the response status should be 200
    And the response body should contain "masked" = true

  # UI Tests

  @ui @transfer @makerChecker @multiBeneficiary @CAblock @CMBO-TC-004
  Scenario Outline: Within-bank securities transfer with CA ex-date block, 60/40 split and maker-checker approval
    Given I am logged in to the web application as 'Maker'
    And I navigate to 'Security Transfer'
    And I select security '<securityId>' from 'Select Security'
    When I proceed to add beneficiaries
    And I choose transfer type 'Within Bank' and case 'Transfer between relatives' with sub-case 'Spouse of a sister/brother'
    And I enter fractional quantity '100.1234'
    And I add two beneficiaries with percentages '60' and '40'
    And I click 'Preview'
    Then I should see '<expectedMessage>'
    When I click 'Release'
    And I assign to 'Checker1'
    And as 'Checker1' I approve the transfer in 'My Queue'
    Then the transfer status should be 'Authorized'
    When the 'WithinBankTransferSettlementEOD' batch completes
    Then the Security Transfer History should show 'Settled' with two split lines

    Examples:
      | securityId  | expectedMessage                                            |
      | TASE:CA-ON  | A corporate action is pending with ExDate today; Security Transfer is not allowed for this security |
      | TASE:EQ-999 | Commission preview displayed; percentages total 100%       |

  @ui @entitlements @marketData @level2Block @ETFPath @CMBO-TC-007
  Scenario Outline: Entitlement-controlled display and Level 2 blocking with ETF dual-path prompt
    Given I am logged in to the web application as 'Branch Dealer' without live foreign entitlements
    And I open 'Market Watch'
    When I observe the row for '<symbol>'
    Then I should see '<banner>'
    When I open 'Get Quote' for '<symbol>'
    And I attempt to view 'Level 2'
    Then I should see '<l2Message>'
    When I place an order from 'ETF List' for 'TASE:ETF229'
    And I choose 'Mutual Fund Order Path' on the alert prompt
    Then I should see 'Additional commission indicator' on Preview

    Examples:
      | symbol     | banner         | l2Message                                      |
      | TASE:AAA   | Live           | Level 2 is available                           |
      | NYSE:XYZ   | Delayed 15m    | Level 2 is not available for your subscription |

  @ui @authorization @POA @MUHomeBranch @nostroTimeout @CMBO-TC-014
  Scenario: POA restrictions, MU/home-branch validation, maker-checker pool assignment, and nostro timeout auto-cancel
    Given I am logged in to the web application as 'POA-User'
    And I am on the 'Order Entry' page
    When I attempt to place a 'Limit Buy' via channel 'Internet'
    Then I should see 'POA orders are not permitted via this channel; approval required from another party'
    When I switch to 'FO' channel as 'Maker' and create the same order
    Then I should see an approval popup requiring assignment to a checker
    When I assign to 'Checker1'
    And I login as a user from a different MU and attempt the same order
    Then I should see 'Kindly visit your home branch to trade'
    When I login as 'Checker1' and open 'My Queue'
    And I attempt to approve an order initiated by myself
    Then I should see 'Segregation of duties prevents self-approval'
    When I increase order amount to exceed maker limit and submit to 'Pool'
    Then it should appear in 'Pool Queue' with alert '610070 Maker Limit Exceeded'
    When I approve from 'Pool Queue' as 'Checker2'
    Then the order status should progress to 'Authorized' and 'Placed with Market'
    When I place a second order on a nostro-managed account and it remains open past timeout
    And I run 'NostroOpenOrderTimeoutJob'
    Then the order should be 'Cancelled by timeout' with alert 'NOSTRO-TIMEOUT-CANCEL'
```