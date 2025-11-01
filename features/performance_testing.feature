Feature: Performance and Load Testing
  As a system administrator
  I want to ensure the system performs well under load
  So that users have a good experience

  Background:
    Given the Semantica application is running

  @performance
  Scenario: Response time validation for paper search
    When I search for papers with query "machine learning"
    Then the response should be received within acceptable time
    And the response should be successful

  @performance  
  Scenario: Response time validation for advisor search
    When I search for advisors with query "artificial intelligence"
    Then the response should be received within acceptable time
    And the response should be successful

  @performance
  Scenario: Memory usage during search operations
    When I perform multiple search operations
    Then the system should maintain stable memory usage
    And not exhibit memory leaks

  @load
  Scenario: System handles multiple concurrent users
    When multiple users search simultaneously
    Then all requests should complete successfully
    And response times should remain reasonable