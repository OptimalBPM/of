import hashlib
from pymongo.mongo_client import MongoClient
from mbe.access import DatabaseAccess

__author__ = 'nibo'


test_credential = {"usernamePassword": {"username": "tester", "password": "test"}}


test_user_data = {
    "name": "TestUser",
    "credentials": test_credential,
    "createdWhen": "2014-11-13T01:00:00+00:00",
    "schemaRef": "2fb3b2c9-a29c-4fc0-b29d-6eed738b6dab",
    "canRead": ["5492cfb0a5cb641288b66c28"],
    "canWrite": ["5492cfb0a5cb641288b66c28"],
    "groups": ["5492cfb0a5cb641288b66c29"]
}

test_hashed_credential = {"usernamePassword": {"username": "tester", "password": hashlib.md5("test".encode('utf-8')).hexdigest()}}

test_hashed_user_data = {
    "name": "TestUser",
    "credentials": test_hashed_credential,
    "createdWhen": "2014-11-13T01:00:00+00:00",
    "schemaRef": "2fb3b2c9-a29c-4fc0-b29d-6eed738b6dab",
    "canRead": ["5492cfb0a5cb641288b66c28"],
    "canWrite": ["5492cfb0a5cb641288b66c28"],
    "groups": ["5492cfb0a5cb641288b66c29"]
}

test_find_user_query = {
    "conditions": test_hashed_user_data,
    "collection": "node"
}

test_session_id = None

def get_empty_db_da(_database_name, _json_schema_folder):
    _client = MongoClient()
    if _database_name in _client.database_names():
        _client.drop_database(_client[_database_name])
    _database = _client[_database_name]
    return DatabaseAccess(_json_schema_folder=None,  _database=_database)