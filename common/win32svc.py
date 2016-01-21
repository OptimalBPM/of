import win32api
import win32security

import win32con
import win32evtlogutil

ph=win32api.GetCurrentProcess()
th = win32security.OpenProcessToken(ph,win32con.TOKEN_READ)
my_sid = win32security.GetTokenInformation(th,win32security.TokenUser)[0]


def write_to_event_log(_log_name, _type, _subject, _message):
    win32evtlogutil.ReportEvent(_log_name, 1, eventType=_type, strings=[_subject, _message],
                                data="Raw\0Data".encode("ascii"), sid=my_sid)

