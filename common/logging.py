"""
This is the central logging facility of the Optimal framework.

Created on Jan 22, 2016

@author: Nicklas Boerjesson

"""
import datetime

__author__ = 'Nicklas Borjesson'
import os


# Severity levels
SEV_DEBUG = 0  # Debugging message
SEV_INFO = 1  # Informational message
SEV_WARNING = 2  # A warning
SEV_ALERT = 3  # Action must be taken immediately
SEV_USER = 4  # A user error or error that can be corrected by the user
SEV_ERROR = 5  # A problem but doesn't stop execution
SEV_FATAL = 6  # A problem that causes something to stop functioning

# EVENT CATEGORIES

EC_NOTIFICATION = 0  # A notification

# Errors
EC_INTERNAL = 1  # An internal error, likely a bug in the system
EC_INVALID = 2  # A validation error, some information failed to validate, invalid reference
EC_COMMUNICATION = 3  # A communications error
EC_SERVICE = 4 # A service level error, such as a failure to start or configuration errors
EC_RESOURCE = 5  # A resource error indicating a lack of memory, space or time/cpu or other resource
EC_RIGHT = 6  # A security related error, insufficient rights
EC_PERMISSION = 7  # A security related error, insufficient permissions
EC_UNCATEGORIZED = 8  # Uncategorized error

# Node change categories
EC_ADD = 9  # Something was added
EC_REMOVE = 10  # Something was removed
EC_CHANGE = 11  # Something was changed

# Attack categories
EC_PROBE = 12  # The system considers itself being probed
EC_DOS = 13  # The system considers itself being under a denial-of-service attack
EC_BREAKIN = 14  # The system considers itself being broken in to

# Human representations

severity_identifiers = [
    "debug",
    "information",
    "warning",
    "user",
    "alert",
    "error",
    "fatal"
]

severity_descriptions = [
    "debugging message",
    "information message",
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
    "service",
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
    "notification message",
    "internal error, likely a bug in the system",
    "validation error, information/structure failed to validate, invalid reference",
    "error during communication",
    "service",
    "error indicating a lack of memory, space or time/cpu",
    "insufficient rights",
    "insufficient permissions",
    "uncategorized error",
    "node was added",
    "node was removed",
    "node was changed",
    "the system is being probed for vurnerabilities",
    "the system is under a denial-of-service attack",
    "someone is trying to break-in to the system"
]



"""The logging callback"""
callback = None
severity = SEV_WARNING

if os.name == "nt":
    import win32api
    import win32security
    import win32evtlog

    import win32con
    import win32evtlogutil

    ph=win32api.GetCurrentProcess()
    th = win32security.OpenProcessToken(ph,win32con.TOKEN_READ)
    my_sid = win32security.GetTokenInformation(th,win32security.TokenUser)[0]


    eventtype_severity = {
        SEV_DEBUG: win32evtlog.EVENTLOG_INFORMATION_TYPE,
        SEV_INFO: win32evtlog.EVENTLOG_INFORMATION_TYPE,
        SEV_WARNING: win32evtlog.EVENTLOG_WARNING_TYPE,
        SEV_ALERT: win32evtlog.EVENTLOG_INFORMATION_TYPE,
        SEV_USER: win32evtlog.EVENTLOG_ERROR_TYPE,
        SEV_ERROR: win32evtlog.EVENTLOG_ERROR_TYPE,
        SEV_FATAL: win32evtlog.EVENTLOG_ERROR_TYPE
    }

    def write_to_event_log(_data, _log_name,_category,  _severity):
        _strcategory = category_to_description(_category, "invalid category")
        _textual = [_strcategory[0] + _strcategory[1:] + "- severity: " +
            severity_to_identifier(_severity=_severity),
            _data
        ]
        win32evtlogutil.ReportEvent(_log_name, 1, eventType=_severity,
                                    strings = _textual,
                                    data="Raw\0Data".encode("ascii"), sid=my_sid)


def severity_to_identifier(_severity, _error = "invalid severity:"):
    """Returns a matching severity identifiers"""
    if isinstance(_severity, int) and 0 <= _severity < len(severity_identifiers):
        return str(severity_identifiers[_severity])
    else:
        return _error + str(_severity)


def severity_to_description(_severity, _error = "invalid severity:  "):
    """Returns a matching severity description"""
    if isinstance(_severity, int) and 0 <= _severity < len(severity_descriptions):
        return str(severity_descriptions[_severity])
    else:
        return _error + str(_severity)


def category_to_identifier(_category, _error = "invalid category: "):
    """Returns a matching category identifiers"""
    if isinstance(_category, int) and 0 <= _category < len(category_identifiers):
        return str(category_identifiers[_category])
    else:
        return _error + str(_category)


def category_to_description(_category, _error = ""):
    """Returns a matching category description"""
    if isinstance(_category, int) and 0 <= _category < len(category_descriptions):
        return str(category_descriptions[_category])
    else:
        return _error + str(_category)


def write_to_log(_data, _category=EC_NOTIFICATION, _severity=SEV_INFO, _process_id=None, _user_id=None,
                 _occurred_when=None, _address=None, _node_id=None, _uid=None, _pid=None):
    """
    Writes a message to the log using the current facility
    :param _data: The error message
    :param _category: The event category (defaults to CN_NOTIFICATION)
    :param _severity: The severity of the error (defaults to SEV_INFO)
    :param _process_id: The current process id (defaults to the current pid)
    :param _user_id: The Id of the user (defaults to the current username)
    :param _occurred_when: The time of occurrance (defaults to the current time)
    :param _address: The peer address
    :param _node_id: An Id for reference (like a node id)
    :param _uid: The system uid
    :param _pid: The system pid
    """
    global callback, severity
    if _severity < severity:
        return _data

    _occurred_when = _occurred_when if _occurred_when is not None else str(datetime.datetime.utcnow())
    _pid = _pid if _pid is not None else os.getpid()
    _uid = _uid if _uid is not None else os.getlogin()

    if callback is not None:
        callback(_data, _category, _severity, _process_id, _user_id, _occurred_when, _address, _node_id, _uid, _pid)
    else:
        print("Logging callback not set, print message:\n" + make_textual_log_message(_data, _category,
                                                                                      _severity, _process_id, _user_id,
                                                                                      _occurred_when, _address, _node_id,
                                                                                      _uid, _pid))

    return _data

def make_event(_data, _category=None, _severity=None, _process_id=None, _user_id=None,
                             _occurred_when=None, _address=None,_node_id=None, _uid=None, _pid=None):

    _event = (
        {
            "data": _data,
            "category": category_identifiers[_category],
            "severity": severity_identifiers[_severity],
            "uid": _uid,
            "pid": _pid,
            "occurredWhen": _occurred_when,
            "process_id": _process_id,
            "schemaRef": "ref://of.event"
        }
    )
    if _node_id is not None:
        _event["node_id"] = _node_id
    if _user_id is not None:
        _event["user_id"] = _user_id
    if _address is not None:
        _event["address"] = _address
    if _process_id is not None:
        _event["process_id"] = _process_id

    return _event

def make_textual_log_message(_data, _category=None, _severity=None, _process_id=None, _user_id=None,
                             _occurred_when=None, _address=None,_node_id=None, _uid=None, _pid=None):
    """
    Build a nice textual error message based on available information for dialogs or event logs.

    :param _data: The message text or data
    :param _category: The kind of error
    :param _severity: The severity of the error
    :param _process_id: The current process id
    :param _user_id: The Id of the user
    :param _occurred_when: The time of occurrance
    :param _address: The peer address
    :param _node_id: An Id for reference (like a node id)
    :param _uid: The system uid
    :param _pid: The system pid

    :return: An error message

    """

    _result = "Process Id: " + (str(_process_id) if _process_id is not None else "Not available")
    _result += ", Adress: " + (str(_address) if _address is not None else str("None"))
    _result += (" - An error occurred:\n" if _severity > 2 else " - Message:\n") + str(_data)
    _result += "\nEvent category: " + category_to_identifier(_category,
                                                             "invalid event category:") if _category is not None else ""
    _result += "\nSeverity: " + severity_to_identifier(_severity,
                                                       "invalid severity level:") if _severity is not None else ""
    _result += "\nUser Id: " + str(_user_id) if _user_id is not None else ""
    _result += "\nOccurred when: " + str(_occurred_when) if _occurred_when is not None else ""
    _result += "\nEntity Id: " + str(_node_id) if _node_id is not None else ""
    _result += "\nSystem uid: " + (str(_uid) if _uid is not None else str(os.getlogin()))
    _result += "\nSystem pid: " + (str(_pid) if _pid is not None else str(os.getpid()))

    return _result


def make_sparse_log_message(_data, _category=None, _severity=None, _process_id=None, _user_id=None,
                             _occurred_when=None, _address=None, _node_id=None, _uid=None, _pid=None):
    """
    Build a sparse textual error message based on available information. One row unless data is multirow.

    :param _data: The message text or data
    :param _log_type: The type of data
    :param _category: The kind of error
    :param _severity: The severity of the error
    :param _process_id: The current process id
    :param _user_id: The Id of the user
    :param _occurred_when: The time of occurrance
    :param _address: The peer address
    :param _node_id: An Id for reference (like a node id)
    :param _uid: The system uid
    :param _pid: The system pid

    :return: An error message

    """
    if _severity == SEV_DEBUG:
        _prefix = " "
    elif _severity in [SEV_INFO, SEV_ALERT, SEV_WARNING]:
        _prefix = "-"
    else:
        _prefix = "*"

    _result = _prefix + "a: " + (str(_address) if _address is not None else str("None"))
    _result += ", pid: " + (str(_pid) if _pid is not None else str(os.getpid()))
    _result += ", uid: " + (str(_uid) if _uid is not None else str(os.getlogin()))

    if "\n" in _data:
        _result += ", data: (multirow, see below)"
        _result += ", ec: " + category_to_identifier(_category,"INV") if _category is not None else "N/A"
        _result += ", sev: " + severity_to_identifier(_severity,"INV") if _severity is not None else "N/A"
        _result += ", p_id: " + (str(_process_id) if _process_id is not None else "N/A")
        _result += ", u_id: " + str(_user_id) if _user_id is not None else ""
        _result += ", t: " + str(_occurred_when) if _occurred_when is not None else ""
        _result += ", node_id: " + str(_node_id) if _node_id is not None else ""
        _result += "\n===\n" + str(_data) +"\n=== "
    else:
        _result += ", data: " + str(_data) + ", "
        _result += "ec: " + category_to_identifier(_category,"INV") if _category is not None else "N/A"
        _result += ", sev: " + severity_to_identifier(_severity,"INV") if _severity is not None else "N/A"
        _result += ", p_id: " + (str(_process_id) if _process_id is not None else "N/A")
        _result += ", u_id: " + str(_user_id) if _user_id is not None else ""
        _result += ", t: " + str(_occurred_when) if _occurred_when is not None else ""
        _result += ", node_id: " + str(_node_id) if _node_id is not None else ""

    return _result
