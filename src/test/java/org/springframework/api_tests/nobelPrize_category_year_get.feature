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
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:8080')
    * url urlBase
    * def authToken = karate.properties['AUTH_TOKEN']

  Scenario Outline: Get Nobel Prize information by category and year
    Given path '/2.1/nobelPrize/<category>/<year>'
    And header Authorization = authToken
    When method GET
    Then status 200
    And match response.nobelPrize.awardYear == <year>
    And match response.nobelPrize.category.en == '#string'
    And match response.nobelPrize.categoryFullName.en == '#string'
    And match response.nobelPrize.dateAwarded == '#regex \\d{4}-\\d{2}-\\d{2}'
    And match response.nobelPrize.prizeAmount == '#number'
    And match response.nobelPrize.prizeAmountAdjusted == '#number'
    And match response.nobelPrize.topMotivation.en == '#string'
    And match each response.nobelPrize.laureates ==
      """
      {
        id: '#number',
        name: {
          en: '#string'
        },
        portion: '#regex (1|1/2|1/3|1/4)',
        sortOrder: '#regex (1|2|3)',
        motivation: {
          en: '#string'
        },
        links: '#array'
      }
      """

    Examples:
      | category | year |
      | che      | 1901 |
      | eco      | 2010 |
      | lit      | 1950 |
      | pea      | 2000 |
      | phy      | 1980 |
      | med      | 1990 |

  Scenario Outline: Get Nobel Prize information with invalid category or year
    Given path '/2.1/nobelPrize/<category>/<year>'
    And header Authorization = authToken
    When method GET
    Then status 400
    And match response ==
      """
      {
        code: '#string',
        message: '#string'
      }
      """

    Examples:
      | category | year  |
      | invalid  | 1901  |
      | che      | 1800  |
      | eco      | 99999 |

  Scenario: Get Nobel Prize information with missing authorization token
    Given path '/2.1/nobelPrize/che/1901'
    When method GET
    Then status 401
