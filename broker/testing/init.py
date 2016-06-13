"""
The init module is responsible for initializing an MBE backend database.
"""

import os

__author__ = 'Nicklas Boerjesson'

import json

from pymongo.mongo_client import MongoClient

from of.broker.lib.access import DatabaseAccess

script_dir = os.path.dirname(__file__)


def get_empty_db_da(_database_name, _json_schema_folders=None, _uri_handlers = None):
    """
    Create an empty database. Drops any existing.

    :param _database_name: The name of the database
    :return: A database access object for the database
    :param _json_schema_folders: A list of application specific JSON schema folders

    """
    _client = MongoClient()
    if _database_name in _client.database_names():
        _client.drop_database(_client[_database_name])
    _database = _client[_database_name]
    return DatabaseAccess(_database=_database, _json_schema_folders=_json_schema_folders, _uri_handlers=_uri_handlers)


def _import_init_file(_filename, _da):
    """
    Imports the content of the file to tha database

    :param _filename: File to import
    :param _da: A data access instance
    :return:

    """
    json_data = open(_filename)
    _data = json.load(json_data)
    for _curr_data in _data:
        print("init - " + _curr_data["name"])
        _da.save(_curr_data, _user=None, _allow_save_id=True)
    json_data.close()


def init_database(_database_name="test_database", _data_files=None, _json_schema_folders=None, _uri_handlers= None):
    """
    Initialises a MBE database. Drops any existing databases and import the provided files

    :param _database_name: The name of the database.
    :param _data_files: A list of application specific additional files to import
    :param _json_schema_folders: A list of application specific JSON schema folders
    :return: A database access object for the database

    """
    if not _data_files:
        _data_files = []

    _da = get_empty_db_da(_database_name, _json_schema_folders = _json_schema_folders, _uri_handlers= _uri_handlers)
    # Init by loading the OF base structure
    _import_init_file(os.path.join(script_dir, 'init.json'), _da)

    # Import the rest of the data
    for _filename in _data_files:
        _import_init_file(_filename, _da)

    return _da


if __name__ == '__main__':
    init_database()

