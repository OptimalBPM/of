"""
The logging module handles all the logging to database of OF.
"""

import datetime

from of.broker.lib.schema_mongodb import mbe_object_id

__author__ = "nibo"


# coding=utf-8
"""
A dictionary difference calculator
Originally posted as:
http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary/1165552#1165552
"""


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values

    """

    def __init__(self, _old, _new):
        """
        Compares two dicts

        :param _old: The old dict
        :param _new: The new dict

        """

        self.current_dict, self.past_dict = _new, _old
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (_new, _old)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        """
        A list of added items

        """
        return self.current_keys - self.intersect

    def removed(self):
        """
        Returns a list of removed items

        """
        return self.past_keys - self.intersect

    def changed(self):
        """
        Returns a list of changed items

        """
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        """
        Returns a list of unchanged items

        """
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])


class Logging():
    """
    The logging class provides functionality to properly write to the "log" collection
    """
    database = None
    _log_collection = None

    def __init__(self, _database):
        """
        Initialize the logger, connects to a database

        :param _database:

        """
        self.database = _database
        self._log_collection = self.database["log"]

    @staticmethod
    def _compare_documents(_old, _new):
        # TODO: This must probably be using field xpaths or something. JSON XPaths might be useful
        # The problem is if a field is in a list of objects. Then fieldId will not be unique in the list of objects.
        # How about always using xpaths for a change? The problem is fieldIds in lists.

        _changes = []
        _differ = DictDiffer(_old, _new)
        for _property in _differ.added():
            _changes.append({"propertyId": _property, "before": None, "after": _new[_property]})

        for _property in _differ.removed():
            _changes.append({"propertyId": _property, "before": _old[_property], "after": None})

        for _property in _differ.changed():
            _changes.append({"propertyId": _property, "before": _old[_property], "after": _new[_property]})

        return _changes

    @staticmethod
    def _generate_node_event_skeleton(_user_id, _occurred_when, _node_id):
        """
        Generate a skeleton for a event item

        :param _user_id: The userId
        :param _occurred_when: When the event occured
        :param _node_id: The affected nodeId

        """
        # TODO: Decide  on how to make user ID reach the logger.
        return {
            "user_id": mbe_object_id(_user_id),
            "occurredWhen": _occurred_when,
            "node_id": mbe_object_id(_node_id)
        }

    def write_error(self, _event):

        pass



    def write_log(self, _event):
        """
        Writes an event to the database

        :param _event: The event data

        """
        _event["writtenWhen"] = str(datetime.datetime.utcnow())
        self._log_collection.save(_event)

    def log_security(self, _category, _message, _user_id, _node_id):
        """
        Creates an security event log item

        :param _category: type of event, can be rights, access or attack
        :param _message: Error message
        :param _user_id: The _id of the user. A string(not the ObjectId)
        :param _node_id: If applicable, the concerned node document
        :return:

        """
        _event = self._generate_node_event_skeleton(_user_id, str(datetime.datetime.utcnow()), _node_id)
        _event["category"] = _category
        _event["severity"] = "user"
        _event["data"] = _message
        self.write_log(_event)

    def log_save(self, _document, _user_id, _old_document=None):
        """
        Creates an event item based on the differences between the provided documents

        :param _document: The new version of the document
        :param _user_id: The _id of the user. A string(not the ObjectId)
        :param _old_document: The previous version

        """

        # Overwrite existing value?
        _event = self._generate_node_event_skeleton(_user_id, str(datetime.datetime.utcnow()),
                                               _document["_id"])
        if _old_document:
            # If so, compare and generate differences and save an "change" event to the "log" collection
            _event["change"] = self._compare_documents(_old=_old_document, _new=_document)
            _event["category"] = "change"

        else:
            # Save an "add" event to "log" collection
            _event["add"] = _document
            _event["category"] = "add"

        self.write_log(_event)

    def log_remove(self, _removed_document, _user_id):
        """
        Created a "remove" event. Called when a document has been removed.

        :param _removed_document: The removed document.
        :param _user_id: The _id of the user. A string(not the ObjectId)

        """

        _event = self._generate_node_event_skeleton(_user_id, str(datetime.datetime.utcnow()),
                                               _removed_document["_id"])
        _event["remove"] = _removed_document
        _event["category"] = "remove"
        self.write_log(_event)


