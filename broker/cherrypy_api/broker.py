"""
This module exposes the Optimal BPM Broker API as a web service through a CherryPy module
Note that most of its initialisation is performed in the startup ../broker.py
"""

import copy
import time
from multiprocessing import Queue

import cherrypy

import of.broker.lib.messaging.websocket
from common.messaging.constants import UNEXPECTED_CONDITION
from mbe.cherrypy import aop_login_json, aop_check_session
from mbe.constants import object_id_right_admin_everything
from mbe.groups import has_right
from mbe.node import sanitize_node
from of.common.messaging.utils import get_environment_data
from of.schemas.constants import peer_type_to_schema_id

__author__ = 'Nicklas Borjesson'


class CherryPyBroker(object):
    """
    The root web server class of the Optimal BPM Broker.
    It exposes the web services of the broker.
    Note: The web application admin UI is served statically from the /admin folder.
    """
    #: The log prefix of the broker
    log_prefix = None

    #: A sessionId-indexed dictionary of logged in peers
    peers = None

    #: Administrative web service
    admin = None

    #: Plugin management
    plugins = None

    #: An reference to an MBE nodes instance
    node = None

    def __init__(self, _process_id, _address, _log_prefix):
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
        self.process_id = _process_id
        self.address = _address

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
        print(self.log_prefix + "Register called")
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

            # TODO: Implement a "defaults" node so that we can return a default empty node here. (PROD-41)

            # Load the matching node for the address
            _condition = {"schemaRef": peer_type_to_schema_id(_peer_type), "address": _address}
            _settings = sanitize_node(self.admin.node._node.find(_condition, kwargs["user"]))
            _session_id = kwargs["session_id"]
            print("New _session_id : " + str(_session_id))

            # Log out any old sessions
            for _curr_session_id, _curr_peer in dict(self.peers).items():
                if _curr_peer["address"] == _address and _curr_session_id != _session_id:
                    print("Removing old registration for the peer at " + _address + ": " +_curr_session_id)
                    if "websocket" in _curr_peer:
                        try:
                            print("Close remaining websocket: " +_address +  ": " +_curr_session_id)
                            _curr_peer["websocket"].close(code=UNEXPECTED_CONDITION, reason='Peer logging in again')
                        except Exception as e:
                            print("Exception doing so, ignoring error: " + str(e))
                    del self.peers[_curr_session_id]


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
                    cherrypy.request.remote.ip) + " failed logging in with this data:" + str(_data) + "\nError:" + str(
                    e))

            return None

    @cherrypy.expose
    def socket(self):
        """
        Called when a client wants to upgrade to a websocket. Currently only implemented for logging purposes.
        """
        print(self.log_prefix + "Broker: Got a /socket upgrade web socket request.")

    @cherrypy.expose
    def status(self):
        """
        Method for checking if the broker is up. No session id required and no checks performed.
        :return: The string "up" if the broker is up
        """
        # TODO: Define what "up" means, this should be a thorough analysis. Should queue monitors be running? (PROD-42)
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

        # TODO: Should be governed by a admin peers right and perhaps moved to /admin (PROD-20)
        _result = []
        # Filter out the unserializable web socket
        for _session in self.peers.values():
            _new_session = copy.copy(_session)
            _new_session["web_socket"] = "removed for serialization"
            _new_session["queue"] = "removed for serialization"
            _result.append(_new_session)

        print("Returning a list of peers:" + str(_result))
        return _result
