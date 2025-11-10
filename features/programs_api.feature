Feature: Programs API Functionality
  As a user
  I want to retrieve available programs
  So that I can filter advisor searches by program

  Background:
    Given the Semantica application is running

  Scenario: Get all programs
    When I request all programs
    Then I should receive a successful response
    And the response should contain programs list