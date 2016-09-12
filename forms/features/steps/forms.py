from behave import *

from of.forms import load_forms_from_directory, of_form_folder, get_form
from nose.tools.trivial import ok_
from of.forms import cache
use_step_matcher("re")


@given("A tree of forms is loaded from a folder")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.forms = {}
    load_forms_from_directory(of_form_folder())



@then("the node and user forms must be present")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    ok_(get_form("ref://of.node.node", "default")[0]["key"] == "name" and \
        get_form("ref://of.node.user", "default")[2]["title"] == "Credentials")



@step("a terse node form is added to the tree")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    cache["ref://of.node.user"]["terse"]= [{"title" : "terse"}]

@then("a references to the terse node form should return the correct form")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    ok_(get_form("ref://of.node.user", "terse")[0]["title"] == "terse")

