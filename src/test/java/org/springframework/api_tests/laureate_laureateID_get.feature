# ********RoostGPT********

# Test generated by RoostGPT for test claude-karate-apitest using AI Type Claude AI and AI Model claude-3-opus-20240229
# 
# Feature file generated for /laureate/{laureateID}_get for http method type GET 
# RoostTestHash=3a8d014c99
# 
# 

# ********RoostGPT********
Feature: Test /2.1/laureate/{laureateID} endpoint

  Background:
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:4010')
    * url urlBase
    * def authToken = karate.properties['AUTH_TOKEN']
    * configure headers = { 'Authorization': '#(authToken)' }

  Scenario Outline: Get laureate information by ID
    Given path '/2.1/laureate/<laureateID>'
    When method GET
    Then status 200
    And match response == { laureate: '#(laureateSchema)' }
    And match header Content-Type == 'application/json'

    Examples:
      | read('laureate_laureateID_get.csv') |

  Scenario: Get laureate information with invalid ID
    Given path '/2.1/laureate/0'
    When method GET
    Then status 400
    And match response ==
      """
      {
        code: '400',
        message: 'Bad request.The request could not be understood by the server due to malformed syntax, modifications needed.'
      }
      """
    And match header Content-Type == 'application/json'

  Scenario: Get laureate information with non-existent ID
    Given path '/2.1/laureate/999999'
    When method GET
    Then status 404
    And match response ==
      """
      {
        code: '404',
        message: 'Not Found. The requested resource could not be found but may be available again in the future.'
      }
      """
    And match header Content-Type == 'application/json'

  Scenario: Get laureate information with invalid ID format
    Given path '/2.1/laureate/abc'
    When method GET
    Then status 422
    And match response ==
      """
      {
        code: '422',
        message: 'Unprocessable Entity. The request was well-formed but was unable to be followed due to semantic errors.'
      }
      """
    And match header Content-Type == 'application/json'
    * def laureateSchema =
      """
      {
        id: '#number',
        laureateIfPerson: '##(personSchema)',
        laureateIfOrg: '##(orgSchema)',
        nobelPrizes: '#[] #(nobelPrizeSchema)'
      }
      """
    * def personSchema =
      """
      {
        knownName: '#(multiLangSchema)',
        givenName: '#(multiLangSchema)', 
        familyName: '#(multiLangSchema)',
        fullName: '#(multiLangSchema)',
        filename: '#string',
        penname: '##string',
        gender: '#string', 
        birth: '#(eventSchema)',
        death: '##(eventSchema)'
      }
      """
    * def orgSchema =
      """
      {
        orgName: '#(multiLangSchema)',
        nativeName: '##string',
        acronym: '##string', 
        founded: '##(eventSchema)',
        dissolution: '##(eventSchema)',
        headquarters: '##(placeSchema)',
        wikipedia: '##(wikiSchema)',
        wikidata: '##(wikidataSchema)',
        sameAs: '##[] #string',
        links: '##[] #(linkSchema)'
      }
      """
    * def nobelPrizeSchema =
      """
      {
        awardYear: '#number',
        category: '#(multiLangSchema)',
        categoryFullName: '#(multiLangSchema)',
        sortOrder: '#string',
        portion: '#string',
        dateAwarded: '##string',
        prizeStatus: '#string',
        motivation: '#(multiLangSchema)', 
        prizeAmount: '#number',
        prizeAmountAdjusted: '#number',
        affiliations: '##[] #(affiliationSchema)',
        residences: '##[] #(placeSchema)',
        links: '##[] #(linkSchema)'
      }
      """
    * def multiLangSchema =
      """
      {
        en: '##string',
        se: '##string'
      }
      """
    * def eventSchema =
      """
      {
        date: '##string',
        place: '#(placeSchema)'  
      }
      """
    * def placeSchema =
      """
      { 
        city: '#(multiLangSchema)',
        country: '#(multiLangSchema)',
        cityNow: '##(multiLangSchema)',
        countryNow: '##(multiLangSchema)',
        continent: '##(multiLangSchema)',
        locationString: '##(multiLangSchema)'
      }
      """
    * def wikiSchema =
      """
      {
        slug: '#string',
        english: '#string'
      }
      """
    * def wikidataSchema =
      """
      {
        id: '#string',
        url: '#string' 
      }
      """
    * def linkSchema =
      """
      {
        rel: '#string',
        href: '#string',
        action: '#string',
        types: '#string'
      }
      """
    * def affiliationSchema =
      """
      {
        name: '#(multiLangSchema)',
        nameNow: '##(multiLangSchema)',
        nativeName: '##string', 
        city: '#(multiLangSchema)',
        country: '#(multiLangSchema)',
        cityNow: '##(multiLangSchema)',
        countryNow: '##(multiLangSchema)',
        locationString: '##(multiLangSchema)'
      }
      """
