Feature: API Integration and Error Handling
  As a developer
  I want to ensure API endpoints handle various scenarios correctly
  So that the application is robust and reliable

  Background:
    Given the Semantica application is running

  Scenario: API response headers validation
    When I make a request to "/programs"
    Then the response should have correct CORS headers
    And the response content type should be JSON

  Scenario: Invalid endpoint handling
    When I make a request to "/invalid/endpoint"
    Then I should receive a 404 error response

  Scenario: Search endpoint parameter validation
    When I search for papers with special characters in query "test@#$%"
    Then I should receive a response
    And the system should handle special characters gracefully

  Scenario: Large query handling
    When I search with a very long query
    Then the system should handle the request appropriately
    And not crash or timeout

  Scenario: Concurrent requests handling
    When I make multiple simultaneous search requests
    Then all requests should be processed successfully
    And responses should be consistent