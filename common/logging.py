"""
This is the central logging facility of the Optimal framework.
"""
__author__ = 'Nicklas Borjesson'
import os

# Logging constants

SEV_INFO = 0  # Informational message
SEV_DEBUG = 1  # Debugging level message
SEV_WARNING = 2  # A warning
SEV_ALERT = 3  # Action must be taken immidiately
SEV_USER = 4  # A user error or error that can be corrected by the user
SEV_ERROR = 5  # An error
SEV_FATAL = 6  # Ar error that causes something to stop functioning

ERR_NONE = 0  # Not an error condition
ERR_SECURITY = 1  # A security related error, insufficient permissions or rights
ERR_INTERNAL = 2  # An internal error, likely a bug in the system
ERR_INVALID = 3  # A validation error, some information failed to validate, invalid reference
ERR_COMMUNICATION = 4  # A communications error
ERR_RESOURCE = 5  # A resource error indicating a lack of memory, space or time/cpu
ERR_OTHER = 6  # Uncategorized error


# Human representations

severity_identifiers = ["information",
                        "debug",
                        "warning",
                        "alert",
                        "user",
                        "error",
                        "fatal"]

severity_descriptions = ["informational message",
                         "debugging message",
                         "warning messare",
                         "action must be taken immitiately",
                         "user correctable error",
                         "error",
                         "a fatal error cause loss of functionality"]
errortype_identifiers = ["no error",
                         "security",
                         "internal",
                         "invalid",
                         "communication",
                         "resource",
                         "other"]

errortype_descriptions = ["not an error",
                          "insufficient permissions or rights",
                          "internal error, likely a bug in the system",
                          "validation error, information/structure failed to validate, invalid reference",
                          "error during communication",
                          "error indicating a lack of memory, space or time/cpu",
                          "other, uncategorized error"]
"""Set logging callbar to"""
logging_callback = None


def index_to_string(_index, _array, _error):
    """Returns a matching array item or error message and value"""
    if isinstance(_index, int) and 0 <= _index < len(_array):
        return str(_array[_index])
    else:
        return _error + str(_index)



def write_to_log(_message, _severity=0, _errortype=0, _process_id=None):
    """
    Writes a message to the log using the current facility
    :param _message: The error message
    :param _severity: The severity of the error
    :param _errortype: The kind of error
    :param _process_id: The current process id

    """
    global logging_callback
    if logging_callback is not None:
        logging_callback(_message, _severity, _errortype, _process_id)
    else:
        print("Logging callback not set, print message:\n"+ make_textual_log_message(_message, _severity, _errortype, _process_id))


def make_textual_log_message(_message, _severity = None, _errortype = None, _process_id = None):
    """
    Build a nice textual error message based on available information

    :param _message: The error message
    :param _severity: The severity of the error
    :param _errortype: The kind of log message
    :param _process_id: The current process id
    :return: An error message
    """
    _result= "Process Id: " + (str(_process_id) if _process_id is not None else str(os.getpid()))
    _result+= (" - An error occured:\n" if _severity > 2 else " - Message:\n") + _message
    _result+= "\nSeverity: " + index_to_string(_severity, severity_identifiers, "invalid severity level:") if _severity is not None else ""
    _result+= "\nError Type: " + index_to_string(_errortype, errortype_identifiers, "invalid severity level:") if _errortype is not None else ""

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