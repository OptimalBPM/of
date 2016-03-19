"""
Tests for the authentication features of MBE
"""

from behave import *
from nose.tools.trivial import ok_

from of.common.security.authentication import AuthenticationError, \
    check_session

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


@given("the user is logged in")
@then("the user is logged in")
def step_impl(context):
    """

    :type context behave.runner.Context

    """

    ok_(check_session(context.session_id) is not None)


@when("the the user logs out")
def step_impl(context):
    """

    :type context behave.runner.Context

    """

    context.auth.logout(context.session_id)


@then("the user is logged out")
@given("the user is logged out")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    if hasattr(context, "session_id"):
        try:
            check_session(context.session_id)
        except AuthenticationError:
            ok_(True)
    else:
        ok_(True)


@given("the user provides bad credentials an AuthenticationError should be raised")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    try:
        context.session_id, context.user = context.auth.login(
            {"usernamePassword": {"username": "tester", "password": "bad password"}})
    except AuthenticationError:
        ok_(True)
        return

    ok_(False, "An error wasn't raised when logging in with bad credentials")


@given("the user provides an invalid session AuthenticationError should be raised")
def step_impl(context):
    """

    :type context behave.runner.Context

    """
    try:
        context.session_id, context.user = context.auth.check_session("000000010000010001000000")
    except AuthenticationError:
        ok_(True)
        return

    ok_(False, "An error wasn't raised when trying to use an invalid session")