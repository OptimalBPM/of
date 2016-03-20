"""
This module contains the implementation of the WebSocketHandler class
"""
import logging
from asyncore import write
from threading import Lock

from of.common.logging import write_to_log, SEV_ERROR, EC_COMMUNICATION, EC_PROBE, EC_UNCATEGORIZED, EC_INTERNAL
from of.common.messaging.constants import PROTOCOL_ERROR, GOING_AWAY
from of.common.messaging.factory import reply_with_error_message
from of.common.queue.handler import Handler
from of.schemas.constants import schema_categories

__author__ = 'Nicklas Borjesson'


class WebSocketHandler(Handler):
    """
        Message handler adds support to the base handler for handling messages for web sockets
    """
    #: A dictionary containing the peers of the connected web sockets
    peers = None
    #: The peer adress of this web socket
    address = None
    #: A map between adresses and peers
    address__session = None
    #: An instance of the MBE schema tools
    schema_tools = None
    # Short cut between message categories and handlers
    category_shortcut = None

    def __init__(self, _process_id, _peers, _schema_tools, _address):
        """
        Initialize the handler. create Lock instance
        :param _process_id: The BPM process id of the running scripts
        :param _peers: A dict of logged in peers
        :param _schema_tools: An instance of the mbe SchemaTools class
        :param _address: The peer address of the peer
        """
        super(WebSocketHandler, self).__init__(_process_id)
        self.peers = _peers
        self.address = _address
        self.schema_tools = _schema_tools
        self.address__session = {}
        self.category_shortcut = {}
        self._last_message_id = 0
        self.web_socket_lock = Lock()


    def handle_error(self, _error, _category = EC_COMMUNICATION, _severity = SEV_ERROR,
                     _web_socket= None, _close_socket = None, _message_to_reply_to=None):
        """

        :param _error: The error message
        :param _category: The category of the error
        :param _severity: Error severity
        :param _web_socket: If the sender was external, the web socket
        :param _close_socket: Close the web socket
        :param _message_to_reply_to: The source message, if set, the error message is sent to the sender
        :return:
        """
        """ Handles and logs errors, decides whether to keep the connection open if an error occurrs


        """
        _error = write_to_log(_data=self.log_prefix + "In handler.handle_error error with error :" +
                           str(_error), _category=_category, _severity=_severity)
        if _web_socket:

            if _message_to_reply_to:
                _web_socket.send_message(reply_with_error_message(self, _message_to_reply_to, _error))

            if _close_socket:
                _web_socket.close(code=PROTOCOL_ERROR, reason=_error)

    def get_handler(self, _web_socket, _schema_id):
        """
        Find the appropriate handler for the schema

        :param _web_socket: If applicable, a web socket
        :param _schema_id: The message schema id
        """

        try:
            _category = schema_categories[_schema_id]
        except KeyError:
            # A proper running system should never encounter this error, so this is considered a concious probe
            self.handle_error("No category found for schema Id " + str(_schema_id),
                _web_socket=_web_socket, _category=EC_PROBE, _severity=SEV_ERROR)
            return None
        try:
            return self.category_shortcut[_category]
        except KeyError:
            raise Exception(self.log_prefix + "No handler for category: " + str(_category))

    def handle(self, _item):
        """
        The handle function is called when a monitor finds an unhandled item on its queue.
        The WebSocketHandler uses the schemaRef and schema categories to find the correct handler for the item.
        :param _item: The message
        """

        _web_socket = _item[0]
        _message_data = _item[1]

        if _web_socket:
            self.write_dbg_info("Handling " + _web_socket.address + " - message : " + str(_message_data))
        else:
            self.write_dbg_info("Handling outgoing message : " + str(_message_data))

        try:
            _schema_id = _message_data["schemaRef"]
        except KeyError:
            # A proper running system should never encounter this error, so this is considered a concious probe
            self.handle_error("No schema id found in message",
                _category=EC_PROBE, _severity=SEV_ERROR, _web_socket = _web_socket)
            return

        _handler = self.get_handler(_web_socket, _schema_id)

        try:
            _handler(_web_socket, _message_data)
        except Exception as e:
            self.handle_error("Error running handler " + str(_schema_id) + " Error: " + str(e),
                _category=EC_INTERNAL, _severity=SEV_ERROR, _web_socket = _web_socket)


    def shut_down(self, _user_id, _code=GOING_AWAY):
        """
        Shut down the handler
        :param _user_id: The user initiating the shut down
        """
        # Stop web sockets
        self.write_dbg_info("shut_down: Closing sockets..")
        for session in self.peers.values():
            if "web_socket" in session:
                self.write_dbg_info(session["address"])
                session["web_socket"].close(code=_code, reason="Shutting down")

        super(WebSocketHandler, self).shut_down(_user_id)

    def register_web_socket(self, _web_socket):
        """
        Register a web socket with the handler. Set its address field and message queue.

        :param _web_socket:

        """
        try:
            _session = self.peers[_web_socket.session_id]
        except KeyError:
            raise Exception(self.log_prefix + "Invalid session id:" + _web_socket.session_id)

        self.web_socket_lock.acquire()
        try:

            # Set the web socket of the session
            _session["web_socket"] = _web_socket
            # Set the address of the socket
            _web_socket.address = _session["address"]  # Perhaps the web socket should set this itself, dunno..
            _web_socket.message_queue = _session["queue"]
            _web_socket.process_id = self.process_id
            _web_socket.address_own = self.address
            # Add the peer to the address session dict
            if _web_socket.address in self.address__session:
                self.write_dbg_info("Register_web_socket: The " + "\"" + _web_socket.address +
                    "\" peer was already registered. Earlier failure to unregister/disconnect? Overwriting the registration.")

            self.address__session[_web_socket.address] = _web_socket.session_id
            self.write_dbg_info(str(_web_socket.address) + " registered, session data: " + str(_session))

        finally:
            # Unlock
            self.web_socket_lock.release()

    def unregister_web_socket(self, _web_socket):
        """
        Unregisters the websocket from the handler

        :param _web_socket:
        """
        self.web_socket_lock.acquire()
        try:
            if _web_socket.address in self.address__session:
                del self.address__session[_web_socket.address]
            else:
                # TODO: Should this be a problem?
                self.write_dbg_info("unregister_web_socket: The " + "\"" + str(
                        _web_socket.address) + "\" peer wasn't registered.")
            if "web_socket" not in self.peers[_web_socket.session_id]:
                self.write_dbg_info(
                    self.log_prefix + "ERROR: Failing to unregister web socket completely as there is no web socket, " +
                    "address " + str(_web_socket.address) + "session: " +
                    str(self.peers[_web_socket.session_id]))
            else:
                del self.peers[_web_socket.session_id]["web_socket"]
            self.write_dbg_info(self.log_prefix + "web_socket (address " + str(_web_socket.address) +
                  ", session_id " + str(_web_socket.session_id) + ") unregistered.")
        finally:
            # Unlock
            self.web_socket_lock.release()
