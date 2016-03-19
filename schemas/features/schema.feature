# Created by nibo at 2015-03-06
  # TODO: These features are written in a quite cumbersome way, see if a better way of expressing is there
  # TODO: Add testing for custom schemas.
Feature: Perform schema handling
  SchemaTools must be able to handle multiple scenarios regarding schema handling

  Scenario: Load all schemas
    Given it loads all available schemas
    Then the list of schemas should contain the node and custom schema

  Scenario: Check schema for mandatory MBE fields
    Given a schema with missing data is presented
    Then it should raise field validation errors

  #Scenario: Validate schema
  #  Given  an erroneous schema is presented
  #  Then it should raise schema validation errors
  # Commented out since these schemas cannot be validated like this

  Scenario: Validate JSON data against schema
    Given it loads all available schemas
    Then applying to an invalid JSON should cause validation errors


  Scenario: Translate an string objectIds into actual ObjectId instances
    Given it loads all available schemas
    Then applying to a valid JSON should cause translate objectId strings

  Scenario: Resolve schema
    Given  a schema with references
    Then it should return a resolved schema

