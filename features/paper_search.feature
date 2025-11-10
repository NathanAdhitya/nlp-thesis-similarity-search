Feature: Paper Search Functionality
  As a student
  I want to search for academic papers
  So that I can find relevant research for my thesis

  Background:
    Given the Semantica application is running

  Scenario: Search for papers with valid query
    When I search for papers with query "machine learning"
    Then I should receive a successful response
    And the response should contain paper results

  Scenario: Search with empty query
    When I search for papers with query ""
    Then I should receive an error response