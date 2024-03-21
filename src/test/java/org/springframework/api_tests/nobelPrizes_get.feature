# ********RoostGPT********

# Test generated by RoostGPT for test karate-sample-api using AI Type Azure Open AI and AI Model roostgpt-4-32k
# 
# Feature file generated for /nobelPrizes_get for http method type GET 
# RoostTestHash=977dd819cb
# 
# 

# ********RoostGPT********
# Karate feature file for a RESTful API

Feature: Nobel Prizes API

    Background:
      * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:8080')
      * url urlBase
      * def authToken = karate.properties['AUTH_TOKEN']
      * configure headers = {Authorization: '#(authToken)'}

    Scenario: Fetch Nobel Prizes with valid parameters
      Given path '/2.1/nobelPrizes'
      And params {offset: 1, limit: 10, nobelPrizeYear: 2000, yearTo: 2010, nobelPrizeCategory: 'eco'}
      When method get
      Then status 200
      And match response contains {nobelPrizes: '#array'}
      And match each response.nobelPrizes contains {awardYear: '#number'}
      
    Scenario: Fetch Nobel Prizes with invalid parameters
      Given path '/2.1/nobelPrizes'
      And params {offset: 'a', limit: 'b'}
      When method get
      Then status 400

    Scenario: Fetch Nobel Prizes with no parameters
      Given path '/2.1/nobelPrizes'
      When method get
      Then status 200
      And match response contains {nobelPrizes: '#array'}
      
    Scenario: Confirm format and language parameters
      Given path '/2.1/nobelPrizes'
      And params {format: 'json', csvLang: 'en'}
      When method get
      Then status 200
      And match response contains {nobelPrizes: '#array'}
