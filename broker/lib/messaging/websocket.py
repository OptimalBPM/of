
import time

import cherrypy
from ws4py.websocket import WebSocket

from of.common.messaging.websocket import OptimalWebSocket
import of.common.messaging.websocket
__author__ = 'Nicklas Borjesson'


class BrokerWebSocket(OptimalWebSocket, WebSocket):
    """
    This class holds a connection from a web socket client
    """
    monitor_message_queue_thread = None

    def __init__(self,  sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        self.log_prefix = ""
        self.write_dbg_info("BrokerWebSocket: Peer connected:" + str(cherrypy.request.remote.ip))
        super(BrokerWebSocket, self).__init__(sock, protocols, extensions, environ, heartbeat_freq)

        self.write_dbg_info("BrokerWebSocket: New peer session, init " + str(cherrypy.request.cookie['session_id'].value))
        self.init(_session_id=cherrypy.request.cookie['session_id'].value)

    def close(self, code=1000, reason=''):
        """
        Closes the connection, and unregisters the web socket at the message monitor
        :param code: A web socket error code as defined in optimalbpm.common messaging.constants, information at: http://tools.ietf.org/html/rfc6455#section-7.4.1
        :param reason: A string describing the reason for closing the connection
        """
        self.write_dbg_info(self.log_prefix + "Told to close (session_id:" + str(self.session_id) + ") , code: " + str(code) + ", reason: " + str(reason))
        if self.monitor_message_queue_thread:
            self.monitor_message_queue_thread.terminated = True

        of.common.messaging.websocket.monitor.handler.unregister_web_socket(self)

        super(BrokerWebSocket, self).close(code, reason)

        self.write_dbg_info("Web socket for "+ self.address + " closed.")

    def closed(self, code, reason=None):
        """
        Called when the socket is closed.
        :param code: A web socket error code as defined in: http://tools.ietf.org/html/rfc6455#section-7.4.1
        :param reason: A string describing the reason for closing the connection
        """
        self.write_dbg_info("Closed, code: " + str(code) + ", reason: " + str(reason))

class MockupWebSocket(BrokerWebSocket):
    """
    This is a mockup class to only test the message broker itself.
    """

    on_message = None
    context = None

    def __init__(self, session_id=None, context=None):
        """
        Any changes made here must be reflected in BrokerWebSocket.__init__
        """

        class MockupSocket:
            """ A socket implementation that does *nothing* """

            def __init__(self):
                self.server_terminated = False

            def close(self):
                print("MockupSocket - Told to close.")

            def sendall(self, b):
                pass

        super(BrokerWebSocket, self).__init__(sock=MockupSocket(), protocols=None, extensions=None, environ=None,
                                               heartbeat_freq=None)

        self.session_id = session_id
        self.context = context

        self.init(session_id)

    def received_message(self, message):
        """
        Receives a message from a peer and puts it on the queue
        """
        self.received_last_message_at = time.perf_counter()
        super(MockupWebSocket, self).received_message(message)

    def send_message(self, message):
        """
            Replaces the BrokerWebSocket.send_message
        """
        self.message = message
        self.sent_last_message_at = time.perf_counter()
        if self.on_message:
            self.on_message(self, message)
        print(self.log_prefix + "got a message to send to its peer from " + message["source"])
