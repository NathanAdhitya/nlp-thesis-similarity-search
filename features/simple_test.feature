Feature: Simple API Test
  As a developer
  I want to test basic API functionality
  So that I can verify the system works

  Scenario: Basic API health check
    Given the application is running
    When I make a basic request
    Then I should get a response