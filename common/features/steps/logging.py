import os

import datetime
from behave import *

from common.logging import CN_NOTIFICATION

use_step_matcher("re")

from nose.tools.trivial import ok_
from of.common.logging import make_textual_log_message, CE_RESOURCE, SEV_DEBUG, SEV_ERROR, write_to_log
import of.common.logging

_global_params = None
_global_err_param = ("Test error", CE_RESOURCE, SEV_ERROR, 1, "TestUser", datetime.datetime(1999, 1, 1, 1, 1, 1, 1), 1)
_global_err_cmp = "Process Id: 1 - An error occurred:\nTest error\nEvent category: resource\n" \
                  "Severity: error\nUser Id: TestUser\nOccurred when: 1999-01-01 01:01:01.000001\nEntity Id: 1"
_global_debug_param = ("Test message", CN_NOTIFICATION, SEV_DEBUG)
_global_debug_cmp = "Process Id: " + str(os.getpid())+" - Message:\nTest message\nEvent category: notification\nSeverity: debug"


def local_test_log_writer(*args):
    global _global_params
    _global_params = args

@then("a error log message is built")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    global _global_err_cmp, _global_debug_cmp, _global_err_param, _global_debug_param

    _err_msg = make_textual_log_message(*_global_err_param)
    ok_(_err_msg == _global_err_cmp, "Error message did not match: \nResult:" + str(_err_msg.encode()) + "\nComparison:\n" + str(_global_err_cmp.encode()))


@then("a debug log message is built")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    global _global_err_cmp, _global_debug_cmp, _global_err_param, _global_debug_param

    _debug_msg = make_textual_log_message(*_global_debug_param)
    ok_(_debug_msg == _global_debug_cmp, "Debug message did not match: \nResult:" + str(_debug_msg.encode()) + "\nComparison:\n" + str(_global_debug_cmp.encode()))


@then("the logging should call it")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    global _global_params, _global_err_param, logging_callback
    _global_params = None
    of.common.logging.logging_callback = local_test_log_writer
    try:
        write_to_log(*_global_err_param)
        ok_(_global_params == _global_err_param, "Global params didn't match!\nResult:" + str(_global_params) + "\nComparison: " + str(_global_err_param))
        _global_params = None
        of.common.logging.logging_callback = None
    except Exception as e:
        # Be sure to reset globals.<
        _global_params = None
        of.common.logging.logging_callback = None
        raise Exception(e)

