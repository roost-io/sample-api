# ********RoostGPT********

# Test generated by RoostGPT for test karate-sample-api using AI Type Azure Open AI and AI Model roostgpt-4-32k
# 
# Feature file generated for /nobelPrize/{category}/{year}_get for http method type GET 
# RoostTestHash=9818bf6b39
# 
# 

# ********RoostGPT********
# I have concentrated on authorization, request url, request method,  parameters, and responses in this feature file.

Feature: Testing /2.1/nobelPrize/{category}/{year} functionality 

  Background: 
    * def auth_token = karate.properties['AUTH_TOKEN']
    * configure headers = {Authorization: '#(auth_token)'}
    * def urlBase = karate.properties['url.base'] || 'http://localhost:8080'
    * url urlBase

  Scenario Outline: Verify the correctness of the API responses
    Given path '2.1/nobelPrize/', '<category>', '<year>'
    When method get
    Then status <status_code>
    And match response == {code: '#(code)', message: '#string'}

    Examples: 
      | category      | year      | status_code | code     | 
      | 'phy'         | 1901      | 200         | '200'    |
      | 'med'         | 2000      | 200         | '200'    | 
      | 'Invalid'     | 1901      | 400         | '400'    |
      | ''            | 1901      | 400         | '400'    |
      | 'phy'         | 9999      | 404         | '404'    |
      | 'phy'         | 'Invalid' | 422         | '422'    |

Scenario Outline: Verify response with invalid auth_token
    Given path '2.1/nobelPrize/', '<category>', '<year>'
    And configure headers = { Authorization: '#(invalid_auth_token)' }
    When method get
    Then status 401
    And match response contains { code:'#(string)', message:'Invalid token' }

    Examples: 
      | category  | year | invalid_auth_token | 
      | 'phy'     | 1901 | 'InvalidToken'     |
      | 'phy'     | 1901 | ''                 |
