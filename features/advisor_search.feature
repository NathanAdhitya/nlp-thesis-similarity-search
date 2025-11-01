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
    And each advisor should have required fields

  Scenario: Search advisors with program filter
    Given I have valid program IDs
    When I search for advisors with query "computer vision" filtered by programs
    Then I should receive a successful response
    And the response should contain advisor results

  Scenario: Search advisors with different models
    When I search for advisors with query "data mining" and model "bgem3"
    Then I should receive a successful response
    And the response should contain advisor results
    When I search for advisors with query "data mining" and model "allminilm"
    Then I should receive a successful response
    And the response should contain advisor results

  Scenario: Search advisors with custom parameters
    When I search for advisors with query "natural language processing" and top_k "3"
    Then I should receive a successful response
    And the response should contain at most 3 advisor results

  Scenario: Search with empty query for advisors
    When I search for advisors with query ""
    Then I should receive an error response