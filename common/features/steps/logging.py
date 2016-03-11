import os
from behave import *
import difflib

use_step_matcher("re")

from nose.tools.trivial import ok_
from of.common.logging import make_textual_log_message, ERR_RESOURCE, SEV_DEBUG, SEV_ERROR, ERR_NONE



@then("a message is built")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    _err_msg = make_textual_log_message(_message="Test error", _severity=SEV_ERROR, _errortype=ERR_RESOURCE, _process_id=1)
    _err_cmp = "Process Id: 1 - An error occured:\nTest error\nSeverity: error\nError Type: resource"
    ok_(_err_msg == _err_cmp, "Error message did not match: \nResult:" + str(_err_msg.encode()) + "\nComparison:\n" + str(_err_cmp.encode()))

    _debug_msg = make_textual_log_message(_message="Test message", _severity=SEV_DEBUG)
    _debug_cmp = "Process Id: " + str(os.getpid())+" - Message:\nTest message\nSeverity: debug"
    ok_(_debug_msg == _debug_cmp, "Debug message did not match: \nResult:" + str(_debug_msg.encode()) + "\nComparison:\n" + str(_debug_cmp.encode()))