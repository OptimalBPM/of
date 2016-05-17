"""
This module exposes the Optimal BPM Broker API as a web service through a CherryPy module
Note that most of its initialisation is performed in the startup ../broker.py
"""

import copy
import time
from multiprocessing import Queue

import cherrypy

from of.common.logging import EC_SERVICE, write_to_log, SEV_DEBUG, EC_NOTIFICATION, EC_PROBE, SEV_WARNING, \
    severity_identifiers, category_identifiers, SEV_ERROR, EC_COMMUNICATION
from of.common.messaging.constants import UNEXPECTED_CONDITION
from of.broker.cherrypy_api.node import CherryPyNode
from of.broker.cherrypy_api.authentication import aop_login_json, aop_check_session, logout, cherrypy_logout
from of.schemas.constants import id_right_admin_everything
from of.common.security.groups import has_right, aop_has_right
from of.broker.lib.node import sanitize_node

from of.schemas.constants import peer_type_to_schema_id


__author__ = 'Nicklas Borjesson'


class CherryPyBroker(object):
    """
    The root web server class of the Optimal BPM Broker.
    It exposes the web services of the broker.
    Note: The web application admin UI is served statically from the /admin folder.
    """

    #: A sessionId-indexed dictionary of logged in peers
    peers = None


    #: Plugin management
    plugins = None

    #: A reference to a Nodes instance
    node = None

    def __init__(self, _process_id, _address, _database_access):
        """
        Initializes the broker web service and includes and initiates the other parts of the API as well
        :param _database_access: A DatabaseAccess instance for database connectivity
        :param _process_id: The system process id of the broker
        :param _address: The peer address of the broker
        :param _stop_broker: A callback to a function that shuts down the broker
        """
        write_to_log(_process_id=_process_id, _category=EC_SERVICE, _severity=SEV_DEBUG,
                     _data="Initializing broker REST API.")
        self.peers = {}
        self.process_id = _process_id
        self.address = _address

        self.node = CherryPyNode(_database_access=_database_access)

    def write_debug_info(self, _data):
        write_to_log(_data=_data, _category=EC_NOTIFICATION, _severity=SEV_DEBUG, _process_id=self.process_id)



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
        # Note: The input to this function is not validated by against the register.json schema and should not be,
        # as it is both a simple structure and would be a potential DOS-voulnerability. All other calls require a valid
        # session cookie before even entering any logic, and are therefore more protected that this function.
        self.write_debug_info("Register called")

        try:
            _data = kwargs["_message"]
            _peer_type = _data["peerType"]
        except KeyError as e:
            write_to_log("Register: A peer at " + str(cherrypy.request.remote.ip) +
                         " tried to register without the " + str(e) + " key in the dict.",
                         _category=EC_PROBE, _severity=SEV_WARNING)
            return None

        try:

            if _data["address"] is None:
                if _peer_type == "admin":
                    # Generate an address, like "admin_root".
                    _address = _peer_type + "_" + kwargs["_user"]["name"]
                else:
                    write_to_log("The " + _peer_type + " peer type must state an address.",
                                 _category=EC_PROBE, _severity=SEV_WARNING)
                    return None
            else:
                _address = _data["address"]

            # TODO: Implement a "defaults" node so that we can return a default empty node here. (PROD-41)

            # Load the matching node for the address
            _condition = {"schemaRef": peer_type_to_schema_id(_peer_type), "address": _address}
            _settings = sanitize_node(self.admin.node._node.find(_condition, kwargs["_user"]))
            _session_id = kwargs["_session_id"]
            self.write_debug_info("New _session_id : " + str(_session_id))

            # Log out any old sessions
            for _curr_session_id, _curr_peer in dict(self.peers).items():
                if _curr_peer["address"] == _address and _curr_session_id != _session_id:
                    self.write_debug_info(
                        "Removing old registration for the peer at " + _address + ": " + _curr_session_id)
                    if "websocket" in _curr_peer:
                        try:
                            self.write_debug_info("Close remaining websocket: " + _address + ": " + _curr_session_id)
                            _curr_peer["websocket"].close(code=UNEXPECTED_CONDITION, reason='Peer logging in again')
                        except Exception as e:
                            self.write_debug_info("Exception doing so, ignoring error: " + str(e))
                    del self.peers[_curr_session_id]

            self.peers[_session_id] = {
                "user": kwargs["_user"],
                "ip": str(cherrypy.request.remote.ip),
                "address": _address,
                "environment": _data["environment"],
                "type": _peer_type,
                "queue": Queue()
            }

            self.write_debug_info("Register: A peer at " + str(
                cherrypy.request.remote.ip) + " registered with this data:" + str(_data))
            return {"session_id": _session_id, "settings": _settings}

        except Exception as e:
            # Wait to take edge off attacks
            time.sleep(3)
            # TODO: Create stats on attempts to block attacking IP:s (PROD-133)

            # report all other errors as probes as it isn't humans making typing errors
            write_to_log("Register: A peer at " + str(
                cherrypy.request.remote.ip) + " failed logging in with this data:" + str(_data) + "\nError:" + str(
                e), _category=EC_PROBE, _severity=SEV_WARNING)

            return None


    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def unregister(self, **kwargs):
        _session_id = kwargs["_session_id"]
        if "session_id" in cherrypy.request.cookie:
            cherrypy.response.cookie = cherrypy_logout(_session_id)


        _peer = self.peers[_session_id]
        if "websocket" in _peer:
            try:
                _peer["websocker"].close()
                write_to_log(_data="Unregister: Closed websocket for address " + _peer["address"] + ".",
                             _category=EC_COMMUNICATION, _severity=SEV_DEBUG)
            except:
                write_to_log(_data="Unregister: Failed closing websocket for address " + _peer["address"] + ".",
                             _category=EC_COMMUNICATION, _severity=SEV_ERROR)

        del self.peers[_session_id]
        return {}

    @cherrypy.expose
    def socket(self):
        """
        Called when a client wants to upgrade to a websocket. Currently only implemented for logging purposes.
        """
        self.write_debug_info("Broker: Got a /socket upgrade web socket request.")

    @cherrypy.expose
    def status(self):
        """
        Method for checking if the broker is up. No session id required and no checks performed.
        :return: The string "up" if the broker is up
        """
        return "up"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @aop_check_session
    def write_to_log(self, **kwargs):
        """
        This function provides a way for registered peers to write to the log even if they have no web socket.
        :param kwargs:
        :return:
        """
        _session_id = kwargs["_session_id"]
        # Only registered peers get to write to the log, other trying is a probe
        if _session_id not in self.peers:
            write_to_log("Client that wasn't registered as peer tried to write to log ",
                         _category=EC_PROBE, _severity=SEV_WARNING)
            return None

        _message = cherrypy.request.json
        write_to_log(_data=_message.get("data"),
                     _category=category_identifiers.index(_message.get("category")),
                     _severity=severity_identifiers.index(_message.get("severity")),
                     _occurred_when=_message.get("occurred_when"),
                     _address=_message.get("address"),
                     _process_id=_message.get("process_id"),
                     _user_id=_message.get("user_id"),
                     _pid=_message.get("pid"),
                     _uid=_message.get("uid"),
                     _node_id=_message.get("node_id")
                     )
        return "{}"


