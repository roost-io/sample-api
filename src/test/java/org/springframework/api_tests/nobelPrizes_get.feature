# ********RoostGPT********

# Test generated by RoostGPT for test claude-karate-apitest using AI Type Claude AI and AI Model claude-3-opus-20240229
# 
# Feature file generated for /nobelPrizes_get for http method type GET 
# RoostTestHash=4940f5c55b
# 
# 

# ********RoostGPT********
Feature: Nobel Prize API

  Background:
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:4010')
    * url urlBase

  Scenario: Get all Nobel Prizes
    Given path '/2.1/nobelPrizes'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    When method GET
    Then status 200
    And match response.nobelPrizes == '#array'
    And match each response.nobelPrizes contains
      """
      {
        awardYear: '#number',
        category: '#object',
        categoryFullName: '#object',
        dateAwarded: '#string',
        prizeAmount: '#number',
        prizeAmountAdjusted: '#number',
        topMotivation: '#object',
        laureates: '#array'
      }
      """
    And match response.meta == '#object'
    And match response.links == '#array'

  Scenario Outline: Get Nobel Prizes with query parameters
    Given path '/2.1/nobelPrizes'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param offset = <offset>
    And param limit = <limit>
    And param sort = <sort>
    And param nobelPrizeYear = <nobelPrizeYear>
    And param nobelPrizeCategory = <nobelPrizeCategory>
    And param format = <format>
    When method GET
    Then status 200
    And match response.nobelPrizes == '#array'
    And match each response.nobelPrizes contains
      """
      {
        awardYear: <nobelPrizeYear>,
        category: '#object',
        categoryFullName: '#object',
        dateAwarded: '#string',
        prizeAmount: '#number',
        prizeAmountAdjusted: '#number',
        topMotivation: '#object',
        laureates: '#array'
      }
      """
    And match response.meta == '#object'
    And match response.links == '#array'

    Examples:
      | read('nobelPrizes_get.csv') |

  Scenario: Get Nobel Prizes with invalid query parameters
    Given path '/2.1/nobelPrizes'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param offset = 'invalid'
    When method GET
    Then status 400
    And match response ==
      """
      {
        code: '#string',
        message: '#string'
      }
      """

  Scenario: Get Nobel Prizes with non-existent resource
    Given path '/2.1/nobelPrizes/invalid'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    When method GET
    Then status 404
    And match response ==
      """
      {
        code: '#string',
        message: '#string'
      }
      """

  Scenario: Get Nobel Prizes with semantic errors
    Given path '/2.1/nobelPrizes'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param nobelPrizeYear = 1800
    When method GET
    Then status 422
    And match response ==
      """
      {
        code: '#string',
        message: '#string'
      }
      """
