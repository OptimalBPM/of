"""
This module contains the MongoDBAuthBackend

Created on Jan 22, 2016

@author: Nicklas Boerjesson
"""


import datetime
import hashlib

from of.broker.lib.schema_mongodb import of_object_id
from of.common.security.authentication import AuthenticationBackend


class MongoDBAuthBackend(AuthenticationBackend):
    """
    The MongoDBAuthBackend class implements the AuthenticationBackend, and provides a mongodb-based
    authentication backend for the Optimal Framework
    """

    # A db_access instance
    db_access = None

    def __init__(self, _db_access):
        self.db_access = _db_access


    def get_session(self, _session_id):
        _session_cond = {
            "conditions": {"_id": of_object_id(_session_id)},
            "collection": "session"
        }

        _sessions = self.db_access.find(_session_cond)
        if len(_sessions) > 0:
            if len(_sessions) > 1:
                raise Exception("session check: Multiple users returned by user query for " + _session_id)
            return _sessions[0]
        else:
            return None

    def get_user(self, _user_id):
        _user_condition = {
            "conditions": {"_id": of_object_id(_user_id), "schemaRef": "ref://of.node.user"},
            "collection": "node"
        }
        _users = list(self.db_access.find(_user_condition))
        if len(_users) > 0:
            if len(_users) > 1:
                raise Exception("get user: Multiple users returned by user query for " + _user_id)
            return _users[0]
        else:
            return None

    def authenticate_username_password(self, _credentials):
        _cred_condition = {
                "conditions":
                        {
                            "credentials.usernamePassword.username": _credentials["usernamePassword"]["username"],
                         "credentials.usernamePassword.password": hashlib.md5(
                            _credentials["usernamePassword"]["password"].encode('utf-8')).hexdigest()

                        },
                "collection": "node"
            }

        # TODO: FTRT make a general credentials schema that is used by the user schema and use it to verify \
        # credential packets

        _users = self.db_access.find(_cred_condition)
        if len(_users) > 0:
            if len(_users) > 1:
                raise Exception("password_login error: Multiple users returned by user query.")

            _user = _users[0]
            # Create Session
            _session_data = {
                "createdWhen": str(datetime.datetime.utcnow()),
                "user_id": str(_user["_id"]),
                "schemaRef": "ref://of.session"
            }

            _session_id = self.db_access.save(_session_data, _user)

            return _session_id, _user
        else:
            return None, None


    def logout(self, _session_id):

        _remove_cond = {
            "conditions": {"_id": of_object_id(_session_id)},
            "collection": "session"
        }

        self.db_access.remove_condition(_remove_cond, None)