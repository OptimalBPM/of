"""
This module implements the BPMWebSocket class and maintains the monitor global variable.
"""
import os
import threading
from queue import Empty
import json
import traceback
from time import sleep

from of.common.messaging.constants import GOING_AWAY, ABNORMAL_CLOSE
from of.common.internal import not_implemented

from ws4py.messaging import TextMessage

__author__ = 'Nicklas Borjesson'

"""
The monitor global variable is used to be able to register the web socket with the handler.
This is not optimal, but the ws4py offer no other way to reach outside its contexts, as it has no parameters.
"""
monitor = None


class BPMWebSocket(object):
    """
    This is a parent class that is use by both client- and server-side web sockets to provide Optimal BPM-specifics.
    It monitors a message_queue, and transmits information appearing in that queue to another connected web socket.
    It also handles session information and registering with the central message monitor.
    """

    #: The name of the client
    address = None
    #: The session id of the socket
    session_id = None
    #: The thread responsible for monitoring the queue of messages to be sent.
    monitor_message_queue_thread = None

    #: The message queue of the socket
    message_queue = None
    #: The log prefix of the socket, used to identify where the log item originated
    log_prefix = None

    def init(self, _session_id):
        """
        Initialize the socket, set the session id an register the web socket with the handler, start monitoring queue.
        :param _session_id: The sessionid
        """
        self.session_id = _session_id
        self.log_prefix = str(os.getpid()) + "-" + self.__class__.__name__ + "(No address yet): "

        try:
            monitor.handler.register_web_socket(self)
        except Exception as e:
            raise Exception(self.log_prefix + "BPMWebSocket: Exception registering web socket:" + str(e))

        self.log_prefix = str(os.getpid()) + "-" + self.__class__.__name__ + "(" + str(self.address) + "): "
        self.start_monitoring_message_queue()

    def start_monitoring_message_queue(self):
        """
        Start monitoring the message queue
        """
        self.monitor_message_queue_thread = threading.Thread(target=self.monitor_message_queue,
                                                             name=self.address + " message queue monitor thread")
        self.monitor_message_queue_thread.start()
        print(self.log_prefix + "Message queue thread started: " + str(self.monitor_message_queue_thread.name))


    def opened(self):
        """
        Implement to have something happen when the socket is opened.
        """
        pass

    def received_message(self, message):
        """
        Receives a message from a peer and puts it on the queue

        :param message:
        :return:
        """

        # TODO: For now, we'll just ignore the empty messages(PROD-20)
        if str(message) != "":
            print(self.log_prefix + "Got this message(putting on queue):" + str(message))
            if isinstance(message, TextMessage):
                monitor.queue.put([self, json.loads(str(message))])
            else:
                monitor.queue.put([self, json.loads(message)])

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
                    print(self.log_prefix + "Error sending message:" + str(e) + "\nTraceback:" + traceback.format_exc())
            except Empty:
                pass
            except Exception as e:
                print(self.log_prefix + "Error accessing send queue:" + str(e))


        print(self.log_prefix + "(" + str(self.address) + ") stopped message queue monitoring. Exiting thread \"" +
              str(self.monitor_message_queue_thread.name) + "\"")



    def send_message(self, message):
        """
        Sends a message to the connected counterpart web socket
        :param message: A string containing the message
        """
        print(self.log_prefix + "Sending message:" + str(message))
        # send() below is implemented by multiple inheritance in the subclass. Ignore "unresolved attribute"-warning.
        self.send(bytes(json.dumps(message).encode()))

    def closed(self, code, reason=None):
        """
        Called when the socket is closed.
        :param code: A web socket error code as defined in: http://tools.ietf.org/html/rfc6455#section-7.4.1
        :param reason: A string describing the reason for closing the connection
        """
        # TODO: Handle the rest of the possible web socket error codes

        if code == ABNORMAL_CLOSE:
            print(self.log_prefix + "The connection to " +  self.address + " has been abnormally closed.")
            self.close(code=code, reason=reason)
        else:
            self.monitor_message_queue_thread.terminated = True
            print(self.log_prefix + "Closed, code: " + str(code) + ", reason: " + str(reason))


    def error_handler(self, exception):
        """
        If an unhandled error occurs, unregister at the broker, and close the socket
        """
        print(self.log_prefix + "An exception handle in the socket, closing. Error: " + str(exception))
        monitor.handler.unregister_web_socket(self)

        # Tell the socket to close
        return False
