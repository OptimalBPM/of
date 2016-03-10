"""
This is the central logging facility of the Optimal framework.
"""

SEV_INFO = 0 # Informational message
SEV_DEBUG = 1 # Debugging level message
SEV_WARNING = 2 # A warning
SEV_ALERT = 3 # Action must be taken immidiately
SEV_USER = 4 # A user error or error that can be corrected by the user
SEV_ERROR = 5 # An error
SEV_FATAL = 6 # Ar error that causes something to stop functioning

ERR_NONE = 0 # Not an error condition
ERR_SECURITY = 1 # A security related error, insufficient permissions or rights
ERR_INTERNAL = 2 # An internal error, likely a bug in the system
ERR_INVALID = 4 # A validation error, some information failed to validate, invalid reference
ERR_COMMUNICATION = 5 # A communications error
ERR_RESOURCE = 6 # A resource error indicating a lack of memory, space or time/cpu
ERR_OTHER = 7 # Uncategorized error

log_callback = None


def write_to_log(_message, _severity = 0, _type = 0, _process_id = None):
    global log_callback
    if log_callback is not None:
        log_callback(_message, _severity, _type, _process_id)


def severity_to_identifier():
    """Returns a list of supported database engines"""
    return ["information",
            "debug",
            "warning",
            "alert",
            "user",
            "error",
            "fatal"]

def severity_to_description():
    """Returns a list of supported database engines"""
    return ["informational message",
            "debugging message",
            "warning messare",
            "action must be taken immitiately",
            "user correctable error",
            "error",
            "a fatal error cause loss of functionality"]


def errortype_to_identifier():
    """Returns a list of supported database engines"""
    return ["no error",
            "security",
            "internal",
            "invalid",
            "communication"]

def errortype_to_description():
    """Returns a list of supported database engines"""
    return ["not an error",
            "insufficient permissions or rights",
            "internal error, likely a bug in the system",
            "validation error, information/structure failed to validate, invalid reference",
            "error during communication",
            "error indicating a lack of memory, space or time/cpu",
            "other, uncategorized error"]

