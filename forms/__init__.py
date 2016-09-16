"""
This package holds functionality to load, access and cache JSF forms

Created on Sep 12, 2016

@author: Nicklas Boerjesson
"""

import os
import json
script_dir = os.path.dirname(__file__)


on_cache_miss = None

cache = {}

def get_form(_uri, _name):
    """
    Load a form from the cache
    :param _uri: The schemaRef
    :param _name: The name of the form
    :return: A JSF form
    """
    _form = None
    if _uri not in cache:
        if on_cache_miss:
            _form = on_cache_miss(_uri, _name)

    else:
        _ns = cache[_uri]
        if _name in _ns:
            _form = _ns[_name]

    if _form is None:
        raise Exception("Form " + _uri + " with name " + _name + "did not exist")
    else:
        return _form


def of_form_folder():
    """
    Get the folder of the forms
    :return: A string with the folder
    """
    return os.path.join(script_dir, "namespaces")

def load_forms_from_directory(_form_folder, _destination = None):
    """
    Load and validate all schemas in a folder structure, add to json_schema_objects

    :param _schema_folder: Where to look

    """
    _loaded_uris = []

    if _destination is None:
        _destination = cache
    def _recurse(_folder):
        for _root, _dirs, _files in os.walk(_folder):
            _ref = "ref://" + ".".join(os.path.relpath(_root, _form_folder).split("/"))
            _forms = {}
            for _file in _files:
                if _file[-5:].lower() == ".json":
                    try:
                        _curr_full_name = os.path.join(_root, _file)
                        with open(os.path.join(_root, _file), "r") as _file_obj:
                            _forms[_file[0:-5]] = json.load(_file_obj)
                    except Exception as e:
                        raise Exception("load_forms_from_directory: Error parsing \"" + _curr_full_name +
                                        "\"" + str(e))
            if _ref not in _loaded_uris:
                _loaded_uris.append(_ref)

            _destination[_ref] = _forms

            for _dir in _dirs:
                _recurse(os.path.join(_folder, _dir))

    _recurse(_form_folder)

    return _loaded_uris