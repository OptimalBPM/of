"""
Tests for The OF Schema feature
"""
import traceback
from copy import deepcopy


import sys
import json

import os
from behave import *
from bson.objectid import ObjectId
from nose.tools.trivial import ok_

from of.schemas.features.resources import schemaRef_custom
from of.schemas.schema import SchemaTools
from of.schemas.validation import of_uri_handler

use_step_matcher("re")

script_location = os.path.dirname(__file__)


def json_load_file(file_name):
    with open(file_name) as data_file:
        return json.load(data_file)


@given("it loads all available schemas")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    context.schema_tools.load_schemas_from_directory(os.path.join(script_location, "..", "schemas"))

@then("the list of schemas should contain the node and custom schema")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    ok_("ref://of.node.node.json" in context.schema_tools.json_schema_objects and
        "ref://cust.car.json" in context.schema_tools.json_schema_objects)


@given("a schema with missing data is presented")
def step_impl(context):
    """

    :type context behave.runner.Context

    """

    context.schema_file = json_load_file(os.path.join(script_location, "../data/missing_req.json"))


@then("it should raise field validation errors")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    try:
        SchemaTools.check_schema_fields(context.schema_file, "test file")
    except Exception as e:
        if str(e) == 'MongoBackend.load_schemas_from_directory: ' \
                     'The "namespace" field is not in the schema-"test file"':
            ok_(True)
        else:
            ok_(False)


@given("an erroneous schema is presented")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    context.schema_tools = SchemaTools()


@then("it should raise schema validation errors")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    try:
        context.schema_tools.load_schema_from_file(os.path.join(script_location, "../data/bad_schema.json"))
    except Exception as e:
        if str(e) == 'MongoSchema: Init, SchemaError in data/bad_schema.json at ' \
                      'path:deque([\'type\'])\nMessage:\n\'bad_type\' is not valid under any of the given schemas':
            ok_(True)
        else:
            ok_(False)


@then("applying to an invalid JSON should cause validation errors")
def step_impl(context):
    """

    :type context behave.runner.Context

    """

    _json_data = json_load_file(os.path.join(script_location, "../data/bad_json.json"))

    try:

        context.schema_tools.apply(_json_data)
    except Exception as e:
        if str(e)[:32] == "'canRead' is a required property":
            ok_(True)
        else:
            if hasattr(sys, "last_traceback"):
                _traceback = traceback.print_tb(sys.last_traceback)
            else:
                _traceback = "Not available"

            ok_(False, "Error: " + str(e) + "\nTraceback:" + _traceback)


@then("applying to a valid JSON should cause translate objectId strings")
def step_impl(context):
    """

    :type context behave.runner.Context

    """

    _json_data = json_load_file(os.path.join(script_location, "../data/objectid_json.json"))
    context.schema_tools2 = context.schema_tools
    context.schema_tools.apply(_json_data)
    if isinstance(_json_data["_id"], ObjectId):
        ok_(True)
    else:
        ok_(False, "Correct data not present, _id should be an ObjectId but wasn't, value:" + str(_json_data["_id"]))


@given("a schema with references")
def step_impl(context):
    """
    :type context behave.runner.Context
    """


    context.resolvedGroupSchema = context.schema_tools.resolveSchema(context.schema_tools.json_schema_objects["ref://of.node.group.json"])






@then("it should return a resolved schema")
def step_impl(context):
    """
    :type context behave.runner.Context
    """

    def replace_attribute(parent, attribute, new_value):
        parent.pop(attribute)
        parent.update(new_value)

    # Completely manually resolve the group schema (this for the test to work better even if minor changes to the schemas are made)

    type_schema = json_load_file(os.path.join(script_location, "../../namespaces/of/type.json"))
    objectId_def = type_schema["properties"]["objectId"]
    uuid_def = type_schema["properties"]["uuid"]
    datetime_def = type_schema["properties"]["datetime"]

    node_schema = json_load_file(os.path.join(script_location, "../../namespaces/of/node/node.json"))
    manually_resolved_node_properties = node_schema["properties"]
    replace_attribute(manually_resolved_node_properties["_id"],"$ref", objectId_def)
    replace_attribute(manually_resolved_node_properties["parent_id"],"$ref", objectId_def)
    replace_attribute(manually_resolved_node_properties["canRead"]["items"],"$ref", objectId_def)
    replace_attribute(manually_resolved_node_properties["canWrite"]["items"],"$ref", objectId_def)

    group_schema = json_load_file(os.path.join(script_location, "../../namespaces/of/node/group.json"))
    manually_resolved_group = deepcopy(group_schema)
    del manually_resolved_group["allOf"]
    manually_resolved_group["properties"] = node_schema["properties"]
    manually_resolved_group["properties"].update(group_schema["allOf"][1]["properties"])
    replace_attribute(manually_resolved_group["properties"]["rights"]["items"],"$ref", objectId_def)

    ok_(context.resolvedGroupSchema == manually_resolved_group)

