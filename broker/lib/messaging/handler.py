"""
This module holds the BrokerWebSocketHandler class
"""
from of.common.logging import write_to_log, EC_COMMUNICATION, SEV_INFO, SEV_DEBUG, EC_NOTIFICATION, SEV_ERROR
from of.common.messaging.constants import UNACCEPTABLE_DATA, BROKER_SHUTTING_DOWN
from of.common.messaging.handler import WebSocketHandler
from of.schemas.constants import intercept_schema_ids
from of.broker.globals import states, states_lookup

__author__ = 'Nicklas Borjesson'


class BrokerWebSocketHandler(WebSocketHandler):
    """
    This is the main handler class in the Optimal BPM system.
    It is called by the message queue monitor when an item appears on the queue.
    It is responsible for brokering messages between clients, writing their log message to the log
    and write their data to they database.
    """

    #: A DatabaseAccess instance for database connectivity
    database_access = None

    def __init__(self, _process_id, _peers, _schema_tools, _address, _database_access):
        """
        :param _process_id: The processId of the broker
        :param _peers: A dictionary of logged in peers
        :param _schema_tools: A SchemaTools instance for validation
        :param _address: The peer address of the broker
        :param _database_access: A DatabaseAccess instance
        """
        super(BrokerWebSocketHandler, self).__init__(_process_id, _peers, _schema_tools, _address)
        self.database_access = _database_access
        # Create a handler function map based on schema categories. See of.schemas.constants
        self.category_shortcut.update({
            "process": self.handle_process,
            "log": self.handle_logging,
            "message": self.handle_message,
            "control": self.handle_message
        })

    def handle_message(self, _source_web_socket, _message_data):
        """
        Handle a message
        :param _source_web_socket: The source web socket if external
        :param _message_data: The data in the message
        """
        if _source_web_socket is None:
            # Message came from internally, no need to validate.
            _message_data["source"] = self.address
        else:
            self.schema_tools.validate(_message_data)

        # Special case: A process result message should be intercepted and saved to the log.
        if _message_data["schemaRef"] in intercept_schema_ids:
            self.handle_logging(_source_web_socket, _message_data)

        _destination = _message_data["destination"]
        if _destination == self.address:
            # The reason for this is likely that something was instigated by the web client.
            write_to_log("Broker was the addressee, the broker is never a destination for a plain message.",
                         _category=EC_COMMUNICATION, _severity=SEV_ERROR, _process_id=self.process_id)
            return

        try:
            _destination_session = self.peers[self.address__session[_destination]]
        except KeyError:
            if _source_web_socket:
                _source_web_socket.close(code=UNACCEPTABLE_DATA,
                                         reason="Missing or invalid destination = " + _destination)
            else:
                raise KeyError("Missing or invalid destination = " + _destination)
        else:
            _destination_session["web_socket"].queue_message(_message_data)

    def handle_process(self, _web_socket, _process_data):
        """
        Writes incoming process information to the process collection.

        :param _web_socket: The source web socket
        :param _process_data: The data to write.
        """
        # Handle messages that writes to the backend, like process instances
        write_to_log("before saving process information, session: " + str(self.peers[_web_socket.session_id]),
                     _category=EC_NOTIFICATION, _severity=SEV_DEBUG, _process_id=self.process_id)

        self.database_access.save(_process_data, self.peers[_web_socket.session_id]["user"], _allow_save_id=True)

        write_to_log("handle_process succeeded", _category=EC_NOTIFICATION, _severity=SEV_DEBUG,
                     _process_id=self.process_id)

    def handle_logging(self, _web_socket, _log_data):
        """
        Write log items to the log collection

        :param _web_socket: The source web socket
        :param _log_data: The log data to write.
        """

        # Check integrity

        self.database_access.schema_tools.apply(_log_data)
        if _web_socket:
            # TODO: Should writtenBy be in some base log schema? (PROD-32)
            _log_data["writtenBy"] = self.peers[_web_socket.session_id]["user"]["_id"]
            _log_data["address"] = _web_socket.address

        self.database_access.logging.write_log(_log_data)

        write_to_log("handle_logging succeeded", _category=EC_NOTIFICATION, _severity=SEV_DEBUG,
                     _process_id=self.process_id)
        # Store states
        if _log_data["schemaRef"] == "of://log_process_state.json":
            # Handle the objectIds
            _log_data["_id"] = str(_log_data["_id"])
            _log_data["processId"] = str(_log_data["processId"])

            if _log_data["processId"] not in states_lookup:
                states.append(_log_data)
                states_lookup[_log_data["processId"]] = len(states) - 1
            else:
                states[states_lookup[_log_data["processId"]]] = _log_data

    def shut_down(self, _user_id):
        """
        Shut down the handler, also shuts down the worker and message monitors
        :param _user_id: The user_id that initiated the shut down
        :return:
        """
        super(BrokerWebSocketHandler, self).shut_down(_user_id, BROKER_SHUTTING_DOWN)
