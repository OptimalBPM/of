"""
This is the central logging facility of the Optimal framework.
"""
import datetime

__author__ = 'Nicklas Borjesson'
import os

# Logging constants

SEV_INFO = 0  # Informational message
SEV_DEBUG = 1  # Debugging level message
SEV_WARNING = 2  # A warning
SEV_ALERT = 3  # Action must be taken immidiately
SEV_USER = 4  # A user error or error that can be corrected by the user
SEV_ERROR = 5  # An error that doesn't stop execution
SEV_FATAL = 6  # Ar error that causes something to stop functioning

# Log types

LOG_INFO = 0  # General information

LOG_E_INTERNAL = 1  # An internal error, likely a bug in the system
LOG_E_INVALID = 2  # A validation error, some information failed to validate, invalid reference
LOG_E_COMMUNICATION = 3  # A communications error
LOG_E_RESOURCE = 4  # A resource error indicating a lack of memory, space or time/cpu or other resource
LOG_E_RIGHT = 5  # A security related error, insufficient permissions or rights
LOG_E_PERMISSION = 6  # A security related error, insufficient permissions or rights
LOG_E_UNCATEGORIZED = 7  # Uncategorized error

LOG_ADD = 8  # Something was added
LOG_REMOVE = 9  # Something was removed
LOG_CHANGE = 10  # Something was changed

LOG_PROBE = 11  # The system consider itself being probed
LOG_DOS = 12  # The system consider itself being under a denial-of-service attack
LOG_BREAKIN = 13  # The system consider itself being broken in to

# Human representations

severity_identifiers = ["information",
                        "debug",
                        "warning",
                        "user",
                        "alert",
                        "error",
                        "fatal"]

severity_descriptions = ["informational message",
                         "debugging message",
                         "warning message",
                         "user correctable error",
                         "action must be taken immitiately",
                         "error",
                         "a fatal error cause loss of functionality"]

logtype_identifiers = ["info",
                       "internal",
                       "invalid",
                       "communication",
                       "resource",
                       "right",
                       "permission",
                       "uncategorized",
                       "add",
                       "remove",
                       "change",
                       "probe",
                       "dos",
                       "breakin"
                       ]

logtype_descriptions = ["an informational message",
                        "internal error, likely a bug in the system",
                        "validation error, information/structure failed to validate, invalid reference",
                        "error during communication",
                        "error indicating a lack of memory, space or time/cpu",
                        "insufficient rights",
                        "insufficient permissions",
                        "uncategorized error",
                        "something was added",
                        "something was removed",
                        "something was changed",
                        "the system is being probed for vurnerabilities",
                        "the system is being under a denial-of-service attack"
                        "someone is trying to break-in to the system"]

"""Set logging callbar to"""
logging_callback = None


def index_to_string(_index, _array, _error):
    """Returns a matching array item or error message and value"""
    if isinstance(_index, int) and 0 <= _index < len(_array):
        return str(_array[_index])
    else:
        return _error + str(_index)


def write_to_log(_data, _severity=SEV_INFO, _logtype=LOG_INFO, _process_id=None, _user_id=None, _occured_when=None,
                 _entity_id=None):
    """
    Writes a message to the log using the current facility
    :param _data: The error message
    :param _severity: The severity of the error (defaults to ERR_INFO)
    :param _logtype: The kind of error (defaults to ERR_LOG)
    :param _process_id: The current process id (defaults to the current pid)
    :param _user_id: The Id of the user (defaults to the current username)
    :param _occured_when: The time of occurrance (defaults to the current time)
    :param _entity_id: An Id for reference (like a node id)
    """
    _occured_when = _occured_when if _occured_when is not None else str(datetime.datetime.utcnow())
    _process_id = _process_id if _process_id is not None else os.getpid()
    _user_id = _user_id if _user_id is not None else os.getlogin()
    global logging_callback
    if logging_callback is not None:
        logging_callback(_data, _severity, _logtype, _process_id, _user_id, _occured_when, _entity_id)
    else:
        print("Logging callback not set, print message:\n" + make_textual_log_message(_data, _severity, _logtype,
                                                                                      _process_id, _user_id,
                                                                                      _occured_when, _entity_id))


def make_textual_log_message(_data, _severity=None, _logtype=None, _process_id=None, _user_id=None,
                             _occurred_when=None, _entity_id=None):
    """
    Build a nice textual error message based on available information

    :param _data: The message text or data
    :param _severity: The severity of the error
    :param _logtype: The kind of error
    :param _process_id: The current process id
    :param _user_id: The Id of the user
    :param _occured_when: The time of occurrance
    :param _entity_id: An Id for reference (like a node id)
    :return: An error message

    """

    _result = "Process Id: " + (str(_process_id) if _process_id is not None else str(os.getpid()))
    _result += (" - An error occured:\n" if _severity > 2 else " - Message:\n") + _data
    _result += "\nSeverity: " + index_to_string(_severity, severity_identifiers,
                                                "invalid severity level:") if _severity is not None else ""
    _result += "\nError Type: " + index_to_string(_logtype, logtype_identifiers,
                                                  "invalid severity level:") if _logtype is not None else ""
    _result += "\nUser Id: " + str(_user_id) if _user_id is not None else ""
    _result += "\nOccured when: " + str(_occurred_when) if _occurred_when is not None else ""
    _result += "\nEntity Id: " + str(_entity_id) if _entity_id is not None else ""

    return _result


"""

from mbe.logging import Logging
from of.common.messaging.factory import log_process_state_message
class BPMLogging(Logging):
    def log_process_state(self, _changed_by, _process_id, _state, _reason):
        _data = log_process_state_message(_changed_by=_changed_by, _process_id=_process_id, _state=_state,
                                          _reason=_reason)

        self.write_log(_data)
"""
