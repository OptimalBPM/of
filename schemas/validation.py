"""
This module holds Optimal Framework-specific JSON schema functionality
"""
import json
import os
from urllib.parse import urlparse

__author__ = 'Nicklas Borjesson'

script_dir = os.path.dirname(__file__)


def general_uri_handler(_uri, _folder):
    """
    This function looks up a JSON schema that matches the URL in the given folder
    :param _uri: The _uri to handle
    :return: The schema
    """
    # TODO: If there ever was a typical function to memoize, this would be it.(ORG-112)

    # Use urlparse to parse the file location from the URI
    _file_location = os.path.abspath(os.path.join(_folder, urlparse(_uri).netloc))

    # noinspection PyTypeChecker
    with open(_file_location, "r", encoding="utf-8") as _schema_file:
        _json = json.load(_schema_file)
    return _json

def of_uri_handler(_uri):
    """
    This function is given as call back to JSON schema tools to handle the of:// namespace references
    :param _uri:
    :return: The schema
    """
    return general_uri_handler(_uri, script_dir)


def of_schema_folder():
    return script_dir