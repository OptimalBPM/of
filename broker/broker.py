import os
import sys
import time

from multiprocessing import Process

import cherrypy
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
import of.common.logging

from of.common.logging import write_to_log, SEV_FATAL, EC_SERVICE, SEV_DEBUG, \
    EC_UNCATEGORIZED, SEV_ERROR, SEV_INFO, EC_INVALID, make_sparse_log_message, make_textual_log_message
from mbe.access import DatabaseAccess
from mbe.authentication import init_authentication
from mbe.misc.schema_mongodb import mbe_object_id
from mbe.schema import SchemaTools
from of.common.settings import JSONXPath

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

__author__ = "Nicklas Borjesson"

# The directory of the current file
script_dir = os.path.dirname(__file__)

# Add relative optimal bpm path to be able to load the modules of this repository properly
sys.path.append(os.path.join(script_dir, "../../"))

# IMPORTANT: ALL OPTIMAL FRAMEWORK IMPORTS MUST BE AFTER ADDING THE PATH
from of.broker import run_broker
from of.common.internal import register_signals, resolve_config_path
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
    from of.common.logging import write_to_event_log

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

#: The processId of the broker used to identify the process in logging
_process_id = None
# Note: System pids are frequently reused on windows and may conflict on all platforms after reboots

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

# The severity when something is logged to the database
_log_to_database_severity = None


def write_srvc_dbg(_data):
    global _process_id
    write_to_log(_data, _category=EC_SERVICE, _severity=SEV_DEBUG, _process_id=_process_id)


def log_locally(_data, _category, _severity, _process_id, _user_id, _occurred_when, _node_id, _uid, _pid):
    if os.name == "nt":
        write_to_event_log(make_textual_log_message(_data, _data, _category, _severity, _process_id, _user_id,
                                                    _occurred_when, _node_id, _uid, _pid),
                           "Application", _category, _severity)
    else:
        print(
            make_sparse_log_message(_data, _category, _severity, _process_id, _user_id, _occurred_when, _node_id, _uid,
                                     _pid))
        # TODO: Add support for /var/log/message


def log_to_database(_data, _category, _severity, _process_id_param, _user_id, _occurred_when, _node_id, _uid, _pid):
    global _log_to_database_severity, _process_id

    if _process_id_param is None:
        _process_id_param = _process_id

    if _severity < _log_to_database_severity:
        log_locally(_data, _category, _severity, _process_id_param, _user_id, _occurred_when, _node_id, _uid, _pid)
    else:
        try:
            _database_access.logging.write_log(
                {
                    "user_id": mbe_object_id(_user_id),
                    "data": _data,
                    "uid": _uid,
                    "pid": _pid,
                    "occurredWhen": _occurred_when,
                    "category": _category,
                    "process_id": _process_id_param,
                    "node_id": _node_id,
                    "schemaRef": "mbe://event.json"
                }
            )
        except Exception as e:
            log_locally("Failed to write to database, error: " + str(e), EC_UNCATEGORIZED, SEV_ERROR,
                        _process_id_param, _user_id, _occurred_when, _node_id, _uid, _pid)

        log_locally(_data, _category, _severity, _process_id, _user_id, _occurred_when, _node_id, _uid, _pid)


def start_broker():
    """
    Starts the broker; Loads settings, connects to database, registers process and starts the web server.
    """

    global _process_id, _database_access, _address, _web_socket_plugin, _repository_parent_folder, \
        _web_config, _schema_tools, _definitions, _log_to_database_severity

    _process_id = str(ObjectId())

    of.common.logging.callback = log_locally

    write_srvc_dbg("=====Starting broker=============================")

    try:
        _cfg_filename = resolve_config_path()
        _settings = JSONXPath(_cfg_filename)

    except Exception as e:
        if os.name == "nt":
            write_to_log(_data="Error loading settings from " + _cfg_filename,
                         _category=EC_SERVICE, _severity=SEV_FATAL)
        raise Exception("Error loading settings:" + str(e))

    of.common.logging.severity = of.common.logging.severity_identifiers.index(
        _settings.get("broker/logging/severityLevel", _default="warning"))

    _log_to_database_severity = of.common.logging.severity_identifiers.index(
        _settings.get("broker/logging/databaseLevel", _default="warning"))

    write_srvc_dbg("Loaded settings from " + _cfg_filename)

    # An address is completely neccessary.
    _address = _settings.get("broker/address", _default=None)
    if not _address or _address == "":
        write_to_log(_data="Broker cannot start, missing [broker] address setting in configuration file.",
                     _category=EC_SERVICE, _severity=SEV_FATAL)
        raise Exception("Broker cannot start, missing address.")

    # TODO: Reorganize. It is likely that almost everything but external database credentials should be stored in the db PROD-105

    # Initialize schema tools (of_uri_handler is later replaced by the general one)
    _schema_tools = SchemaTools(_json_schema_folders=[os.path.join(script_dir, "../schemas/")],
                                _uri_handlers={"of": of_uri_handler})

    _definitions = Definitions()

    write_srvc_dbg("Load plugin data")
    # Find the plugin directory
    _plugin_dir = _settings.get_path("broker/pluginFolder", _default="plugins")

    # Load all plugin data
    _plugins = CherryPyPlugins(_plugin_dir=_plugin_dir, _schema_tools=_schema_tools, _definitions=_definitions,
                               _process_id=_process_id)

    write_srvc_dbg("===register signal handlers===")
    register_signals(stop_broker)
    _plugins.call_hook("before_db_connect", _globals=globals())
    # Connect to the database
    _host = _settings.get("broker/database/host", _default="127.0.0.1")
    _user = _settings.get("broker/database/username", _default=None)
    _password = _settings.get("broker/database/password", _default=None)
    if _user:
        write_srvc_dbg("===Connect to remote MongoDB backend " + _host + "===")
        # http://api.mongodb.org/python/current/examples/authentication.html
        _client = MongoClient("mongodb://" + _user + ":" + _password + "@" + _host)
    else:
        write_srvc_dbg("===Connect to local MongoDB backend===")
        _client = MongoClient()

    _database_name = _settings.get("broker/database/databaseName", _default="optimalframework")
    write_srvc_dbg("to database name :" + _database_name)

    _database = _client[_database_name]
    _database_access = DatabaseAccess(_database=_database, _schema_tools=_schema_tools)
    of.common.logging.callback = log_to_database
    _database_access.save(store_process_system_document(_process_id=_process_id,
                                                        _name="Broker instance(" + _address + ")"),
                          _user=None,
                          _allow_save_id=True)
    _plugins.call_hook("after_db_connect", _globals=globals())
    # TODO: It is possible that one would like to initialize, or at least read the plugins *before* trying to connect to the database

    # Must have a valid CherryPy version
    if hasattr(cherrypy.engine, "subscribe"):  # CherryPy >= 3.1
        pass
    else:
        write_to_log(_data="This application requires CherryPy >= 3.1 or higher.", _category=EC_SERVICE,
                     _severity=SEV_FATAL)
        raise Exception("Broker init: This application requires CherryPy >= 3.1 or higher.")
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
    write_srvc_dbg("Starting CherryPy, ssl at " + os.path.join(ssl_path(), "optimalframework_test_privkey.pem"))

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
    _root = CherryPyBroker(_process_id=_process_id, _address=_address)
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
                           _address=_address, _stop_broker=stop_broker,
                           _definitions=_definitions, _monitor=of.common.messaging.websocket.monitor,
                           _root_object=_root)
    _admin.plugins = _plugins

    _root.admin = _admin
    _plugins.call_hook("init_admin_ui", _root_object=_admin, _definitions=_definitions)

    # Generate the static content, initialisation
    _plugins.refresh_static(_web_config)

    _web_config_debug = "Broker configured. Starting web server. Web config:\n"
    for _curr_key, _curr_config in _web_config.items():
        if "tools.staticdir.dir" in _curr_config:
            _web_config_debug += "Path: " + _curr_key + " directory: " + _curr_config["tools.staticdir.dir"]
        else:
            _web_config_debug += "Path: " + _curr_key + " - no static dir"

    write_to_log(_web_config_debug, _category=EC_SERVICE, _severity=SEV_INFO)
    _plugins.call_hook("pre_webserver_start", web_config=_web_config, globals=globals())
    cherrypy.quickstart(_root, "/", _web_config)


def stop_broker(_reason, _restart=None):
    global _root, _process_id
    if _restart:
        write_to_log("BROKER WAS TOLD TO RESTART, shutting down orderly",
                     _category=EC_SERVICE, _severity=SEV_INFO, _process_id=_process_id)
    else:
        write_to_log("BROKER WAS TERMINATED, shutting down orderly",
                     _category=EC_SERVICE, _severity=SEV_INFO, _process_id=_process_id)

    write_srvc_dbg("Reason:" + str(_reason))

    _exit_status = 0
    write_srvc_dbg("Stop the monitor")
    try:
        of.common.messaging.websocket.monitor.stop()
    except Exception as e:
        write_to_log("Exception trying to stop monitor:", _category=EC_INVALID)
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
        write_to_log("Exception trying to write log item to Mongo DB backend:" + str(e), _category=EC_SERVICE,
                     _severity=SEV_ERROR)
        _exit_status += 1

    try:

        write_srvc_dbg("Unsubscribing the web socket plugin...")
        _web_socket_plugin.unsubscribe()

        write_srvc_dbg("Stopping the web socket plugin...")
        _web_socket_plugin.stop()

        write_srvc_dbg("Shutting down web server...")
        cherrypy.engine.stop()

        write_srvc_dbg("Web server shut down...")
    except Exception as e:
        write_to_log("Exception trying to shut down web server:" + str(e), _category=EC_SERVICE,
                     _severity=SEV_ERROR)
        _exit_status += 4

    if _restart:
        write_srvc_dbg("Broker was told to restart, so it now starts a new broker instance...")

        _broker_process = Process(target=run_broker, name="optimalframework_broker", daemon=False)
        _broker_process.start()
        _broker_process.join()

    write_srvc_dbg("Broker exiting with exit status " + str(_exit_status))

    if os.name != "nt":
        os._exit(_exit_status)
    else:
        cherrypy.engine.exit()
        return _exit_status
        # TODO: Add monitoring of processes and killing those not responding, log states to broker. (ORG-112)


if __name__ == "__main__":
    start_broker()
