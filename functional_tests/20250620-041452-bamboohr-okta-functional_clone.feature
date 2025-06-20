Feature: Testing BambooHROktaProvisioning API

Scenario: Testing the BambooHROktaProvisioning constructor
Given the API base URL 'http://localhost:3000' 
When I send a POST request to '/constructor' with body '{"subdomain": "test", "apiKey": "testKey", "domain": "testDomain", "apiToken": "testToken"}'
Then the response status should be 200
And the response should contain an instance of BambooHROktaProvisioning with the provided configuration

Scenario: Testing the fetchBambooHREmployees function
Given the API base URL 'http://localhost:3000' 
When I send a GET request to '/employees' with query parameters '["firstName", "lastName", "workEmail", "department", "jobTitle", "employeeNumber", "status"]'
Then the response status should be 200
And the response should contain an array of employee objects

Scenario: Testing the checkOktaUserExists function
Given the API base URL 'http://localhost:3000' 
When I send a GET request to '/oktaUser' with query parameter 'test@test.com'
Then the response status should be 200
And the response should contain an Okta user object or null

Scenario: Testing the generateTemporaryPassword function
Given the API base URL 'http://localhost:3000' 
When I send a GET request to '/generatePassword'
Then the response status should be 200
And the response should contain a string of 16 characters

Scenario: Testing the createOktaUserProfile function
Given the API base URL 'http://localhost:3000' 
When I send a POST request to '/createProfile' with body '{"firstName": "John", "lastName": "Doe", "workEmail": "john.doe@test.com", "department": "Engineering", "jobTitle": "Engineer", "employeeNumber": "123", "status": "Active"}'
Then the response status should be 200
And the response should contain an Okta user profile object

Scenario: Testing the createOktaUser function
Given the API base URL 'http://localhost:3000' 
When I send a POST request to '/createUser' with body '{"profile": {"firstName": "John", "lastName": "Doe", "email": "john.doe@test.com", "login": "john.doe@test.com", "employeeNumber": "123", "title": "Engineer", "department": "Engineering", "primaryPhone": "1234567890", "manager": "Manager"}, "credentials": {"password": {"value": "password"}}, "groupIds": [], "activate": true}'
Then the response status should be 200
And the response should contain a created Okta user object

Scenario: Testing the updateOktaUser function
Given the API base URL 'http://localhost:3000' 
When I send a PUT request to '/updateUser/123' with body '{"firstName": "John", "lastName": "Doe", "email": "john.doe@test.com", "login": "john.doe@test.com", "employeeNumber": "123", "title": "Engineer", "department": "Engineering", "primaryPhone": "1234567890", "manager": "Manager"}'
Then the response status should be 200
And the response should contain an updated Okta user object

Scenario: Testing the assignUserToGroups function
Given the API base URL 'http://localhost:3000' 
When I send a POST request to '/assignGroups/123' with body '{"department": "Engineering", "jobTitle": "Engineer"}'
Then the response status should be 200

Scenario: Testing the provisionUsers function
Given the API base URL 'http://localhost:3000' 
When I send a POST request to '/provisionUsers' with body '{"dryRun": false, "updateExisting": true}'
Then the response status should be 200
And the response should contain a results object

Scenario: Testing the syncSingleEmployee function
Given the API base URL 'http://localhost:3000' 
When I send a POST request to '/syncEmployee/123'
Then the response status should be 200
