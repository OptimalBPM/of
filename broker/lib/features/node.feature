# Created by nibo at 2015-03-12
Feature: Node management
  It provides an interface to a tree structure


  Scenario: A user adds a node
    Given the user logs in with username tester and password test
    And a test node is added
    Then test node should be in the database
    And a add test node history item should be in the database

  Scenario: A user updates a node
    Given the user logs in with username tester and password test
    And a test node is updated
    Then the node should have the new data
    And a change test node history item should be in the database


  Scenario: Non-privileged user tries to remove a node and lacks permissions on an item
    Given the user logs in with username guest and password test
    Then trying to remove a node, a PermissionError should be raised
    And an permission security error prefixed Node.remove should be in the event log

  Scenario: A user removes a node
    Given the user logs in with username tester and password test
    And a test node is removed
    Then the node should not be in the database
    And a remove test node history item should be in the database

  Scenario: A user without rights tries to access the node interface
    Given the user logs in with username none and password test
    Then trying to administrate nodes, a RightCheckError should be raised
    And the user logs in with username tester and password test
    And a rights security error should be in the event log

    # TODO: Add test for scenario where a user tries to remove a node and lacks permissions on an item

  Scenario: A user without permissions tries to load a single node
    Given the user logs in with username guest and password test
    Then trying to load a node, a PermissionError should be raised
    And the user logs in with username tester and password test
    And an permission security error prefixed Node.load should be in the event log


  Scenario: A user wants a selector list of groups
    Given the user logs in with username root and password root
    Then a user loads a selector list of groups, the result must be longer than one and contain the administrators group

  Scenario: A uses loads a list of children
    Given the user logs in with username root and password root
    Then a user loads a list of children, the result must be longer than one and contain the administrators group


  Scenario: Load schemas
    Given the user logs in with username root and password root
    And a request to the API is made
    Then it should return a list of schema

  Scenario: Load templates
    Given the user logs in with username root and password root
    And the user requests a list of templates
    Then it should return a list of templates
