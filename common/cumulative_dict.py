""""
This modules holds the CumulativeDict class.
"""
import json

__author__ = "Nicklas Börjesson"


class CumulativeDict:
    """The CumulativeDicts class holds dictionaries indexed by names, adding one
    """

    """A dict namespaces, keys are namespaces"""
    _dicts = None

    """The default value of a new dict"""
    default = None

    def __init__(self, _default = None):
        self._dicts = {}
        self.default = _default

    def add_cumulatively(self, _dicts):
        """
        Add a definition to _dicts, _definition may
        :param _definition: The definition to add, may span several namaspaces
        :return:
        """

        def recurse_dict(_existing, _new):
            if isinstance(_new, dict):
                for _curr_new_key, _curr_new_value in _new.items():
                    if _curr_new_key in _existing and isinstance(_existing[_curr_new_key], dict) \
                            and isinstance(_existing[_curr_new_key], dict):
                        recurse_dict(_existing[_curr_new_key], _curr_new_value)
                    else:
                        _existing[_curr_new_key] = _curr_new_value

            else:
                raise Exception("Can only call cumulatively_add_definition with a dict")

        recurse_dict(self._dicts, _dicts)

    # Getters, setters and iterators

    def __getitem__(self, item):
        if item not in self._dicts:
            self._dicts[item] = dict(self.default)
        return self._dicts[item]

    def __setitem__(self, key, value):
        self._dicts[key] = value

    def __iter__(self):
        for _item in self._dicts:
            yield _item

    def values(self):
        return self._dicts.values()

    def keys(self):
        return self._dicts.keys()

    def items(self):
        return self._dicts.items()


    def load_dicts(self, _definition_files, _top_attribute=None):
        """
        Load namespaces from files
        :param _definition_files: A list of _definition_files
        """

        def load_definition_file(_filename):
            with open(_filename, "r") as _local_file:
                _local_def_data = json.load(_local_file)
                if _top_attribute is not None:
                    self.add_cumulatively(_local_def_data[_top_attribute])
                else:
                    self.add_cumulatively(_local_def_data)

        if _definition_files:
            for _curr_definition in _definition_files:
                load_definition_file(_curr_definition)


    def as_dict(self):
        return self._dicts
