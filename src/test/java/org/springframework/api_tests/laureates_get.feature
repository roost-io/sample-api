# ********RoostGPT********

# Test generated by RoostGPT for test claude-karate-apitest using AI Type Claude AI and AI Model claude-3-opus-20240229
# 
# Feature file generated for /laureates_get for http method type GET 
# RoostTestHash=bb9ad621b1
# 
# 

# ********RoostGPT********
Feature: Nobel Prize Laureates API

  Background:
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:4010')
    * url urlBase
    * def authToken = karate.properties['AUTH_TOKEN']
    * configure headers = { 'Authorization': '#(authToken)' }

  Scenario: Get all Nobel Prize Laureates
    Given path '/2.1/laureates'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains { id: '#number', nobelPrizes: '#[_ > 0]' }
    And match response.meta.count == '#number'

  Scenario: Get Nobel Prize Laureates with pagination
    Given path '/2.1/laureates'
    And param offset = 10
    And param limit = 20
    When method GET
    Then status 200
    And match response.laureates == '#[20]'
    And match response.meta.offset == 10
    And match response.meta.limit == 20

  Scenario: Get Nobel Prize Laureates sorted by name in descending order
    Given path '/2.1/laureates'
    And param sort = 'desc'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match response.meta.sort == 'desc'

  Scenario: Get Nobel Prize Laureate by ID
    Given path '/2.1/laureates'
    And param ID = 123
    When method GET
    Then status 200
    And match response.laureates == '#[1]'
    And match response.laureates[0].id == 123

  Scenario: Get Nobel Prize Laureates by name
    Given path '/2.1/laureates'
    And param name = 'John'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains { laureateIfPerson: { knownName: { en: '#regex John' } } }

  Scenario: Get Nobel Prize Laureates by gender
    Given path '/2.1/laureates'
    And param gender = 'female'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains { laureateIfPerson: { gender: 'female' } }

  Scenario: Get Nobel Prize Laureates by motivation
    Given path '/2.1/laureates'
    And param motivation = 'peace'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates[*].nobelPrizes[*].motivation.en contains 'peace'

  Scenario: Get Nobel Prize Laureates by affiliation
    Given path '/2.1/laureates'
    And param affiliation = 'University'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates[*].nobelPrizes[*].affiliations[*].name.en contains 'University'

  Scenario: Get Nobel Prize Laureates by residence
    Given path '/2.1/laureates'
    And param residence = 'USA'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates[*].nobelPrizes[*].residences[*].country.en contains 'USA'

  Scenario: Get Nobel Prize Laureates by birth date
    Given path '/2.1/laureates'
    And param birthDate = 1950
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains { laureateIfPerson: { birth: { date: '#regex 1950' } } }

  Scenario: Get Nobel Prize Laureates by birth date range
    Given path '/2.1/laureates'
    And param birthDate = 1950
    And param birthDateTo = 1960
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfPerson: {
          birth: {
            date: '#? _ >= "1950" && _ <= "1960"'
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by death date
    Given path '/2.1/laureates'
    And param deathDate = 2000
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains { laureateIfPerson: { death: { date: '#regex 2000' } } }

  Scenario: Get Nobel Prize Laureates by death date range
    Given path '/2.1/laureates'
    And param deathDate = 2000
    And param deathDateTo = 2010
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfPerson: {
          death: {
            date: '#? _ >= "2000" && _ <= "2010"'
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by founded date
    Given path '/2.1/laureates'
    And param foundedDate = 1900
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains { laureateIfOrg: { founded: { date: '#regex 1900' } } }

  Scenario: Get Nobel Prize Laureates by birth city
    Given path '/2.1/laureates'
    And param birthCity = 'New York'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfPerson: {
          birth: {
            place: {
              city: {
                en: 'New York'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by birth country
    Given path '/2.1/laureates'
    And param birthCountry = 'USA'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfPerson: {
          birth: {
            place: {
              country: {
                en: 'USA'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by birth continent
    Given path '/2.1/laureates'
    And param birthContinent = 'North America'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfPerson: {
          birth: {
            place: {
              continent: {
                en: 'North America'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by death city
    Given path '/2.1/laureates'
    And param deathCity = 'Paris'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfPerson: {
          death: {
            place: {
              city: {
                en: 'Paris'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by death country
    Given path '/2.1/laureates'
    And param deathCountry = 'France'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfPerson: {
          death: {
            place: {
              country: {
                en: 'France'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by death continent
    Given path '/2.1/laureates'
    And param deathContinent = 'Europe'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfPerson: {
          death: {
            place: {
              continent: {
                en: 'Europe'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by founded city
    Given path '/2.1/laureates'
    And param foundedCity = 'Geneva'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfOrg: {
          founded: {
            place: {
              city: {
                en: 'Geneva'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by founded country
    Given path '/2.1/laureates'
    And param foundedCountry = 'Switzerland'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfOrg: {
          founded: {
            place: {
              country: {
                en: 'Switzerland'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by founded continent
    Given path '/2.1/laureates'
    And param foundedContinent = 'Europe'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfOrg: {
          founded: {
            place: {
              continent: {
                en: 'Europe'
              }
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by headquarters city
    Given path '/2.1/laureates'
    And param headquartersCity = 'New York'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfOrg: {
          headquarters: {
            cityNow: {
              en: 'New York'
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by headquarters country
    Given path '/2.1/laureates'
    And param headquartersCountry = 'USA'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfOrg: {
          headquarters: {
            countryNow: {
              en: 'USA'
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by headquarters continent
    Given path '/2.1/laureates'
    And param headquartersContinent = 'North America'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates contains
      """
      {
        laureateIfOrg: {
          headquarters: {
            continent: {
              en: 'North America'
            }
          }
        }
      }
      """

  Scenario: Get Nobel Prize Laureates by Nobel Prize year
    Given path '/2.1/laureates'
    And param nobelPrizeYear = 2000
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates[*].nobelPrizes[*].awardYear == 2000

  Scenario: Get Nobel Prize Laureates by Nobel Prize year range
    Given path '/2.1/laureates'
    And param nobelPrizeYear = 2000
    And param yearTo = 2010
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates[*].nobelPrizes[*].awardYear >= 2000
    And match each response.laureates[*].nobelPrizes[*].awardYear <= 2010

  Scenario: Get Nobel Prize Laureates by Nobel Prize category
    Given path '/2.1/laureates'
    And param nobelPrizeCategory = 'phy'
    When method GET
    Then status 200
    And match response.laureates == '#[_ > 0]'
    And match each response.laureates[*].nobelPrizes[*].category.en == 'Physics'

  Scenario: Get Nobel Prize Laureates in CSV format
    Given path '/2.1/laureates'
    And param format = 'csv'
    When method GET
    Then status 200
    And match header Content-Type contains 'text/csv'

  Scenario: Get Nobel Prize Laureates in CSV format with Swedish language
    Given path '/2.1/laureates'
    And param format = 'csv'
    And param csvLang = 'se'
    When method GET
    Then status 200
    And match header Content-Type contains 'text/csv'

  Scenario: Get Nobel Prize Laureates with invalid query parameter
    Given path '/2.1/laureates'
    And param invalid = 'value'
    When method GET
    Then status 400
    And match response.code == '400'
    And match response.message contains 'Bad request'

  Scenario: Get Nobel Prize Laureate with non-existent ID
    Given path '/2.1/laureates'
    And param ID = 999999
    When method GET
    Then status 404
    And match response.code == '404'
    And match response.message contains 'Not Found'