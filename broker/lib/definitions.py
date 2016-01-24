""""
This modules holds the definitions class.
Definitions are indexed by their namespaces.
"""
import json

__author__ = "Nicklas Börjesson"


class Definitions:
    """The definitions class holds definitions.
    Definitions are grouped by namespaces.
    """

    """A dict definitions, keys are namespaces"""
    _definitions = None

    def __init__(self):
        self._definitions = {}

    def add_cumulatively(self, _definition):
        """
        Add a definition to _definitions, _definition may
        :param _definition: The definition to add, may span several namaspaces
        :return:
        """
        # TODO: Create a definitions schema
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

        recurse_dict(self._definitions, _definition)

    # Getters, setters and iterators

    def __getitem__(self, item):
        if item not in self._definitions:
            self._definitions[item] = {
                "schemas": []
            }
        return self._definitions[item]

    def __setitem__(self, key, value):
        self._definitions[key] = value

    def __iter__(self):
        for _item in self._definitions:
            yield _item

    def load_definitions(self, _definition_files):
        """
        Load definitions from files
        :param _definition_files: A list of _definition_files
        """

        def load_definition_file(_filename):
            with open(_filename, "r") as _local_file:
                _local_def_data = json.load(_local_file)
                self.add_cumulatively(_local_def_data)

        if _definition_files:
            for _curr_definition in _definition_files:
                load_definition_file(_curr_definition)


    def as_dict(self):
        return self._definitions
