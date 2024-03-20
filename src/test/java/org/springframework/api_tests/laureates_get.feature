# ********RoostGPT********

# Test generated by RoostGPT for test azure-karate-apitest using AI Type Azure Open AI and AI Model roostgpt-4-32k
# 
# Feature file generated for /laureates_get for http method type GET 
# RoostTestHash=ff433d7857
# 
# 

# ********RoostGPT********
Feature: Nobel Laureates API Tests

Background:
* def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:8080')
* url urlBase
* def authToken = karate.properties['AUTH_TOKEN']
* configure headers = {Authorization: '#(authToken)'}

Scenario: Verify the List all Laureates endpoint
    Given path '/2.1/laureates'
    When method get
    Then status 200
    And match each response.laureates contains { id:'#number', id: '#exist' }
    And match response.meta == '#notnull'

Scenario: Verify the search Laureates by gender endpoint
    Given path '/2.1/laureates'
    And param gender = 'female'
    When method get
    Then status 200
    And match each response.laureates contains { id:'#number', laureateIfPerson: {gender: 'female'} }

Scenario: Verify the search Laureates by their birth year
    Given path '/2.1/laureates'
    And param birthDate = '1990'
    When method get
    Then status 200
    And match each response.laureates contains { id:'#number', laureateIfPerson: {birth: {date:'#regex[1990-.*]'}} }

@ignore
Scenario: Verify Laureates search endpoint with invalid inputs
    Given path '/2.1/laureates'
    And param gender = 'unknown'
    When method get
    Then status 400

@ignore
Scenario: Verify Laureates search endpoint for 404 - Not Found
    Given path '/2.1/laureates'
    And param gender = 'robot'
    When method get
    Then status 404

