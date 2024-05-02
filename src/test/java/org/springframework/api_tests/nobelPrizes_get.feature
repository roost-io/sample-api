# ********RoostGPT********

# Test generated by RoostGPT for test karate-sample-api using AI Type Azure Open AI and AI Model roostgpt-4-32k
# 
# Feature file generated for /nobelPrizes_get for http method type GET 
# RoostTestHash=977dd819cb
# 
# 

# ********RoostGPT********
Feature: Nobel Prizes

    Background:
        * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:8080')
        * url urlBase

    Scenario Outline: Issues a successful GET request to GET all or query specific Nobel Prizes
        Given path '/2.1/nobelPrizes'
        And headers { Authorization : '#(karate.properties['AUTH_TOKEN'])' }
        And params { offset: '<offset>', limit: '<limit>', sort: '<sort>', nobelPrizeYear: '<nobelPrizeYear>', yearTo: '<yearTo>', nobelPrizeCategory: '<nobelPrizeCategory>', format: '<format>', csvLang: '<csvLang>' }
        When method get
        Then status 200
        And match response == { nobelPrizes: '#array', meta: '#object', links: '#array' }
        And match each response.nobelPrizes.laureates contains { id: '#number', name: '#object', portion: '#string', sortOrder: '#string', motivation: '#object', links: '#array', description: '#string' }
        And match response.meta == { offset: '#number', limit: '#number', nobelPrizeYear: '#number', yearTo: '#number', nobelPrizeCategory: '#string', count: '#number' }
        And match each response.links contains { first: '#string', prev: '#string', self: '#string', next: '#string', last: '#string' }

    Examples: 
        |offset|limit|sort|nobelPrizeYear|yearTo|nobelPrizeCategory|format|csvLang|
        |1     |10   |desc|2000          |2010  |phy               |json  |en     | 
        |2     |20   |asc |1990          |2000  |che               |json  |en     |

    Scenario Outline: Issues an unsuccessful GET request due to bad request
        Given path '/2.1/nobelPrizes'
        And headers { Authorization : '#(karate.properties['AUTH_TOKEN'])' }
        And params { offset: '<offset>', limit: '<limit>', sort: '<sort>', nobelPrizeYear: '<nobelPrizeYear>', yearTo: '<yearTo>', nobelPrizeCategory: '<nobelPrizeCategory>', format: '<format>', csvLang: '<csvLang>' }
        When method get
        Then status 400
        And match response contains { code: '#string', message: '#string' }

    Examples: 
        |offset|limit|sort|nobelPrizeYear|yearTo |nobelPrizeCategory|format|csvLang|
        |-1    |10   |desc|2000          |2010   |phy               |json  |en     |
        |2     |20   |asc |-1900         |2000   |che               |json  |en     |
