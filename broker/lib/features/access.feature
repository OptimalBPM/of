# Created by nibo at 2015-03-12
Feature: Database access layer and logging
  The database access layer hides many of the complexities of using MongoDB. Also, the logging is tested here

  Scenario: the user needs to save data
    Given the user logs in with username tester and password test
    And test node is saved to the database
    Then test node should be in the database
    And a add test node log item should have been created

  Scenario: The user want to remove data
    Given the user logs in with username tester and password test
    And the test node is removed from the database
    Then the test node should not be present
    And a remove test node log item should have been created
