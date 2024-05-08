# ********RoostGPT********

# Test generated by RoostGPT for test MiniProjects using AI Type Open AI and AI Model gpt-4-1106-preview
# 
# Feature file generated for /aisp/account-consents_post for http method type POST 
# RoostTestHash=3a9edd08a1
# 
# 

# ********RoostGPT********
Feature: Account Consent Setup

  Background:
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:8080')
    * url urlBase
    * def authToken = karate.properties['AUTH_TOKEN']

  Scenario Outline: Create account consent with valid input payload
    Given path 'aisp/account-consents'
    And header Authorization = 'Bearer ' + authToken
    And header Content-Type = 'application/json'
    And header x-fapi-auth-date = <x-fapi-auth-date>
    And header x-fapi-customer-ip-address = <x-fapi-customer-ip-address>
    And header x-fapi-interaction-id = <x-fapi-interaction-id>
    And header Accept-Language = <Accept-Language>
    And request 
    """
    <body>
    """
    When method POST
    Then status 201
    And match responseHeaders['x-fapi-interaction-id'] == <x-fapi-interaction-id>
    And match response.data.consentId != null
    And match response.data.creationDate != null
    And match response.data.status == 'PendingAuthorise'
    And match response.data.permissions contains only <body>.data.permissions
    And match response.data.expirationDate == <body>.data.expirationDate
    And match response.data.transactionFromDate == <body>.data.transactionFromDate
    And match response.data.transactionToDate == <body>.data.transactionToDate
    And match response.links.self != null

    Examples:
      | x-fapi-auth-date                | x-fapi-customer-ip-address | x-fapi-interaction-id    | Accept-Language | body                                                                                                                                       |
      | 'Sun, 10 Sep 2017 19:43:31 UTC' | '169.254.169.254'          | 'unique-interaction-id'  | 'en-HK'         | { "data": { "permissions": ["ReadAccountBalance"], "expirationDate": "2017-04-05T00:07:00Z" }}                                           |
      | 'Sun, 10 Sep 2017 19:43:31 UTC' | '169.254.169.254'          | 'unique-interaction-id2' | 'zh-HK'         | { "data": { "permissions": ["ReadAccountStatus", "ReadAccountTransaction"], "transactionFromDate": "2017-04-05T00:07:00Z", "transactionToDate": "2017-05-05T00:07:00Z" }} |

  Scenario: Attempt to create account consent with invalid input payload
    Given path 'aisp/account-consents'
    And header Authorization = 'Bearer ' + authToken
    And header Content-Type = 'application/json'
    And header x-fapi-auth-date = 'Sun, 10 Sep 2017 19:43:31 UTC'
    And header x-fapi-customer-ip-address = '169.254.169.254'
    And header x-fapi-interaction-id = 'unique-interaction-id'
    And header Accept-Language = 'en-HK'
    And request 
    """
    { "data": { "invalidField": "invalidValue" }}
    """
    When method POST
    Then status 400
    And match responseHeaders['x-fapi-interaction-id'] == 'unique-interaction-id'
    And match response.id != null
    And match response.errors[*].code contains 'OB.Field.Unexpected'
    And match response.errors[*].causes contains 'A mandatory field isn\'t supplied'

  Scenario: Attempt to create account consent without authorization
    Given path 'aisp/account-consents'
    And header Content-Type = 'application/json'
    And header x-fapi-auth-date = 'Sun, 10 Sep 2017 19:43:31 UTC'
    And header x-fapi-customer-ip-address = '169.254.169.254'
    And header x-fapi-interaction-id = 'unique-interaction-id'
    And header Accept-Language = 'en-HK'
    And request 
    """
    { "data": { "permissions": ["ReadAccountBalance"], "expirationDate": "2017-04-05T00:07:00Z" }}
    """
    When method POST
    Then status 401
    And match responseHeaders['x-fapi-interaction-id'] == 'unique-interaction-id'
    And match response.message != null
