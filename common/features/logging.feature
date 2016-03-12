# Created by nibo at 2015-06-02
Feature: Logging
  Logging facilities for the Optimal Framework

  Scenario: A textual log message needs to be created
    Then a log message is built

  Scenario: The callback is defined
    Then the logging should call it
