"""
The handler module implements the Handler class.

Created on Jan 22, 2016

@author: Nicklas Boerjesson
"""

import os

from of.common.logging import write_to_log, EC_COMMUNICATION, SEV_DEBUG, EC_NOTIFICATION

__author__ = 'Nicklas Borjesson'


class Handler(object):
    """
    Handler is the base class for all queue item handlers.
    """

    #: The prefix for all log messages
    log_prefix = None
    #: The Optimal BPM process Id
    process_id = None

    #: The last message id, used to keep track of responses.
    _last_message_id = None
    # TODO: This is likely insufficient, look at new solution.

    def __init__(self, _process_id):
        self.process_id = _process_id
        self.log_prefix = str(os.getpid()) + "-" + self.__class__.__name__ + ": "

    def on_monitor_init(self, _monitor):
        """
        Override this to make something happen after the monitor has been initialized.

        :param _monitor: The monitor
        """
        pass

    def write_dbg_info(self, _data):
        """
        Shortcut to writing debug information
        :param _message: The message
        :param _severity: The severity of the log information, a constant defined in the built-in logging module
        """
        write_to_log(self.log_prefix + _data, _category=EC_NOTIFICATION, _severity=SEV_DEBUG, _process_id=self.process_id)


    def handle(self, _item):
        """
        This function is implemented by subclasses and is called when the monitor detects that an item has been queued.
        It is imperative that it doesn't contain synchronous code that might not return or otherwise hang in any way.
        Hint: Only use async I/0 and avoid complex library calls.

        :param _item: The item from the queue
        """
        raise Exception(self.log_prefix + "The required call handler method is not implemented.")

    def shut_down(self, _user_id):
        """
        Called by the monitor when shutting down. Override to provide own actions

        :param _user_id: The Optimal BPM user id

        """

        pass
