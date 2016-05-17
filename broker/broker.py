import os
import sys
import time
from multiprocessing import Process

import cherrypy
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

__author__ = "Nicklas Borjesson"

# The directory of the current file
script_dir = os.path.dirname(__file__)

# Add relative optimal bpm path to be able to load the modules of this repository properly
sys.path.append(os.path.join(script_dir, "../../"))

# IMPORTANT: ALL OPTIMAL FRAMEWORK IMPORTS MUST BE AFTER ADDING THE PATH
import of.common.logging
from of.broker.lib.access import DatabaseAccess
from of.broker.lib.auth_backend import MongoDBAuthBackend
from of.common.cumulative_dict import CumulativeDict
from of.common.logging import write_to_log, SEV_FATAL, EC_SERVICE, SEV_DEBUG, \
    EC_UNCATEGORIZED, SEV_ERROR, SEV_INFO, EC_INVALID, make_sparse_log_message, make_textual_log_message, make_event
from of.common.security.authentication import init_authentication
from of.common.settings import JSONXPath
from of.schemas.schema import SchemaTools
from of.broker import run_broker
from of.common.internal import register_signals, resolve_config_path
from of.common.messaging.factory import store_process_system_document, log_process_state_message
from of.broker.lib.messaging.websocket import BrokerWebSocket
from of.schemas.constants import zero_object_id
from of.schemas.validation import of_uri_handler
from of.broker.cherrypy_api.broker import CherryPyBroker
from of.common.plugins import CherryPyPlugins

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
address = ""
#: A SchemaTools instance, used across the broker TODO: Is this thread/process safe?(ORG-112)
schema_tools = None
#: A DatabaseAccess instance, used across the broker TODO: Is this thread/process safe?(ORG-112)
database_access = None

#: The processId of the broker used to identify the process in logging
process_id = None
# Note: System pids are frequently reused on windows and may conflict on all platforms after reboots

#: The root web server class
web_root = None
#: The WebSocketPlugin instance
web_socket_plugin = None
# The web server configuration
web_config = None
# The plugins instance
plugins = None

# All namespaces
namespaces = None

# The severity when something is logged to the database
log_to_database_severity = None


def write_srvc_dbg(_data):
    global process_id
    write_to_log(_data, _category=EC_SERVICE, _severity=SEV_DEBUG, _process_id=process_id)


def log_locally(_data, _category, _severity, _process_id_param, _user_id, _occurred_when, _address_param, _node_id,
                _uid, _pid):
    global process_id, address

    if _process_id_param is None:
        _process_id_param = process_id
    if _address_param is None:
        _address_param = address
    if os.name == "nt":
        write_to_event_log(make_textual_log_message(_data, _data, _category, _severity, _process_id_param, _user_id,
                                                    _occurred_when, _address_param, _node_id, _uid, _pid),
                           "Application", _category, _severity)
    else:
        print(
            make_sparse_log_message(_data, _category, _severity, _process_id_param, _user_id, _occurred_when,
                                    _address_param, _node_id, _uid,
                                    _pid))
        # TODO: Add support for /var/log/message


def log_to_database(_data, _category, _severity, _process_id_param, _user_id, _occurred_when, _address_param, _node_id,
                    _uid, _pid):
    global log_to_database_severity, process_id, address

    if _process_id_param is None:
        _process_id_param = process_id
    if _address_param is None:
        _address_param = address

    if _severity < log_to_database_severity:
        log_locally(_data, _category, _severity, _process_id_param, _user_id, _occurred_when, _address_param,
                    _node_id, _uid, _pid)
    else:
        try:
            database_access.logging.write_log(make_event(_data, _category, _severity, _process_id_param, _user_id,
                                                         _occurred_when, _address_param, _node_id, _uid, _pid))
        except Exception as e:
            log_locally("Failed to write to database, error: " + str(e), EC_UNCATEGORIZED, SEV_ERROR,
                        _process_id_param, _user_id, _occurred_when, _address_param, _node_id, _uid, _pid)

        log_locally(_data, _category, _severity, process_id, _user_id, _occurred_when, _address_param, _node_id, _uid,
                    _pid)


def start_broker():
    """
    Starts the broker; Loads settings, connects to database, registers process and starts the web server.
    """

    global process_id, database_access, address, web_socket_plugin, repository_parent_folder, \
        web_config, schema_tools, namespaces, log_to_database_severity, plugins

    process_id = str(ObjectId())

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

    log_to_database_severity = of.common.logging.severity_identifiers.index(
        _settings.get("broker/logging/databaseLevel", _default="warning"))

    write_srvc_dbg("Loaded settings from " + _cfg_filename)

    # An address is completely neccessary.
    address = _settings.get("broker/address", _default=None)
    if not address or address == "":
        write_to_log(_data="Broker cannot start, missing [broker] address setting in configuration file.",
                     _category=EC_SERVICE, _severity=SEV_FATAL)
        raise Exception("Broker cannot start, missing address.")

    # TODO: Reorganize. It is likely that almost everything but external database credentials should be stored in the db PROD-105

    # Initialize schema tools (of_uri_handler is later replaced by the general one)
    schema_tools = SchemaTools(_json_schema_folders=[os.path.join(script_dir, "../schemas/")],
                               _uri_handlers={"of": of_uri_handler})

    namespaces = CumulativeDict(_default={"schemas": []})

    write_srvc_dbg("Load plugin data")
    # Find the plugin directory
    _plugin_dir = _settings.get_path("broker/pluginFolder", _default="plugins")

    # Load all plugin data
    plugins = CherryPyPlugins(_plugin_dir=_plugin_dir, _schema_tools=schema_tools, _namespaces=namespaces,
                               _process_id=process_id)


    # Plugins may want to load settings or add globals
    plugins.call_hook("init_broker_scope", _broker_scope=globals(), _settings=_settings)

    write_srvc_dbg("===Register signal handlers===")
    register_signals(stop_broker)
    plugins.call_hook("before_db_connect", _broker_scope=globals())
    # Connect to the database
    _host = _settings.get("broker/database/host", _default="127.0.0.1")
    _user = _settings.get("broker/database/username", _default=None)
    _password = _settings.get("broker/database/password", _default=None)
    if _user:
        write_srvc_dbg("===Connecting to remote MongoDB backend " + _host + "===")
        # http://api.mongodb.org/python/current/examples/authentication.html
        _client = MongoClient("mongodb://" + _user + ":" + _password + "@" + _host)
    else:
        write_srvc_dbg("===Connecting to local MongoDB backend===")
        _client = MongoClient()

    _database_name = _settings.get("broker/database/databaseName", _default="optimalframework")
    write_srvc_dbg("Using database name :" + _database_name)

    _database = _client[_database_name]
    database_access = DatabaseAccess(_database=_database, _schema_tools=schema_tools)
    of.common.logging.callback = log_to_database
    database_access.save(store_process_system_document(_process_id=process_id,
                                                       _name="Broker instance(" + address + ")"),
                         _user=None,
                         _allow_save_id=True)
    plugins.call_hook("after_db_connect", _broker_scope=globals())
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
        return os.path.dirname(_cfg_filename)

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
        "server.ssl_certificate": os.path.join(ssl_path(), "optimalframework_test_cert.pem"),
        "server.ssl_private_key": os.path.join(ssl_path(), "optimalframework_test_privkey.pem")
    })
    write_srvc_dbg("Starting CherryPy, ssl at " + os.path.join(ssl_path(), "optimalframework_test_privkey.pem"))

    web_config = {
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

    global web_root

    cherrypy._global_conf_alias.update(web_config)
    web_socket_plugin = WebSocketPlugin(cherrypy.engine)
    web_socket_plugin.subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.engine.signals.bus.signal_handler.handlers = {'SIGUSR1': cherrypy.engine.signals.bus.graceful}

    # Initialize the decorator-based authentication framework
    init_authentication(MongoDBAuthBackend(database_access))

    # Initialize root UI
    web_root = CherryPyBroker(_process_id=process_id, _address=address, _database_access=database_access)
    # Initialize messaging
    of.common.messaging.websocket.monitor = Monitor(_handler=BrokerWebSocketHandler(process_id, _peers=web_root.peers,
                                                                                    _database_access=database_access,
                                                                                    _schema_tools=database_access.schema_tools,
                                                                                    _address=address))

    web_root.plugins = plugins
    # Generate the static content, initialisation
    plugins.call_hook("init_web", _broker_scope = globals())

    _web_config_debug = "Broker configured. Starting web server. Web config:\n"
    for _curr_key, _curr_config in web_config.items():
        if "tools.staticdir.dir" in _curr_config:
            _web_config_debug += "Path: " + _curr_key + " directory: " + _curr_config["tools.staticdir.dir"]
        else:
            _web_config_debug += "Path: " + _curr_key + " - no static dir"

    write_to_log(_web_config_debug, _category=EC_SERVICE, _severity=SEV_INFO)
    plugins.call_hook("pre_webserver_start", web_config=web_config, globals=globals())
    cherrypy.quickstart(web_root, "/", web_config)


def stop_broker(_reason, _restart=None):
    global web_root, process_id
    if _restart:
        write_to_log("BROKER WAS TOLD TO RESTART, shutting down orderly",
                     _category=EC_SERVICE, _severity=SEV_INFO, _process_id=process_id)
    else:
        write_to_log("BROKER WAS TERMINATED, shutting down orderly",
                     _category=EC_SERVICE, _severity=SEV_INFO, _process_id=process_id)

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
        database_access.save(log_process_state_message(_changed_by=zero_object_id,
                                                       _state="killed",
                                                       _process_id=process_id,
                                                       _reason="Broker was terminated, reason: \"" +
                                                                _reason + "\", shutting down gracefully"),
                             _user=None)

    except Exception as e:
        write_to_log("Exception trying to write log item to Mongo DB backend:" + str(e), _category=EC_SERVICE,
                     _severity=SEV_ERROR)
        _exit_status += 1

    try:

        write_srvc_dbg("Unsubscribing the web socket plugin...")
        web_socket_plugin.unsubscribe()

        write_srvc_dbg("Stopping the web socket plugin...")
        web_socket_plugin.stop()

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
