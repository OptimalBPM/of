"""
The admin module holds the CherryPy implementation of the admin interface.
Note that most of its initialisation happens in the broker init script, ../broker.py
"""
import copy
import threading

import cherrypy

from mbe.cherrypy import aop_check_session
from mbe.cherrypy import CherryPyNode
from mbe.constants import object_id_right_admin_everything
from mbe.groups import aop_has_right


class CherryPyAdmin(object):
    """
    The CherryPyAdmin class is a plugin for CherryPy that shows the admin UI for the Optimal Framework
    """


    #: The log prefix of the broker
    log_prefix = None

    #: Plugin management
    plugins = None

    #: A reference to the stop broker function in the main thread
    stop_broker = None

    #: A reference to root object (broker)
    root = None

    #: Node management web service(MBE)
    node = None

    def __init__(self,_database_access, _process_id, _address, _log_prefix, _stop_broker, _definitions, _monitor, _root_object):
        print(_log_prefix + "Initializing Admin class.")

        self.stop_broker = _stop_broker
        self.log_prefix = _log_prefix
        self.monitor = _monitor

        self.process_id = _process_id
        self.address = _address
        self.database_access = _database_access
        self.node = CherryPyNode(_database_access=_database_access)
        self.root = _root_object

    def broker_ctrl(self, _command, _reason, _user):
        """
        Controls the broker's running state

        :param _command: Can be "stop" or "restart".
        :param _user: A user instance
        """
        print(self.log_prefix + "broker.broker_control: Got the command " + str(_command))
        # TODO: There should be a log item written with reason and userid.(PROD-32)
        # TODO: UserId should also be appended to reason below.(PROD-32)

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
                                                   kwargs["_user"])

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    @aop_has_right([object_id_right_admin_everything])
    def get_peers(self, **kwargs):
        """
        Returns a list of all logged in peers
        :param kwargs: Unused here so far, but injected by get session
        :return: A list of all logged in peers
        """


        _result = []
        # Filter out the unserializable web socket
        for _session in self.root.peers.values():
            _new_session = copy.copy(_session)
            _new_session["web_socket"] = "removed for serialization"
            _new_session["queue"] = "removed for serialization"
            _result.append(_new_session)

        print("Returning a list of peers:" + str(_result))
        return _result
