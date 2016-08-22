import datetime
import json
import time

from behave import *
from bson.objectid import ObjectId
from nose.tools.trivial import ok_



use_step_matcher("re")


@given("a peer sends a message to another")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    context.message = {"destination": "destination_peer", "schemaRef": "ref://of.message.message.json", "sourceProcessId": str(ObjectId()), "source": "source_peer", "messageId": 1}

    context.sender.received_message(json.dumps(context.message))


@then("then the message should be received")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    time.sleep(0.1)
    print("Took " + str(
        (context.receiver.sent_last_message_at - context.sender.received_last_message_at) * 1000) + " milliseconds.")
    context.message.update({"source": "source_peer"})

    ok_(context.receiver.message == context.message)


@given("a peer sends a system process instance message to the broker")
def step_impl(context):
    """
    :type context behave.runner.Context
    """

    context.message = {
        "spawnedBy": context.user["_id"],
        "spawnedWhen": str(datetime.datetime.utcnow()),
        "name": "Test_process_name",
        "systemPid": 10000,
        "schemaRef": "ref://of.process.system.json"
    }

    context.sender.received_message(json.dumps(context.message))


@then("then the system process instance must saved to the process collection")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    time.sleep(0.01)
    context.process_instance = \
    context.db_access.find({"conditions": {"name": "Test_process_name"}, "collection": "process"}, context.user)[0]

    ok_(context.message["name"] == context.process_instance["name"])


@given("a peer sends a log message to the broker")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    context.process_instance = \
    context.db_access.find({"conditions": {"name": "Test_process_name"}, "collection": "process"}, context.user)[0]
    print(context.process_instance["_id"])

    context.message = {
        "changedBy": context.user["_id"],
        "changedWhen": str(datetime.datetime.utcnow()),
        "name": "Test_process_name",
        "state": "running",
        "processId": str(context.process_instance["_id"]),
        "schemaRef": "ref://of.log.process_state.json"
    }
    context.sender.received_message(json.dumps(context.message))


@then("then a matching log item must exist in the log collection")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    time.sleep(0.01)
    context.log_item = \
    context.db_access.find({"conditions": {"processId": context.process_instance["_id"]}, "collection": "log"},
                           context.user)[0]
    ok_(True)
