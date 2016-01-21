"""
Created on Nov 6, 2012

@author: Nicklas Boerjesson
@note: This decorator raises an NotImplemented error if a certain method is decorated
"""
import os
import sys
import platform

import signal
from decorator import decorator


# TODO: BPMSettings should probably not be used by QAL(use only resources)optimalbpm.common.* (PROD-94)
from of.common.settings import INISettings

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
    Converts a general Optimal BPM node_id strings to a local one by XOR;ing the MongoDB objectId:s.
    :param _node_id: A node object id
    :param _environment_id: The Optimal BPM environment_id
    :return: The locally usable value
    """
    result = int(_node_id, 16) ^ int(_environment_id, 16)  # convert to integers and xor them together
    return '{:x}'.format(result)


def load_settings():
    """
    Load settings from settings file, first environment variable OPTIMAL_BPM_CFG, then default locations:
    * Windows - %APPDATA%\optimalframework
    * Linux/OSX - ~/ptimalframework

    :return: a qal BPM settings instance
    """

    # TODO: Break out into utils, this exists in broker as well.(OB1-149)

    # TODO: Write settings documentation.(OB1-149)
    if platform.system().lower() in ["linux", "darwin"]:
        # Linux/OSX
        _default_settings_folder = os.path.join(os.path.expanduser("~"), "optimalframework", "main.cfg")
    elif platform.system().lower() == "windows":
        # Windows
        _default_settings_folder = os.path.join(os.getenv("APPDATA"), "optimalframework", "main.cfg")
    else:
        raise Exception("Unsupported platform: " + platform.system().lower())

    _cfg_path = os.path.expanduser(os.getenv("OPTIMAL_FW_CFG", _default_settings_folder))
    print("Config path set to: " + _cfg_path)
    return INISettings(_cfg_path)


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
    print("Windows signal handler called")
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
            print("Registered win32 ctrl handler")
    else:
        signal.signal(signal.SIGINT, signal_handler_unix)
        signal.signal(signal.SIGTERM, signal_handler_unix)
        signal.signal(signal.SIGQUIT, signal_handler_unix)
        signal.signal(signal.SIGHUP, signal_handler_unix)