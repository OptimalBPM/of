"""
Tests for The MBE Node feature
"""
import os

from behave import *
import json
from nose.tools.trivial import ok_

from of.broker.lib.features.test_resources import test_node
from of.common.security.groups import RightCheckError
from of.broker.lib.schema_mongodb import mbe_object_id

script_location = os.path.dirname(__file__)

use_step_matcher("re")

def json_load_file(file_name):
    with open(file_name) as data_file:
        return json.load(data_file)

@given("a test node is added")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    context.curr_id = context.node.save(test_node, context.user)


@step("a (?P<security_event_type>.+) test node history item should be in the database")
def step_impl(context, security_event_type):
    """

    :type context behave.runner.Context
    :param security_event_type The type of event

    """
    _result = context.node.history({"_id": context.curr_id}, context.user)

    for _curr_event in _result:
        if _curr_event["node_id"] == context.curr_id and \
                        security_event_type in _curr_event:
            ok_(True)
            return

    ok_(False, "Test log item wasn't found, result:" + str(_result))


@given("a test node is updated")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    changed_node = context.node.find({"name": "test_node"}, context.user)[0]
    changed_node["name"] = "test_node_changed"
    context.curr_id = context.node.save(changed_node, context.user)
    pass


@then("the node should have the new data")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    _result = context.node.find({"_id": "ObjectId(" + context.curr_id + ")"}, context.user)
    if _result[0]["name"] == "test_node_changed":
        ok_(True)
    else:
        ok_(False, "Test log item didn't match change, result:" + str(_result))


@given("a test node is removed")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    _test_node = context.node.find({"name": "test_node_changed"}, context.user)[0]
    context.curr_id = _test_node["_id"]

    context.node.remove({"_id": context.curr_id}, context.user)


@then("the node should not be in the database")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    _result = context.node.find({"_id": mbe_object_id(context.curr_id)}, context.user)
    if len(_result) == 0:
        ok_(True)
    else:
        ok_(False, "Test log item wasn't remove, result:" + str(_result))


@then("trying to administrate nodes, a RightCheckError should be raised")
def step_impl(context):
    """

    :type context behave.runner.Context

    """

    try:
        context.node.find({"_id": mbe_object_id("000000010000010001e64d01")}, context.user)
    except RightCheckError:
        ok_(True)
        return

    ok_(False)


@step("a rights security error should be in the event log")
def step_impl(context):
    """

    :type context behave.runner.Context

    """

    _result = context.node.database_access.find(
        {"conditions": {"node_id": None, "user_id": mbe_object_id("000000010000010001e64d15"),
                        "category": "right"}, "collection": "log"})
    if len(_result) == 1:
        ok_(True)
    else:
        ok_(False)


@then("trying to load a node, a PermissionError should be raised")
def step_impl(context):
    """

    :type context behave.runner.Context

    """

    try:
        context.node.load_node({"_id": "000000010000010001e64d01"}, context.user)
    except PermissionError:
        ok_(True)
        return

    ok_(False)


@step("an (?P<event_category>.+) security error prefixed (?P<prefix>.+) should be in the event log")
def step_impl(context, event_category, prefix):
    """

    :type context behave.runner.Context
    :param security_event_type The type of event
    :param prefix The prefix to look for

    """

    _result = context.node.database_access.find(
        {"conditions": {"node_id": mbe_object_id("000000010000010001e64d01"),
                        "user_id": mbe_object_id("000000010000010001e64d13"),
                        "category": event_category}, "collection": "log"})
    for _curr_error in _result:
        if _curr_error["data"][0:len(prefix)] == prefix:
            ok_(True)
            return

    ok_(False, context.scenario.name + ": Missing security event")


@then("a user loads a selector list of groups, the result must be longer than one and contain the administrators group")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    _result = context.node.lookup(
        {"conditions": {"parent_id": mbe_object_id("000000010000010001e64c24")}, "collection": "node"}, context.user)
    for _curr_select in _result:
        if _curr_select["value"] == "000000010000010001e64c28" and _curr_select["text"] == "Administrators":
            ok_(True)
            return

    ok_(False)


@then("a user loads a list of children, the result must be longer than one and contain the administrators group")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    _result = context.node.load_children({"parent_id": "000000010000010001e64c24"}, context.user)
    for _curr_select in _result:
        if _curr_select["_id"] == "000000010000010001e64c28" and _curr_select["name"] == "Administrators":
            ok_(True)
            return

    ok_(False)


@then("trying to remove a node, a PermissionError should be raised")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    try:
        context.node.remove({"_id": "000000010000010001e64d01"}, context.user)
    except PermissionError:
        ok_(True)
        return

    ok_(False)


@step("a request to the API is made")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    context.loaded_schemas = context.node.get_schemas(context.user)
    ok_(True)


@then("it should return a list of schema")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    ok_(type(context.loaded_schemas) is dict, "Get schema did not return a disctionary")

    _file = json_load_file(os.path.join(script_location, "../../../../schemas/user.json"))

    _resolved = context.node.database_access.schema_tools.resolveSchema(_file)


    ok_("of://user.json" in context.loaded_schemas, "The user schema is missing from schema list")
    ok_(context.loaded_schemas["of://user.json"]  == _resolved, "The resolved user schema doesn't match")


@then("Test (?P<prefix>.+)")
def step_impl(context, prefix):
    """
    :type context: behave.runner.Context
    """
    pass


@step("the user requests a list of templates")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.loaded_templates = context.node.get_templates("of://node_broker.json", context.user)
    ok_(True)


@then("it should return a list of templates")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    ok_(context.loaded_templates[0]["description"] == "Broker template")