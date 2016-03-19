"""
Tests for the database access abstraction features of MBE
"""

from behave import *
from nose.tools.trivial import ok_

from of.broker.lib.features.test_resources import test_node, test_find_node_query

use_step_matcher("re")

@when("the user logs in with username (?P<username>.+) and password (?P<password>.+)")
@then("the user logs in with username (?P<username>.+) and password (?P<password>.+)")
@given("the user logs in with username (?P<username>.+) and password (?P<password>.+)")
def step_impl(context, username, password):
    """
    :type context behave.runner.Context
    :param username The username
    :param password The password

    """

    context.session_id, context.user = context.auth.login(
        {"usernamePassword": {"username": username, "password": password}})

@given("test node is saved to the database")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    context.db_access.save(test_node, context.user)


@then("test node should be in the database")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    _result = context.db_access.find(test_find_node_query)
    if len(_result) == 1:
        ok_(True)
    else:
        ok_(False, "Test node wasn't found, result:" + str(_result))


@step("a (?P<event_category>.+) test node log item should have been created")
def step_impl(context, event_category):
    """

    :type context behave.runner.Context
    :param event_type The type of event

    """

    _result = context.db_access.find(
        {"conditions": {"category" : event_category, event_category+".name" : "test_node"}, "collection": "log"})
    if len(_result) == 1:
        ok_(True)
    else:
        ok_(False, "Test log item wasn't found, result:" + str(_result))


@given("the test node is removed from the database")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    context.db_access.remove_condition(test_find_node_query, context.user)


@then("the test node should not be present")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    _result = context.db_access.find(test_find_node_query)
    if len(_result) == 0:
        ok_(True)
    else:
        ok_(False, "Test node was till found found, result:" + str(_result))
