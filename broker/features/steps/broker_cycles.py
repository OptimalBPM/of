import os

import traceback
from multiprocessing import Process
import time

from behave import *
from nose.tools.trivial import ok_

from of.broker.features import run_broker_testing
from of.common.messaging.utils import call_api, register_at_broker

use_step_matcher("re")

_log_prefix = "Tester - Broker Cycles :"
script_dir = os.path.dirname(__file__)



@given("the broker is started")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    try:
        print(_log_prefix + "Starting broker process.")
        context.broker_process = Process(name="broker_testing", target=run_broker_testing, daemon=False)
        context.broker_process.start()
        if context.broker_process.exitcode:
            ok_(False, "Failed starting the process, it terminated within wait time.")
        else:
            ok_(True)
    except Exception as e:
        print(_log_prefix + "Error starting broker: " + str(e) + "\nTraceback:" + traceback.format_exc())
        ok_(False)





@then("a termination on linux should return zero as exit code")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    print(_log_prefix + "Terminating the broker process")
    context.broker_process.terminate()
    try:
        context.broker_process.join(timeout=10)
    except:
        ok_(False, "Broker process did not exit within 5 seconds")
    if os.name == "nt":
        print("Terminations cannot be gracefully catched and acted upon on windows")
        ok_(True)
    else:
        if context.broker_process.exitcode != 0:
            ok_(False, "Broker process exited with a nonzero exit code: " + str(context.broker_process.exitcode))
        else:
            ok_(True)


@step("the broker is told to restart using the API")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    print(_log_prefix + "Telling Broker to restart using a call to broker_control...")
    call_api(_url="https://127.0.0.1:8080/admin/broker_control",
             _session_id=context.session["session_id"],
             _data={"command": "restart", "reason": "Testing restarting the broker"},
             _verify_SSL=False
             )
    print(_log_prefix + "Waiting for process to exit...")

    context.broker_process.join(timeout=2)
    ok_(True)

@step("the broker is told to stop using the API")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    print(_log_prefix + "Telling Broker to stop using a call to stop_broker...")
    call_api(_url="https://127.0.0.1:8080/admin/broker_control",
             _session_id=context.session["session_id"],
             _data={"command": "stop", "reason": "Testing stopping the broker"},
             _verify_SSL=False
             )
    ok_(True)

@step("a get environment request should fail")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    try:
        _response = call_api(_url="https://127.0.0.1:8080/get_broker_environment",
                 _session_id=context.session["session_id"],
                 _data={}, _verify_SSL=False)
    except Exception as e:
        ok_(True, str(e))
    else:

        os.kill(_response["systemPid"], 9)
        ok_(False, "The broker could still be reached after being told to shut down, killed pid "+ str(_response["systemPid"] + " manually."))


@step("we wait (?P<seconds>.+) seconds")
def step_impl(context, seconds):
    """
    :type context behave.runner.Context
    """
    time.sleep(float(seconds))
    ok_(True)


@step("there is a web_socket peer with the address (?P<address>.+)")
def step_impl(context, address):
    """
    :type context behave.runner.Context
    """
    print("Tester: Calling get_peers and checking for the address " + str(address))
    try:
        _peers = call_api(_url="https://127.0.0.1:8080/admin/get_peers",
                 _session_id=context.session["session_id"],
                 _data={}, _verify_SSL=False
                 )
    except Exception as e:
        ok_(False, "An error occurred contacting server:" + str(e))
    if _peers:
        for _peer in _peers:

            if "web_socket" in _peer and _peer["address"] == address and _peer["web_socket"] == "removed for serialization":
                ok_(True)
                return
        ok_(False, "No " + str(address) + " peer registered.")
    else:
        ok_(False, "No response from the server.")



@step("it is it possible to register an (?P<peer_type>.+) at the broker")
def step_impl(context, peer_type):
    """
    :type context behave.runner.Context
    """

    try:
        context.session = register_at_broker(_address="test", _type=peer_type, _server="https://127.0.0.1:8080",
                                             _username="tester", _password="test", _verify_SSL=False)

        if context.session["session_id"]:
            print("Successfully registered at broker, got sessionid: " + str(context.session["session_id"]))
            ok_(True)
        else:
            ok_(False, "No session Id returned.")
    except ConnectionError as e:
        ok_(False, "'Connection Error registering:" + str(e))
    except Exception as e:
        ok_(False, "Error registering:" + str(e))


