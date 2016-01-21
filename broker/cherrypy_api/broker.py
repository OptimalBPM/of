"""
This module exposes the Optimal BPM Broker API as a web service through a CherryPy module
"""

import copy
import json
import threading
import time
from multiprocessing import Queue

import cherrypy
from mbe.constants import object_id_right_admin_everything
from mbe.groups import has_right
from of.broker.cherrypy_api.plugins import CherryPyPlugins
from of.broker.lib.definitions import Definitions

import of.broker.lib.messaging.websocket
from mbe.authentication import init_authentication
from mbe.cherrypy import CherryPyNode, aop_login_json, aop_check_session
from mbe.node import sanitize_node
from of.broker.lib.messaging.handler import BrokerWebSocketHandler
from of.common.messaging.utils import get_environment_data
from of.common.queue.monitor import Monitor
from of.schemas.constants import peer_type_to_schema_id

__author__ = 'Nicklas Borjesson'


class CherryPyBroker(object):
    """
    The root web server class of the Optimal BPM Broker.
    It exposes the web services of the broker.
    Note: The web application UI is served statically from the optimal/admin folder.
    """
    #: The log prefix of the broker
    log_prefix = None
    #: A sessionId-indexed dictionary of logged in peers
    peers = None

    #: The monitor monitors the message queue.
    monitor = None

    #: Administrative web service
    admin = None
    #: Node management web service(MBE)
    node = None
    #: Plugin management
    plugins = None

    #: All definitions, schemas, and so on
    definitions = None

    #: A storage of the web server web config, used during initialization
    web_config = None

    #: A reference to the stop broker function in the main thread
    stop_broker = None

    #: A database access instance
    database_access = None


    def __init__(self, _database_access, _process_id, _address, _log_prefix, _stop_broker, _repository_parent_folder,
                 _web_config):
        """
        Initializes the broker web service and includes and initiates the other parts of the API as well
        :param _database_access: A DatabaseAccess instance for database connectivity
        :param _process_id: The system process id of the broker
        :param _address: The peer address of the broker
        :param _log_prefix: The log prefix of the broker
        :param _stop_broker: A callback to a function that shuts down the broker
        """
        self.log_prefix = _log_prefix
        print(self.log_prefix + "Initializing broker class.")

        self.peers = {}
        self.web_config = _web_config
        self.definitions = Definitions()

        self.stop_broker = _stop_broker
        self.process_id = _process_id
        self.address = _address
        self.database_access = _database_access

        init_authentication(_database_access)
        self.monitor = Monitor(_handler=BrokerWebSocketHandler(_process_id, _peers=self.peers,
                                                               _database_access=_database_access,
                                                               _schema_tools=_database_access.schema_tools,
                                                               _address=_address), _logging_function=None)

        of.common.messaging.websocket.monitor = self.monitor

        self.node = CherryPyNode(_database_access=_database_access)

        self.plugins = CherryPyPlugins(_repository_parent_folder=_repository_parent_folder,
                                       _database_access=_database_access,
                                       _broker_object=self)


        # TODO: Break out definitions and definition handling in separate class/module definitions["qal"], definition.load_definition

        print(self.log_prefix + "Initializing broker class done.")




    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def get_broker_environment(self, **kwargs):
        has_right(object_id_right_admin_everything, kwargs["user"])
        print("Request for broker information")
        return get_environment_data()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_login_json
    def register(self, **kwargs):
        """
        Register a peer with the web service.
        :param kwargs: A structure containing credentials, environment data, peer type and peer address.
        :return: A structure containing the sessionId and settings of the peer.
        """
        # TODO: Should this get its own schema? (PROD-20)
        try:
            _data = kwargs["message"]
            _peer_type = _data["peerType"]
        except KeyError as e:
            print(self.log_prefix + "Register: A peer at " + str(
                cherrypy.request.remote.ip) + " tried logging without the " + str(e) + " key in the dict.")
            return None

        try:

            if _data["address"] is None:
                if _peer_type == "admin":
                    # Generate an address, like "admin_root".
                    _address = _peer_type + "_" + kwargs["user"]["name"]
                else:
                    raise Exception("The " + _peer_type + " peer type must state an address.")
            else:
                _address = _data["address"]

            # TODO: Implement a "defaults" node so that we can return a default empty node here. (OB1-44)

            # Load the matching node for the address
            _condition = {"schemaId": peer_type_to_schema_id(_peer_type), "address": _address}
            _settings = sanitize_node(self.node._node.find(_condition, kwargs["user"]))
            _session_id = kwargs["session_id"]

            # Should one allow re-registering? Probably. It should be like logging in again, nothing more.
            self.peers[_session_id] = {
                "user": kwargs["user"],
                "ip": str(cherrypy.request.remote.ip),
                "address": _address,
                "environment": _data["environment"],
                "type": _peer_type,
                "queue": Queue()
            }

            print(self.log_prefix + "Register: A peer at " + str(
                cherrypy.request.remote.ip) + " registered with this data:" + str(_data))
            return {"session_id": _session_id, "settings": _settings}

        except Exception as e:
            time.sleep(3)
            # report invalid login attempt
            print(self.log_prefix + "Register: A peer at " + str(
                cherrypy.request.remote.ip) + " failed logging in with this data:" + str(_data) + "\nError:" + str(e))

            return None

    @cherrypy.expose
    def socket(self):
        """
        Called when a client wants to upgrade to a websocket. Currently only implemented for logging purposes.
        """
        print("Broker: Got an /agent request.")

    @cherrypy.expose
    def status(self):
        """
        Method for checking if the broker is up. No session id required and no checks performed.
        :return: The string "up" if the broker is up
        """
        # TODO: Define what "up" means, this should be a thorough analysis. Should queue monitors be running? (OB1-143)
        return "up"

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def get_peers(self, **kwargs):
        """
        Returns a list of all logged in peers
        :param kwargs: Unused here so far, but injected by get session
        :return: A list of all logged in peers
        """

        # TODO: Should be governed by a admin peers right (PROD-20)
        _result = []
        # Filter out the unserializable web socket
        for _session in self.peers.values():
            _new_session = copy.copy(_session)
            _new_session["web_socket"] = "removed for serialization"
            _new_session["queue"] = "removed for serialization"
            _result.append(_new_session)

        print("Returning a list of peers:" + str(_result))
        return _result


    def broker_ctrl(self, _command, _reason, _user):
        """
        Controls the broker's running state

        :param _command: Can be "stop" or "restart".
        :param _user: A user instance
        """
        print("broker.broker_control: Got the command " + str(_command))
        # TODO: There should be a log item written with reason and userid.(OB1-132)
        # TODO: UserId should also be appended to reason below.(OB1-132)

        def _command_local(_local_command):

            if _local_command == "restart":
                self.stop_broker(_reason=_reason, _restart=True)
            if _local_command == "stop":
                self.stop_broker(_reason=_reason, _restart=False)

        _restart_thread = threading.Thread(target=_command_local, args=[_command])
        _restart_thread.start()

        return {}


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def broker_control(self, **kwargs):
        return self.broker_ctrl(cherrypy.request.json["command"],
                                                   cherrypy.request.json["reason"],
                                                   kwargs["user"])