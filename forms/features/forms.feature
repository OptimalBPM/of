# Created by nicklasborjesson at 2016-09-11
Feature: # Form features
  # Loading and accessing forms

  Scenario: # Recursively loading forms
    Given A tree of forms is loaded from a folder
    Then the node and user forms must be present


  Scenario: # Looking up forms
    Given A tree of forms is loaded from a folder
    And a terse node form is added to the tree
    Then a references to the terse node form should return the correct form
