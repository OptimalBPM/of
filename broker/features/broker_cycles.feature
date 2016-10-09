# Created by nibo at 2015-06-03
Feature: Broker startup and shutdown scenarios
  These scenarios will cover differend startup- and shutdown scenarios

  Scenario: Starting and shutting down broker using process termination
    Given the broker is started
    And we wait 1 seconds
    And it is it possible to register an admin at the broker
    Then a termination on linux should return zero as exit code
