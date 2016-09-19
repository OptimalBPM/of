"""
The utils module gathers all utility functions used in messaging

Created on Jan 22, 2016

@author: Nicklas Boerjesson
"""

import os
import socket
import platform
import datetime
import json
import logging



import requests
import sys


from requests.cookies import RequestsCookieJar

from of.common.logging import write_to_log, EC_NOTIFICATION, SEV_DEBUG, SEV_FATAL, EC_SERVICE, SEV_ERROR, \
    EC_COMMUNICATION
from of.common.messaging.factory import get_current_login
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress insecure request
# TODO: However, this chould not always be set
urllib3.disable_warnings(InsecureRequestWarning)

# TODO: get_python_versions should be duplicated into of.common.* (PROD-94)

__author__ = 'Nicklas Borjesson'


def make_log_prefix(_name):
    return _name + "(" + str(os.getpid()) + "):"

def sys_modules():
    result = []
    for curr_key in sys.modules.keys():
        result.append(curr_key)

    return result

def get_environment_data():
    def python_versions():
        _major, _minor, _release, _state, _build = sys.version_info
        return str(_major) + "." + str(_minor) + "." + str(_release) + " " + _state + " build " + str(_build)

    return {
        "hostname": socket.gethostname(),
        "implementation": {
            "language": "python",
            "version": python_versions(),
            "modules": sys_modules(),
        },
        "platform": platform.system(),
        "processor": platform.processor(),
        "systemPid": os.getpid(),
        "user": get_current_login(),
    }

def write_dbg_info(_data):
    write_to_log(_data, _category=EC_NOTIFICATION, _severity=SEV_DEBUG)

def register_at_broker(_address, _type, _server, _username, _password, _log_prefix="", _verify_SSL=True):
    _log_prefix = make_log_prefix(_log_prefix)

    _data = {
        "credentials": {
            "usernamePassword": {
                "username": _username,
                "password": _password
            }
        },
        "environment": get_environment_data(),
        "peerType": _type,
        "address": _address
    }
    write_dbg_info(_log_prefix + "[" + str(datetime.datetime.utcnow()) + "] Registering at broker API.")

    _headers = {'content-type': 'application/json'}
    _response = requests.post(_server + "/register", data=json.dumps(_data), auth=('user', 'pass'), headers=_headers,
                              verify=_verify_SSL)
    if _response.status_code == 500:
        write_dbg_info(_log_prefix + "Broker login failed with internal server error! Exiting.")
        return False
    if _response.status_code != 200:
        write_dbg_info(_log_prefix + "Broker login failed with error + "+ str(_response.status_code) + "! Exiting.")
        return False

    _response_dict = _response.json()
    if _response_dict is not None:
        _data = _response_dict

        if "session_id" in _data:
            write_dbg_info(_log_prefix + "Got a session id:" + _data["session_id"])
            return _data
        else:
            write_to_log(_log_prefix + "Broker login failed! Exiting.", _category=EC_SERVICE, _severity=SEV_ERROR)
        return False

    else:
        write_to_log(_log_prefix + "Broker login failed! Exiting.", _category=EC_SERVICE, _severity=SEV_ERROR)
        return False


def call_api(_url, _session_id, _data, _timeout=None, _print_log=None, _verify_SSL=True):
    """

    :param _url:
    :param _session_id:
    :param _data:
    :param _timeout:
    :param _print_log: Do not call write to log
    :return:
    """

    def do_log(_error, _category=EC_NOTIFICATION, _severity=SEV_DEBUG):
        if _print_log:
            print(_error)
        else:
            write_to_log(_data, _category=_category, _severity=_severity)
        return _error

    _cookie_jar = RequestsCookieJar()
    _cookie_jar.set(name="session_id", value=_session_id, secure=True)

    _headers = {'content-type': 'application/json'}

    _response = requests.post(_url, data=json.dumps(_data), headers=_headers, timeout=_timeout,
                              verify=_verify_SSL, cookies=_cookie_jar)

    _response_dict = None

    if _response.status_code != 200:
        do_log("Response code :" + str(_response.status_code))
        try:
            _response.raise_for_status()
        except Exception as e:
            raise Exception(do_log("Error in call_api:" + str(e), _category=EC_COMMUNICATION, _severity=SEV_ERROR))
    else:
        if _response.content:
            try:
                _response_dict = _response.json()
            except Exception as e:
                do_log("response.content didn't contain JSON data", _category=EC_COMMUNICATION, _severity=SEV_ERROR)
                _response_dict = None

    if _response_dict is not None:
        return _response_dict
    else:
        do_log("Got an empty response from server:" + str(_response.content), _category=EC_COMMUNICATION,
                     _severity=SEV_ERROR)

        return None


def make_error(_code, _message):
    return {
        "error_code": _code,
        "message": _message
    }


def message_is_none(_message, _property, _value):
    """
    If a property is unset, return value, otherwise the specified property

    :param _message: The message
    :param _property: The name of the property
    :param _value: The value
    :return: A value
    """
    if _property in _message:
        return _message[_property]
    else:
        return _value


class MultiprocessingLoggingHandler:
    # TODO: Should this be removed or is it used elsewhere?
    level = 0
    debug_prefix = None

    def handle(self, _record):
        write_dbg_info(self.debug_prefix + ": " + str(_record))

    def __init__(self, _log_prefix=None, _level=None):
        if _log_prefix is not None:
            self.debug_prefix = _log_prefix
        else:
            self.debug_prefix = "No debug_prefix set"

        if _level is not None:
            self.level = _level
        else:
            self.level = logging.INFO
