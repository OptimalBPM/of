"""
The utils module gathers all utility functions used in messaging
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

from of.common.messaging.factory import get_current_login


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


def register_at_broker(_address, _type, _server, _username, _password, _log_prefix=""):
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
    # TODO: Credentials should not be outputted here in production.(OB1-149)
    print(_log_prefix + "[" + str(datetime.datetime.utcnow()) + "] Registering at broker API.")

    _headers = {'content-type': 'application/json'}
    _response = requests.post(_server + "/register", data=json.dumps(_data), auth=('user', 'pass'), headers=_headers,
                              verify=False)
    if _response.status_code == 500:
        print(_log_prefix + "Broker login failed with internal server error! Exiting.")
        return False
    if _response.status_code != 200:
        print(_log_prefix + "Broker login failed with error + "+ str(_response.status_code) + "! Exiting.")
        return False

    _response_dict = _response.json()
    if _response_dict is not None:
        _data = _response_dict

        if "session_id" in _data:
            print(_log_prefix + "Got a session id:" + _data["session_id"])
            return _data
        else:
            print(_log_prefix + "Broker login failed! Exiting.")
        return False

    else:
        print(_log_prefix + "Broker login failed! Exiting.")
        return False


def call_api(_url, _session_id, _data, _timeout=None):
    _cookie_jar = RequestsCookieJar()
    _cookie_jar.set(name="session_id", value=_session_id, secure=True)

    _headers = {'content-type': 'application/json'}
    print("[" + str(datetime.datetime.utcnow()) + "] Calling API " + _url)

    _response = requests.post(_url, data=json.dumps(_data), headers=_headers, timeout=_timeout,
                              verify=False, cookies=_cookie_jar)
    _response_dict = None

    if _response.status_code != 200:
        print("Response code :" + str(_response.status_code))
        try:
            _response.raise_for_status()
        except Exception as e:
            print("Error in call_api:" + str(e))
            raise Exception("Error in call_api:" + str(e))
    else:
        if _response.content:
            try:
                _response_dict = _response.json()
            except Exception as e:
                print("response.content didn't contain JSON data")
                _response_dict = None

    if _response_dict is not None:

        print("Got a response from " + _url + " :" + str(_response_dict))
        return _response_dict
    else:
        print("Got an empty response from server:" + str(_response.content))
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
    level = 0
    debug_prefix = None

    def handle(self, _record):
        print(self.debug_prefix + ": " + str(_record))

    def __init__(self, _log_prefix=None, _level=None):
        if _log_prefix is not None:
            self.debug_prefix = _log_prefix
        else:
            self.debug_prefix = "No debug_prefix set"

        if _level is not None:
            self.level = _level
        else:
            self.level = logging.INFO
