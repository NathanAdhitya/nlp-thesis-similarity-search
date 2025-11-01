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
    And each paper should have required fields

  Scenario: Search papers with different models
    When I search for papers with query "artificial intelligence" and model "bgem3"
    Then I should receive a successful response
    And the response should contain paper results
    When I search for papers with query "artificial intelligence" and model "allminilm"
    Then I should receive a successful response
    And the response should contain paper results

  Scenario: Search papers with custom top-k parameter
    When I search for papers with query "deep learning" and top_k "5"
    Then I should receive a successful response
    And the response should contain at most 5 paper results

  Scenario: Search with empty query
    When I search for papers with query ""
    Then I should receive an error response

  Scenario: Search with invalid model
    When I search for papers with query "neural networks" using model "invalid_model"
    Then I should receive a successful response
    And the response should contain paper results