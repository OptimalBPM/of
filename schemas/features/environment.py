"""
    Initialization for MBE tests.
"""

import os

from of.schemas.schema import SchemaTools
from of.schemas.validation import of_uri_handler

__author__ = 'nibo'

from of.common.security.authentication import init_authentication


# Test users uuids
id_user_root = "000000010000010001e64c30"
id_user_test = "000000010000010001e64c31"
id_user_testagent = "000000010000010001e64c32"

id_right_admin_nodes = "000000010000010001e64d01"

script_dir = os.path.dirname(__file__)

def before_feature(context, feature):
    """

    Initialisation for all features.

    :param context:
    :param feature:
    :return:

    """
    context.schema_tools = SchemaTools(_json_schema_folders=[os.path.join(script_dir, "..", "namespaces")], _uri_handlers={"ref": of_uri_handler})


