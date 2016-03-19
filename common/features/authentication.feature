# Created by Nicklas B at 2015-02-08
Feature: Authentication
  Authentication should be able to handle login:s and sessions.

  Scenario: Log in a user
    Given the user is logged out
    When the user logs in with username tester and password test
    Then the user is logged in


  Scenario: Log out a user
    Given the user logs in with username tester and password test
    And the user is logged in
    When the the user logs out
    Then the user is logged out

  Scenario: User tried to log in with bad credentials
    Given the user provides bad credentials an AuthenticationError should be raised

  Scenario: User tried to validate an invalid session
    Given the user provides an invalid session AuthenticationError should be raised