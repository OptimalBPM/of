"""
This module implements the OptimalWebSocket class and maintains the monitor global variable.
Created on Jan 22, 2016

@author: Nicklas Boerjesson
"""
import os
import threading
from queue import Empty
import json
import traceback


from of.common.logging import write_to_log, EC_COMMUNICATION, SEV_DEBUG, SEV_ERROR, EC_INTERNAL, SEV_INFO, \
    make_sparse_log_message
import of.common.logging
from of.common.messaging.factory import reply_with_error_message
from of.common.messaging.constants import ABNORMAL_CLOSE

from ws4py.messaging import TextMessage

__author__ = 'Nicklas Borjesson'

"""
The monitor global variable is used to be able to register the web socket with the handler.
This is not optimal, but the ws4py offer no other way to reach outside its contexts, as it has no parameters.
"""
monitor = None


class OptimalWebSocket(object):
    """
    This is a parent class that is use by both client- and server-side web sockets to provide Optimal Framework-specifics.
    It monitors a message_queue, and transmits information appearing in that queue to another connected web socket.
    It also handles session information and registering with the central message monitor.
    """

    #: The peer name of the client the web socket is connected to
    address = None

    #: The peer name of the client the web socket is located on
    address_own = None

    #: The session id of the socket
    session_id = None

    #: The optimal framework process id
    process_id = None
    #: The thread responsible for monitoring the queue of messages to be sent.
    monitor_message_queue_thread = None

    #: The message queue of the socket
    message_queue = None

    # The socket is connected
    connected = None

    #: A string containing the classname and address classname(address) for use with logging
    log_prefix = None

    def init(self, _session_id):
        """
        Initialize the socket, set the session id an register the web socket with the handler, start monitoring queue.
        :param _session_id: The sessionid
        """
        self.session_id = _session_id
        self.log_prefix = str(os.getpid()) + "-" + self.__class__.__name__ + "(No address yet): "
        self.connected = False
        try:
            monitor.handler.register_web_socket(self)
        except Exception as e:
            raise Exception(write_to_log("OptimalWebSocket: Exception registering web socket:" + str(e),
                                         _category=EC_COMMUNICATION, _severity=SEV_ERROR))

        # Generate log prefix string for performance
        self.log_prefix = str(os.getpid()) + "-" + self.__class__.__name__ + "(" + str(self.address) + "): "

        self.start_monitoring_message_queue()

    def write_dbg_info(self, _data):
        write_to_log(self.log_prefix + str(_data),
                     _category=EC_COMMUNICATION, _severity=SEV_DEBUG, _process_id=self.process_id)

    def start_monitoring_message_queue(self):
        """
        Start monitoring the message queue
        """
        self.monitor_message_queue_thread = threading.Thread(target=self.monitor_message_queue,
                                                             name=self.address + " message queue monitor thread")
        self.monitor_message_queue_thread.start()
        self.write_dbg_info("Message queue thread started: " + str(self.monitor_message_queue_thread.name))


    def opened(self):
        """
        Implement to have something happen when the socket is opened.
        """
        self.connected = True

    def received_message(self, message):
        """
        Receives a message from a peer and puts it on the queue

        :param message: The message
        """


        if str(message) != "":
            self.write_dbg_info("Got this message(putting on queue):" + str(message))
            if isinstance(message, TextMessage):
                monitor.queue.put([self, json.loads(str(message))])
            else:
                monitor.queue.put([self, json.loads(message)])
        else:
            self.send_message(reply_with_error_message(_runtime_instance=os.getpid(),
                                                       _error_message="Cannot send empty messages to agent",
                                                       _message={}))


    def queue_message(self, message):
        """
        Puts a message on the message queue
        :param message: The message
        :return:
        """
        self.message_queue.put(message)

    def monitor_message_queue(self):
        """
        Monitors the messages queue. Stops when the queue-threads' terminated attribute is set to True
        """
        self.monitor_message_queue_thread.terminated = False
        while not self.monitor_message_queue_thread.terminated:
            try:
                _message = self.message_queue.get(True, .1)
                try:
                    self.send_message(_message)
                except Exception as e:
                    write_to_log(self.log_prefix + "Error sending message:" + str(e) + "\nTraceback:" + traceback.format_exc(),
                                 _category=EC_COMMUNICATION, _severity=SEV_ERROR)
            except Empty:
                pass
            except Exception as e:
                write_to_log(self.log_prefix + "Error accessing send queue:" + str(e) + "\nTraceback:" + traceback.format_exc(),
                             _category=EC_INTERNAL, _severity=SEV_ERROR)

        self.write_dbg_info(" stopped message queue monitoring. Exiting thread \"" +
              str(self.monitor_message_queue_thread.name) + "\"")



    def send_message(self, message):
        """
        Sends a message to the connected counterpart web socket
        :param message: A string containing the message
        """
        if of.common.logging.severity < SEV_INFO:
            # We cannot use the normal facility here as that would cause recursion
            print(make_sparse_log_message("Sending message:" + str(message), _category=EC_COMMUNICATION,
                                          _severity = SEV_DEBUG, _address=self.address_own, _process_id=self.process_id))
        # send() below is implemented by multiple inheritance in the subclass. Ignore "unresolved attribute"-warning.
        self.send(bytes(json.dumps(message).encode()))

    def closed(self, code, reason=None):
        """
        Called when the socket is closed.
        :param code: A web socket error code as defined in: http://tools.ietf.org/html/rfc6455#section-7.4.1
        :param reason: A string describing the reason for closing the connection
        """
        # TODO: Handle the rest of the possible web socket error codes
        self.connected = False
        if code == ABNORMAL_CLOSE:
            write_to_log(self.log_prefix + "The connection to " +  self.address + " has been abnormally closed.",
                         _category=EC_COMMUNICATION, _severity=SEV_ERROR)
            self.close(code=code, reason=reason)
        else:
            self.monitor_message_queue_thread.terminated = True
            self.write_dbg_info(self.log_prefix + "Closed, code: " + str(code) + ", reason: " + str(reason))


    def error_handler(self, exception):
        """
        If an unhandled error occurs, unregister at the broker, and close the socket
        """
        write_to_log(self.log_prefix + "An exception handle in the socket, closing. Error: " + str(exception),
                                 _category=EC_COMMUNICATION, _severity=SEV_ERROR)
        monitor.handler.unregister_web_socket(self)

        # Tell the socket to close
        return False
