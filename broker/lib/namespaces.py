""""
This modules holds the namespaces class.
Namespaces are indexed by their namespaces.
"""
import json

__author__ = "Nicklas Börjesson"


class Namespaces:
    """The namespaces class holds namespaces.
    Namespaces are grouped by namespaces.
    """

    """A dict namespaces, keys are namespaces"""
    _namespaces = None

    def __init__(self):
        self._namespaces = {}

    def add_cumulatively(self, _namespace):
        """
        Add a definition to _namespaces, _definition may
        :param _definition: The definition to add, may span several namaspaces
        :return:
        """
        # TODO: Create a namespaces schema
        def recurse_dict(_left, _right):
            if isinstance(_right, dict):
                for _curr_right_key, _curr_right_value in _right.items():
                    if _curr_right_key in _left and isinstance(_left[_curr_right_key], dict) and isinstance(
                            _left[_curr_right_key], dict):
                        recurse_dict(_left[_curr_right_key], _right[_curr_right_key])
                    else:
                        _left[_curr_right_key] = _right[_curr_right_key]

            else:
                raise Exception("Can only call cumulatively_add_definition with a dict")

        recurse_dict(self._namespaces, _namespace)

    # Getters, setters and iterators

    def __getitem__(self, item):
        if item not in self._namespaces:
            self._namespaces[item] = {
                "schemas": []
            }
        return self._namespaces[item]

    def __setitem__(self, key, value):
        self._namespaces[key] = value

    def __iter__(self):
        for _item in self._namespaces:
            yield _item

    def load_namespaces(self, _definition_files):
        """
        Load namespaces from files
        :param _definition_files: A list of _definition_files
        """

        def load_definition_file(_filename):
            with open(_filename, "r") as _local_file:
                _local_def_data = json.load(_local_file)
                self.add_cumulatively(_local_def_data["namespaces"])

        if _definition_files:
            for _curr_definition in _definition_files:
                load_definition_file(_curr_definition)


    def as_dict(self):
        return self._namespaces
