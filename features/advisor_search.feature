Feature: Advisor Search Functionality
  As a student
  I want to search for thesis advisors
  So that I can find supervisors matching my research topic

  Background:
    Given the Semantica application is running

  Scenario: Search for advisors with valid query
    When I search for advisors with query "machine learning"
    Then I should receive a successful response
    And the response should contain advisor results

  Scenario: Search with empty query for advisors
    When I search for advisors with query ""
    Then I should receive an error response