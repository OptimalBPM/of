import json
import os
import sys
import time
from multiprocessing import Process
from time import sleep

import cherrypy
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient


from mbe.access import DatabaseAccess
from mbe.authentication import init_authentication
from mbe.schema import SchemaTools
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

__author__ = "Nicklas Borjesson"

# The directory of the current file
script_dir = os.path.dirname(__file__)

# Add relative optimal bpm path to be able to load the modules of this repository properly
sys.path.append(os.path.join(script_dir, "../../"))

# IMPORTANT: ALL OPTIMAL FRAMEWORK IMPORTS MUST BE AFTER ADDING THE PATH
from of.broker import run_broker
from of.common.internal import make_log_prefix
from of.common.internal import load_settings, register_signals
from of.common.messaging.factory import store_process_system_document, log_process_state_message
from of.broker.lib.messaging.websocket import BrokerWebSocket
from of.schemas.constants import zero_object_id
from of.schemas.validation import of_uri_handler
from of.broker.cherrypy_api.broker import CherryPyBroker
from of.broker.cherrypy_api.plugins import CherryPyPlugins
from of.broker.lib.definitions import Definitions
from of.broker.cherrypy_api.admin import CherryPyAdmin
from of.broker.lib.messaging.handler import BrokerWebSocketHandler
from of.common.queue.monitor import Monitor
import of.common.messaging.websocket

if os.name == "nt":
    from of.common.win32svc import write_to_event_log

aux_runner = None

"""
Global variables
"""

#: The peer address of the broker
_address = ""
#: A SchemaTools instance, used across the broker TODO: Is this thread/process safe?(ORG-112)
_schema_tools = None
#: A DatabaseAccess instance, used across the broker TODO: Is this thread/process safe?(ORG-112)
_database_access = None

#: The processId of the broker
_process_id = None
#: The root web server class
_root = None
#: The WebSocketPlugin instance
_web_socket_plugin = None
# The web server configuration
_web_config = None
# The plugins instance
_plugins = None

# All definitions, namespaces, plugin settings
_definitions = None

# The prefix to all logging messages
_log_prefix = None


def start_broker():
    """
    Starts the broker; Loads settings, connects to database, registers process and starts the web server.
    """

    global _process_id, _database_access, _address, _web_socket_plugin, _repository_parent_folder, \
        _web_config, _schema_tools, _definitions, _log_prefix

    _process_id = str(ObjectId())

    print("=====Starting broker=============================")
    print("=====Process Id: " + str(_process_id) + "=====")
    try:
        _settings = load_settings()
    except Exception as e:
        write_to_event_log("Application", 1, "Error loading settings", str(e))
        print("Error loading settings:" + str(e))

        return

    # An address is completely neccessary.
    _address = _settings.get("broker", "address", _default=None)
    if not _address or _address == "":
        print("Fatal error: Broker cannot start, missing [broker] address setting in configuration file.")
        raise Exception("Broker cannot start, missing address.")

    _log_prefix = make_log_prefix(_address)

    # TODO: Reorganize. It is likely that almost everything but external database credentials should be stored in the db PROD-105

    # Initialize schema tools (of_uri_handler is later replaced by the general one)
    _schema_tools = SchemaTools(_json_schema_folders=[os.path.join(script_dir, "../schemas/")],
                                _uri_handlers={"of": of_uri_handler})

    _definitions = Definitions()

    print("Load plugin data")
    # Find the plugin directory
    _plugin_dir = _settings.get_path("broker", "plugin_folder", _default="plugins")

    # Load all plugin data
    _plugins = CherryPyPlugins(_plugin_dir=_plugin_dir, _schema_tools=_schema_tools, _definitions=_definitions,
                               _log_prefix=_log_prefix)

    _plugins.call_hook("before_reading", _globals=globals())
    print("===register signal handlers===")
    register_signals(stop_broker)

    # Connect to the database
    _host = _settings.get("database", "host", _default="127.0.0.1")
    _user = _settings.get("database", "username", _default=None)
    _password = _settings.get("database", "password", _default=None)
    if _user:
        # http://api.mongodb.org/python/current/examples/authentication.html
        _client = MongoClient("mongodb://" + _user + ":" + _password + "@" + _host)
    else:
        _client = MongoClient()

    _database_name = _settings.get("database", "database_name", _default="optimalframework")
    _database = _client[_database_name]
    _database_access = DatabaseAccess(_database=_database, _schema_tools=_schema_tools)

    _database_access.save(store_process_system_document(_process_id=_process_id,
                                                        _name="Broker instance(" + _address + ")"),
                          _user=None,
                          _allow_save_id=True)

    # TODO: It is possible that one would like to initialize, or at least read the plugins *before* trying to connect to the database

    # Must have a valid CherryPy version
    if hasattr(cherrypy.engine, "subscribe"):  # CherryPy >= 3.1
        pass
    else:
        raise Exception(_log_prefix + ": This application requires CherryPy >= 3.1 or higher.")
        # cherrypy.engine.on_stop_engine_list.append(_save_data)

    def ssl_path():
        # Figure out the path to the ssl-certificates
        # TODO: Load from database instead. Or not? (PROD-19)
        return os.path.join(os.path.expanduser("~"), "optimalframework")

    # Initialize CherryPy:s global configuration; note that this could be moved into a configuration file
    cherrypy.config.update({
        "tools.encode.on": True,
        "tools.encode.encoding": "utf-8",
        "tools.decode.on": True,
        "tools.trailing_slash.on": True,

        "tools.staticdir.root": os.path.abspath(os.path.dirname(__file__)),
        "server.ssl_module": "builtin",
        # TODO: Remove this when this bug is fixed:
        # https://bitbucket.org/cherrypy/cherrypy/issue/1341/autoreloader-also-fails-if-six-is-present
        "engine.autoreload.on": False,
        'server.socket_host': '0.0.0.0',
        "server.ssl_certificate": os.path.join(ssl_path(), "optimalframework_test_cert.pem"),
        "server.ssl_private_key": os.path.join(ssl_path(), "optimalframework_test_privkey.pem")
    })
    print(_log_prefix + "Starting CherryPy, ssl at " + os.path.join(ssl_path(), "optimalframework_test_privkey.pem"))

    _web_config = {
        # The UI root
        "/": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "ui",
            "tools.trailing_slash.on": True,
            "tools.staticdir.index": "index.html",
        },
        # Note that the web socket handling is put under /socket.
        "/socket": {
            "tools.websocket.on": True,
            "tools.websocket.handler_cls": BrokerWebSocket
        }
    }

    global _root

    cherrypy._global_conf_alias.update(_web_config)
    _web_socket_plugin = WebSocketPlugin(cherrypy.engine)
    _web_socket_plugin.subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.engine.signals.bus.signal_handler.handlers = {'SIGUSR1': cherrypy.engine.signals.bus.graceful}

    # Initialize the decorator-based authentication framework
    init_authentication(_database_access)

    # Initialize root UI
    _root = CherryPyBroker(_process_id=_process_id, _address=_address,
                           _log_prefix=_log_prefix)
    # Initialize messaging
    of.common.messaging.websocket.monitor = Monitor(_handler=BrokerWebSocketHandler(_process_id, _peers=_root.peers,
                                                                                    _database_access=_database_access,
                                                                                    _schema_tools=_database_access.schema_tools,
                                                                                    _address=_address),
                                                    _logging_function=None)

    _root.plugins = _plugins
    _plugins.call_hook("init_ui", _root_object=_root, _definitions=_definitions)

    # Initialize admin user interface /admin
    _admin = CherryPyAdmin(_database_access=_database_access, _process_id=_process_id,
                           _address=_address, _log_prefix=_log_prefix, _stop_broker=stop_broker,
                           _definitions=_definitions, _monitor=of.common.messaging.websocket.monitor, _root_object=_root)
    _admin.plugins = _plugins

    _root.admin = _admin
    _plugins.call_hook("init_admin_ui", _root_object=_admin, _definitions=_definitions)

    # Generate the static content, initialisation
    _plugins.refresh_static(_web_config)

    print(_log_prefix + "Starting web server. Web config:\n" )
    for _curr_key, _curr_config in _web_config.items():
        if "tools.staticdir.dir" in _curr_config:
            print("Path: " + _curr_key + " directory: " +_curr_config["tools.staticdir.dir"])
        else:
            print("Path: " + _curr_key + " - no static dir")

    _plugins.call_hook("pre_webserver_start", web_config=_web_config, globals=globals())
    cherrypy.quickstart(_root, "/", _web_config)


def stop_broker(_reason, _restart=None):
    global _root
    if _restart:
        print(_log_prefix + "--------------BROKER WAS TOLD TO RESTART, shutting down orderly------------")
    else:
        print(_log_prefix + "--------------BROKER WAS TERMINATED, shutting down orderly------------")

    print(_log_prefix + "Process Id: " + str(_process_id))
    print(_log_prefix + "Reason:" + str(_reason))

    _exit_status = 0
    print(_log_prefix + "Stop the monitor")
    try:
        of.common.messaging.websocket.monitor.stop()
    except Exception as e:
        print(_log_prefix + "Exception trying to stop monitor:" + str(e))
        _exit_status += 1
    time.sleep(1)


    # TODO: Terminate all child processes.(ORG-112)

    try:
        _database_access.save(log_process_state_message(_changed_by=zero_object_id,
                                                        _state="killed",
                                                        _process_id=_process_id,
                                                        _reason="Broker was terminated, reason: \"" +
                                                                _reason + "\", shutting down gracefully"),
                              _user=None)

    except Exception as e:
        print(_log_prefix + "Exception trying to write log item to Mongo DB backend:" + str(e))
        _exit_status += 1

    try:

        print(_log_prefix + "Unsubscribing the web socket plugin...")
        _web_socket_plugin.unsubscribe()

        print(_log_prefix + "Stopping the web socket plugin...")
        _web_socket_plugin.stop()

        print(_log_prefix + "Shutting down web server...")
        cherrypy.engine.stop()

        print(_log_prefix + "Web server shut down...")
    except Exception as e:
        print(_log_prefix + "Exception trying to shut down web server:" + str(e))
        _exit_status += 4

    if _restart:
        print(_log_prefix + "Broker was told to restart, so it now starts a new broker instance...")

        _broker_process = Process(target=run_broker, name="optimalframework_broker", daemon=False)
        _broker_process.start()
        _broker_process.join()

    print(_log_prefix + "Broker exiting with exit status " + str(_exit_status))

    if os.name != "nt":
        os._exit(_exit_status)
    else:
        cherrypy.engine.exit()
        return _exit_status
        # TODO: Add monitoring of processes and killing those not responding, log states to broker. (ORG-112)


if __name__ == "__main__":
    start_broker()
