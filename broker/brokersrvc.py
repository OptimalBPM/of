"""
This module implements windows service functionality for the Optimal Framework

Created on Jan 22, 2016

@author: Nicklas Boerjesson

"""


import os
import servicemanager
import socket
import sys
import win32event
import win32service

import win32serviceutil

# The directory of the current file
script_dir = os.path.dirname(__file__)

# Add relative optimal bpm path
sys.path.append(os.path.join(script_dir, "../../"))

from of.common.win32svc import write_to_event_log
import of.broker.broker


class BrokerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "Optimal BPM Broker Service"
    _svc_display_name_ = "The Optimal BPM Broker Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        _exit_status = of.broker.broker.stop_broker("Shutting down the Broker service")
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        os.exit(_exit_status)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        try:
            of.broker.broker.start_broker()
        except Exception as e:
            write_to_event_log("Application", 1, "Error starting broker", str(e))


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(BrokerService)
