# Created by nibo at 2015-05-05
Feature: Message broker
  This tests the Optimal Framework message mechanism

  Scenario: Send a process message from one peer to another
    Given a peer sends a message to another
    Then then the message should be received

  Scenario: A process instance message
    Given a peer sends a system process instance message to the broker
    Then then the system process instance must saved to the process collection

  Scenario: A log message is sent
    Given a peer sends a log message to the broker
    Then then a matching log item must exist in the log collection