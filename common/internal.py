"""
This module holds internally used utilities

Created on Nov 6, 2012

@author: Nicklas Boerjesson

"""
import os
import sys
import platform

import signal
from decorator import decorator




from of.common.logging import write_to_log, EC_SERVICE, SEV_INFO

stop_handler = None

def _not_implemented(func, *args, **kwargs):
    raise NotImplementedError('Internal error in "' + func.__name__ + '": Not implemented.')


def not_implemented(f):
    """
    Raises a NotImplementedError error. Example: "Internal error in function_name: Not implemented."
    """
    return decorator(_not_implemented, f)


def node_id_with_env(_node_id, _environment_id):
    """
    Converts a general Optimal Framework node_id strings to a local one by XOR;ing the MongoDB objectId:s.
    :param _node_id: A node object id
    :param _environment_id: The Optimal BPM environment_id
    :return: The locally usable value
    """
    result = int(_node_id, 16) ^ int(_environment_id, 16)  # convert to integers and xor them together
    return '{:x}'.format(result)


def resolve_config_path():
    """
    Load settings from settings file, first environment variable OPTIMAL_BPM_CFG, then default locations:
    * Windows - %APPDATA%\optimalframework
    * Linux/OSX - ~/optimalframework

    :return: a qal BPM settings instance
    """

    if platform.system().lower() in ["linux", "darwin"]:
        # Linux/OSX
        _default_settings_folder = os.path.join(os.path.expanduser("~"), "optimalframework")
    elif platform.system().lower() == "windows":
        # Windows
        _default_settings_folder = os.path.join(os.getenv("USERPROFILE"), "optimalframework")
    else:
        raise Exception("Unsupported platform: " + platform.system().lower())

    return os.path.expanduser(os.getenv("OPTIMAL_FW_CFG", os.path.join(_default_settings_folder, "config.json")))



def signal_handler_unix(_signal, _frame):
    """
    Manage system signals
    :param _signal: The Posix signal See: http://pubs.opengroup.org/onlinepubs/009695399/
    :param _frame: Unused, interrupted stack frame.
    """
    _reason = None
    if _signal == signal.SIGHUP:
        _reason = 'Got SIGTERM, restarting..'
        stop_handler(_reason, _restart=True)
    else:
        if _signal == signal.SIGQUIT:
            _reason = 'Ctrl+D pressed, shutting down..'
        elif _signal == signal.SIGINT:
            _reason = 'Ctrl+C pressed, shutting down..'
        elif _signal == signal.SIGTERM:
            _reason = 'Got SIGTERM, shutting down..'

        stop_handler(_reason)

def signal_handler_windows():
    write_to_log("Windows signal handler called", _category=EC_SERVICE, _severity=SEV_INFO)
    stop_handler('The process has been terminated, shutting down..')

def register_signals(_stop_handler):
    """
    Register a callback to gracefully handle the system being externally shut down (terminated)
    :param _stop_handler: A callback that helps the system shut down gracefully.
    """

    if _stop_handler:
        global stop_handler
        stop_handler = _stop_handler
    else:
        raise Exception("No stop handler, probably an internal error, needed for graceful shut down.")
    if os.name == "nt":
        try:
            import win32api
        except ImportError:
            version = ".".join(map(str, sys.version_info[:2]))
            raise Exception("pywin32 not installed for Python " + version)
        else:
            win32api.SetConsoleCtrlHandler(signal_handler_windows, True)
            write_to_log("Registered win32 ctrl handler", _category=EC_SERVICE, _severity=SEV_INFO)
    else:
        signal.signal(signal.SIGINT, signal_handler_unix)
        signal.signal(signal.SIGTERM, signal_handler_unix)
        signal.signal(signal.SIGQUIT, signal_handler_unix)
        signal.signal(signal.SIGHUP, signal_handler_unix)


def make_log_prefix(_address):
    """
    Create the log prefix for a broker, used in log texts.
    """
    return str(os.getpid()) + "-" + _address + ":"

