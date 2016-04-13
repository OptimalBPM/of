"""
The init_env module/script initializes an Optimal Framework testing environment.
"""
import os
import sys

from bson.objectid import ObjectId

script_dir = os.path.dirname(__file__)
# Add relative optimal bpm path to be able to load the modules of this repository properly
sys.path.append(os.path.join(script_dir, "../../../"))

from of.broker.lib.auth_backend import MongoDBAuthBackend
from of.common.security.authentication import init_authentication
from of.broker.testing.init import init_database
from of.schemas.validation import of_uri_handler

__author__ = 'nibo'




def init_env(_database_name = "test_of", _context=None, _data_files=[], _json_schema_folders=[], _uri_handlers={}):
    """
    Initiates the test_broker database
    :param _context: If set, logs in and adds db_access, auth, session_id and peer_process_id properties
    :return:
    """
    _data_files += [os.path.join(script_dir, "data_struct.json")]
    _json_schema_folders += [os.path.abspath(os.path.join(script_dir, "..", "..", "schemas"))]
    _uri_handlers.update({"of": of_uri_handler})

    _db_access = init_database(_database_name, _data_files=_data_files,
                               _json_schema_folders=_json_schema_folders,
                               _uri_handlers=_uri_handlers)

    if _context:
        _context.db_access = _db_access
        _context.auth = init_authentication(MongoDBAuthBackend(_context.db_access))

        _context.session_id, _context.user = _context.auth.login(
            {"usernamePassword": {"username": "tester", "password": "test"}})

        _context.peer_process_id = str(ObjectId())


if __name__ == "__main__":
    init_env()
