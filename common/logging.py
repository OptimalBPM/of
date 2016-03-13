"""
This is the central logging facility of the Optimal framework.
"""
import datetime

__author__ = 'Nicklas Borjesson'
import os

# Severity levels
SEV_INFO = 0  # Informational message
SEV_DEBUG = 1  # Debugging message
SEV_WARNING = 2  # A warning
SEV_ALERT = 3  # Action must be taken immidiately
SEV_USER = 4  # A user error or error that can be corrected by the user
SEV_ERROR = 5  # A problem but doesn't stop execution
SEV_FATAL = 6  # A problem that causes something to stop functioning


# EVENT CATEGORIES

CN_NOTIFICATION = 0  # A notification

# Errors
CE_INTERNAL = 1  # An internal error, likely a bug in the system
CE_INVALID = 2  # A validation error, some information failed to validate, invalid reference
CE_COMMUNICATION = 3  # A communications error
CE_RESOURCE = 4  # A resource error indicating a lack of memory, space or time/cpu or other resource
CE_RIGHT = 5  # A security related error, insufficient permissions or rights
CE_PERMISSION = 6  # A security related error, insufficient permissions or rights
CE_UNCATEGORIZED = 7  # Uncategorized error

# Node change categories
CC_ADD = 8  # Something was added
CC_REMOVE = 9  # Something was removed
CC_CHANGE = 10  # Something was changed

# Attack categories
CA_PROBE = 11  # The system consider itself being probed
CA_DOS = 12  # The system consider itself being under a denial-of-service attack
CA_BREAKIN = 13  # The system consider itself being broken in to

# Human representations

severity_identifiers = [
    "information",
    "debug",
    "warning",
    "user",
    "alert",
    "error",
    "fatal"
]

severity_descriptions = [
    "information message",
    "debugging message",
    "warning message",
    "user correctable error",
    "action must be taken immediately",
    "error",
    "a fatal error cause loss of functionality"
]

category_identifiers = [
    "notification",
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

category_descriptions = [
    "a notification message",
    "internal error, likely a bug in the system",
    "validation error, information/structure failed to validate, invalid reference",
    "error during communication",
    "error indicating a lack of memory, space or time/cpu",
    "insufficient rights",
    "insufficient permissions",
    "uncategorized error",
    "a node was added",
    "a node was removed",
    "a node was changed",
    "the system is being probed for vurnerabilities",
    "the system is under a denial-of-service attack",
    "someone is trying to break-in to the system"
]


"""The logging callback"""
logging_callback = None


def severity_to_identifier(_severity, _error):
    """Returns a matching severity identifiers"""
    if isinstance(_severity, int) and 0 <= _severity < len(severity_identifiers):
        return str(severity_identifiers[_severity])
    else:
        return _error + str(_severity)

def severity_to_description(_severity, _error):
    """Returns a matching severity description"""
    if isinstance(_severity, int) and 0 <= _severity < len(severity_descriptions):
        return str(severity_descriptions[_severity])
    else:
        return _error + str(_severity)

def category_to_identifier(_category, _error):
    """Returns a matching category identifiers"""
    if isinstance(_category, int) and 0 <= _category < len(category_identifiers):
        return str(category_identifiers[_category])
    else:
        return _error + str(_category)

def category_to_description(_category, _error):
    """Returns a matching category description"""
    if isinstance(_category, int) and 0 <= _category < len(category_descriptions):
        return str(category_descriptions[_category])
    else:
        return _error + str(_category)


def write_to_log(_data, _category=CN_NOTIFICATION, _severity=SEV_INFO, _process_id=None, _user_id=None,
                 _occured_when=None,
                 _entity_id=None):
    """
    Writes a message to the log using the current facility
    :param _data: The error message
    :param _log_type: The type of data
    :param _category: The event category (defaults to CN_NOTIFICATION)
    :param _severity: The severity of the error (defaults to SEV_INFO)
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
        logging_callback(_data, _category, _severity, _process_id, _user_id, _occured_when, _entity_id)
    else:
        print("Logging callback not set, print message:\n" + make_textual_log_message(_data, _category,
                                                                                      _severity,
                                                                                      _process_id, _user_id,
                                                                                      _occured_when, _entity_id))


def make_mbe_event(_data, _log_type, _event_category, _severity, _process_id, _user_id, _occured_when, _entity_id):
    pass


def make_textual_log_message(_data, _category=None, _severity=None, _process_id=None, _user_id=None,
                             _occurred_when=None, _entity_id=None):
    """
    Build a nice textual error message based on available information

    :param _data: The message text or data
    :param _log_type: The type of data
    :param _category: The kind of error
    :param _severity: The severity of the error
    :param _process_id: The current process id
    :param _user_id: The Id of the user
    :param _occured_when: The time of occurrance
    :param _entity_id: An Id for reference (like a node id)
    :return: An error message

    """

    _result = "Process Id: " + (str(_process_id) if _process_id is not None else str(os.getpid()))
    _result += (" - An error occured:\n" if _severity > 2 else " - Message:\n") + str(_data)
    _result += "\nEvent category: " + category_to_identifier(_category,
                                                  "invalid event category:") if _category is not None else ""
    _result += "\nSeverity: " + severity_to_identifier(_severity,
                                                "invalid severity level:") if _severity is not None else ""
    _result += "\nUser Id: " + str(_user_id) if _user_id is not None else ""
    _result += "\nOccured when: " + str(_occurred_when) if _occurred_when is not None else ""
    _result += "\nEntity Id: " + str(_entity_id) if _entity_id is not None else ""

    return _result

