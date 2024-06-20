# ********RoostGPT********

# Test generated by RoostGPT for test claude-karate-apitest using AI Type Claude AI and AI Model claude-3-opus-20240229
# 
# Feature file generated for /nobelPrize/{category}/{year}_get for http method type GET 
# RoostTestHash=adfce3f1d2
# 
# 

# ********RoostGPT********
Feature: Nobel Prize API

  Background:
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:4010')
    * url urlBase
    * configure headers = { 'Authorization': '#(karate.properties["AUTH_TOKEN"])' }

  Scenario Outline: Get Nobel Prize information by category and year
    Given path '/2.1/nobelPrize/<category>/<year>'
    When method GET
    Then status 200
    And match response.nobelPrize.awardYear == <year>
    And match response.nobelPrize.category.en == '#string'
    And match response.nobelPrize.categoryFullName.en == '#string'
    And match response.nobelPrize.dateAwarded == '#string'
    And match response.nobelPrize.prizeAmount == '#number'
    And match response.nobelPrize.prizeAmountAdjusted == '#number'
    And match response.nobelPrize.topMotivation.en == '#string'
    And match response.nobelPrize.laureates == '#array'
    And match each response.nobelPrize.laureates contains { id: '#number', name: { en: '#string' }, portion: '#string', sortOrder: '#string', motivation: { en: '#string' }, links: '#array' }
    And match responseHeaders['Content-Type'][0] contains 'application/json'

    Examples:
      | read('nobelPrize_category_year_get.csv') |

  Scenario Outline: Get Nobel Prize information with invalid category
    Given path '/2.1/nobelPrize/<invalidCategory>/<year>'
    When method GET
    Then status 400
    And match response.code == '404'
    And match response.message == 'There is not Laureate born that date'

    Examples:
      | read('nobelPrize_category_year_get.csv') |

  Scenario Outline: Get Nobel Prize information with invalid year
    Given path '/2.1/nobelPrize/<category>/<invalidYear>'
    When method GET
    Then status 400
    And match response.code == '404'
    And match response.message == 'There is not Laureate born that date'

    Examples:
      | read('nobelPrize_category_year_get.csv') |

  Scenario: Get Nobel Prize information with unsupported media type
    Given path '/2.1/nobelPrize/che/1901'
    And header Accept = 'application/xml'
    When method GET
    Then status 406

  Scenario: Get Nobel Prize information with invalid endpoint
    Given path '/2.1/invalidEndpoint'
    When method GET
    Then status 404