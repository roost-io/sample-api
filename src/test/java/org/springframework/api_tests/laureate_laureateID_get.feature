# ********RoostGPT********

# Test generated by RoostGPT for test karate-sample-api using AI Type Azure Open AI and AI Model roostgpt-4-32k
# 
# Feature file generated for /laureate/{laureateID}_get for http method type GET 
# RoostTestHash=e702c0f931
# 
# 

# ********RoostGPT********
Feature: Testing Nobel Prize Laureate API

Background:
  * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:8080')
  * url urlBase

Scenario Outline: Test Laureate API endpoint with valid laureateID
  Given path '2.1/laureate/', <laureateID>
  When method get
  Then status 200
  And match response.laureate.id == <laureateID>
  And match response.laureate.laureateIfPerson.* == '#notnull'

Examples:
  | laureateID |
  | 1          |
  | 456        |
  | 789        |

Scenario Outline: Test Laureate API endpoint with invalid laureateID
  Given path '2.1/laureate/', <laureateID>
  When method get
  Then status 404
  And match response.code == '404'
  And match response.message == 'There is not Laureate born that date'

Examples:
  | laureateID |
  | 0          |
  | -1         |
  | 10.5       |

Scenario Outline: Test Laureate API endpoint with non-integer laureateID
  Given path '2.1/laureate/', <laureateID>
  When method get
  Then status 400
  And match response.code == '400'
  And match response.message == 'There is not Laureate born that date'

Examples:
  | laureateID     |
  | 'hello'        |
  | '123abc'       |
  | '%@#!&^%'      |
