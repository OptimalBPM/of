"""
The factory module contains a number of functions that return message structures.
Use these functions instead of building messages manually to follow changes.

Created on Jan 22, 2016

@author: Nicklas Boerjesson
"""

import datetime
import os

if os.name != "nt":
    import pwd

import socket



__author__ = 'Nicklas Borjesson'


def get_current_login():
    if os.name == "nt":
        return os.getlogin()
    else:
        return pwd.getpwuid(os.geteuid()).pw_name



def reply_with_error_message(_runtime_instance, _message, _error_message):
    """
    Takes data from the incoming message and the instance replying to send an error message back to the sender.
    :param _runtime_instance: The calling class (to get the process_id from it)
    :param _message: The message to reply to(to get sender and messageId)
    :param _error_message: The error message to send
    """
    _struct = {
        "sourceProcessId": _runtime_instance.process_id,
        "messageId": _message["messageId"],
        "errorMessage": _error_message,
        "schemaRef": "ref://of.message.error"
    }

    if "source" in _message or _message["source"] == "":
        _struct["destination"] = _message["source"]

    if "destination" in _message or _message["source"] == "":
        _struct["source"] = _message["destination"]
    if "sourceProcessId" in _message and _message["sourceProcessId"] == "":
        _struct["destinationProcessId"] = _message["sourceProcessId"]

    return _struct


def store_process_system_document(_process_id, _name, _parent_id=None):
    """
    Creates a process instance structure, automatically sets systemPid, spawnedBy, host and spawnedWhen
    """
    _struct = {
        "_id": _process_id,
        "systemPid": os.getpid(),
        "spawnedBy": get_current_login(),
        "name": _name,
        "host": socket.getfqdn(),
        "spawnedWhen": str(datetime.datetime.utcnow()),
        "schemaRef": "ref://of.process.system"
    }
    if _parent_id:
        _struct["parent_id"] = _parent_id,

    return _struct


def log_process_state_message(_changed_by, _state, _process_id, _reason):
    """
    Created a general process state document
    """
    return {
        "changedBy": _changed_by,
        "changedWhen": str(datetime.datetime.utcnow()),
        "state": _state,
        "reason": _reason,
        "processId": _process_id,
        "schemaRef": "ref://of.log.process_state"
    }

