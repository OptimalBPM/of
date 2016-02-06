"""
This module contains the implementation of the WebSocketHandler class
"""
import logging
from threading import Lock

from of.common.messaging.constants import PROTOCOL_ERROR, GOING_AWAY
from of.common.queue.handler import Handler
from of.schemas.constants import schema_categories

__author__ = 'Nicklas Borjesson'


class WebSocketHandler(Handler):
    """
        Message handler adds support to the base handler for handling messages for web sockets
    """
    #: A dictionary containing the peers of the connected web sockets
    peers = None
    #: The Optimal BPM adress of this web socket
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

    def handle_error(self, _web_socket, _error):
        """ Handles and logs errors, decides whether to keep the connection open if an error occurrs

        :param _web_socket: If the sender was external, the web socket
        :param _error: The error
        """
        # TODO: This must become far more fine-grained. Possibly, a severity parameter should be added.(PROD-20)

        self.logging_function(_message=_error, _severity=logging.ERROR)
        print("in handle_error error with error :" + str(_error))
        if _web_socket:
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
            self.handle_error(_web_socket, self.log_prefix + "No category found for schema Id " + str(_schema_id))
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
            print(self.log_prefix + "Handling " + _web_socket.address + " - message : " + str(_message_data))
        else:
            print(self.log_prefix + "Handling outgoing message : " + str(_message_data))

        try:
            _schema_id = _message_data["schemaRef"]
        except KeyError:
            self.handle_error(_web_socket, self.log_prefix + "No schema id found in message.")
            return

        _handler = self.get_handler(_web_socket, _schema_id)

        try:
            _handler(_web_socket, _message_data)
        except Exception as e:
            # TODO: This should really not close the socket, rather return information (PROD-21)
            self.handle_error(_web_socket,
                              self.log_prefix + "Error running handler " + str(_schema_id) + " Error: " + str(e))

    def shut_down(self, _user_id, _code=GOING_AWAY):
        """
        Shut down the handler
        :param _user_id: The user initiating the shut down
        """
        # Stop web sockets
        print(self.log_prefix + "shut_down: Closing sockets..")
        for session in self.peers.values():
            if "web_socket" in session:
                print("Closing " + session["address"])
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
            # Add the peer to the address session dict
            if _web_socket.address in self.address__session:
                print(
                    self.log_prefix + "Register_web_socket: The " + "\"" + _web_socket.address +
                    "\" peer was already registered. Earlier failure to unregister/disconnect? Overwriting the registration.")

            self.address__session[_web_socket.address] = _web_socket.session_id
            print(self.log_prefix + str(_web_socket.address) + " registered, session data: " + str(_session))

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
                print(
                    self.log_prefix + "unregister_web_socket: The " + "\"" + str(
                        _web_socket.address) + "\" peer wasn't registered.")
            if "web_socket" not in self.peers[_web_socket.session_id]:
                print(
                    self.log_prefix + "ERROR: Failing to unregister web socket completely as there is no web socket, " +
                    "address " + str(_web_socket.address) + "session: " +
                    str(self.peers[_web_socket.session_id]))
            else:
                del self.peers[_web_socket.session_id]["web_socket"]
            print(self.log_prefix + "web_socket (address " + str(_web_socket.address) +
                  ", session_id " + str(_web_socket.session_id) + ") unregistered.")
        finally:
            # Unlock
            self.web_socket_lock.release()
