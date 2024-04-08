# ********RoostGPT********

# Test generated by RoostGPT for test karate-employee-api-test using AI Type Azure Open AI and AI Model roostgpt-4-32k
# 
# Feature file generated for /employees_post for http method type POST 
# RoostTestHash=b517afeac4
# 
# 

# ********RoostGPT********
Feature: API Test Suite for Employee API

Background: 
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:8080')
    * url urlBase
    * def authHeader = { Authorization: '#(karate.properties['AUTH_TOKEN'])' }
    * configure headers = authHeader

# Scenario for testing POST operation API - Add new employee
Scenario Outline: Verifying POST API adds an employee to the system

    Given path "/employees"
    And request { id: '#(id)', name: '#(name)', email: '#(email)', jobTitle: '#(jobTitle)'}
    When method post
    Then status 201
    And match response == { description: '#(description)' }

    Examples:
    | id                                    | name         | email                | jobTitle        | description         |
    | 'd290f1ee-6c54-4b01-90e6-d701748f0851' | 'John Smith' | 'john.smith@acme-corp.com' | 'System Analyst' | 'employee created' |

# Scenario for testing POST operation API - Add new employee with invalid input
Scenario Outline: Verifying POST API with invalid input returns 400

    Given path "/employees"
    And request { id: '#(id)', name: '#(name)', email: '#(email)', jobTitle: '#(jobTitle)'}
    When method post
    Then status 400
    And match response == { description: '#(description)' }

    Examples:
    | id      | name | email | jobTitle | description                  |
    | '1234'  | ' ' | ' '  | ' '  | 'invalid input, object invalid' |

# Scenario to test duplicate employee addition
Scenario Outline: Verifying POST API with existing employee returns 409

    Given path "/employees"
    And request { id: '#(id)', name: '#(name)', email: '#(email)', jobTitle: '#(jobTitle)'}
    When method post
    Then status 409
    And match response == { description: '#(description)' }

    Examples:
    | id                                    | name         | email                | jobTitle        | description                    |
    | 'd290f1ee-6c54-4b01-90e6-d701748f0851' | 'John Smith' | 'john.smith@acme-corp.com' | 'System Analyst' | 'an existing employee already exists' |
