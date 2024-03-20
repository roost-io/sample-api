# ********RoostGPT********

# Test generated by RoostGPT for test azure-karate-apitest using AI Type Azure Open AI and AI Model roostgpt-4-32k
# 
# Feature file generated for /laureate/{laureateID}_get for http method type GET 
# RoostTestHash=e702c0f931
# 
# 

# ********RoostGPT********
Feature: Retrieve laureate information

Background: 
* def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:8080') 
* url urlBase

Scenario: Retrieve laureate information for valid laureateID 
   Given path '/2.1/laureate/', '#(laureateID)' 
   And header Authorization = karate.properties['AUTH_TOKEN'] 
   When method get 
   Then status 200 
   And match response == { #add expected response schema here}

Scenario Outline: Test various error codes with invalid input
   Given path '/2.1/laureate/' , '<laureateID>'
   And header Authorization = karate.properties['AUTH_TOKEN'] 
   When method get 
   Then status <status_code>

Examples:
| laureateID | status_code |
| 0          | 400         |
| abc        | 422         |
| -123       | 422         |
| null       | 400         |

