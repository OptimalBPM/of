"""
This module holds Optimal Framework-specific JSON schema functionality

Created on Jan 22, 2016

@author: Nicklas Boerjesson
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

    # Parse the schema file reference
    _netloc = urlparse(_uri).netloc
    # Translate into file name
    _filename = _netloc.replace(".", "/")
    # Use urlparse to parse the file location from the URI
    _file_location = os.path.abspath(os.path.join(_folder, "namespaces", _filename + ".json"))

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
    return os.path.join(script_dir, "namespaces")

def parse_name_parts(_import):
    """
    Parses a string of the namespace.namespace.localname structure and returns a tuple with the namespace and the local name.
    :param _import: The string to parse
    :return: a tuple with the namespace and the local name
    """
    _scheme, _netloc, _path = urlparse(_import).netloc.split(".")
