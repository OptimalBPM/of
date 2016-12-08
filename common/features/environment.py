"""
    Initialization for MBE tests.
"""

import os

from of.schemas.schema import SchemaTools

__author__ = 'nibo'

from of.common.security.authentication import init_authentication, AuthenticationBackend

# Test users uuids
id_user_root = "000000010000010001e64c30"
id_user_test = "000000010000010001e64c31"
id_user_testagent = "000000010000010001e64c32"

id_right_admin_nodes = "000000010000010001e64d01"

script_dir = os.path.dirname(os.path.abspath(__file__))


class MockupAuthenticationBackend(AuthenticationBackend):
    """
    This class implements a mockup authentication backend, it has one user and one session
    """

    def get_session(self, _session_id):
        if _session_id == "1":
            return {"user_id": "tester"}
        else:
            return None

    def get_user(self, _user_id):
        if _user_id == "tester":
            return {}
        else:
            return None

    def authenticate_username_password(self, _credentials):
        if _credentials["usernamePassword"]["username"] == "tester" and \
                        _credentials["usernamePassword"]["password"] == "test":
            return "1", {"user_id": "tester"}
        else:
            return None, None

    def logout(self, _credentials):
        return


def before_feature(context, feature):
    """

    Initialisation for all features.

    :param context:
    :param feature:
    :return:

    """

    context.auth = init_authentication(MockupAuthenticationBackend())
