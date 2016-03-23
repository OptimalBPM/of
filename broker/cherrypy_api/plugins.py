"""
This module handles the plugin structure of the  the Optimal BPM Admin API as a web service through a CherryPy module
"""
import importlib
import json
import os
import time
from urllib.parse import urlparse
from uuid import UUID
import sys

import cherrypy


from of.broker.cherrypy_api.node import aop_check_session
from of.common.logging import write_to_log, EC_NOTIFICATION, SEV_DEBUG, SEV_ERROR, EC_SERVICE, SEV_INFO

__author__ = 'Nicklas Borjesson'


class CherryPyPlugins(object):
    """
    The CherryPyPlugins class is a plugin for CherryPy to handle the Optimal BPM plug-ins
    """

    """List of plugins"""
    plugins = None

    """Last refresh"""
    last_refresh_time = None

    """ Schema tools instance"""
    schema_tools = None

    """A init string for the client"""
    admin_ui_init = None
    """A init string for SystemJS"""
    admin_systemjs_init = None
    """A list of the available menus"""
    admin_menus = None
    """Reference to the namespaces"""
    namespaces = None
    """The process id (not pid)"""
    process_id = None

    def __init__(self, _plugin_dir, _schema_tools, _namespaces, _process_id):

        self.schema_tools = _schema_tools
        self.last_refresh_time = -31
        self.namespaces = _namespaces
        self.process_id = _process_id

        # Add the parent of plugins to sys path
        sys.path.append(os.path.join(_plugin_dir, ".."))
        self.refresh_plugins(_plugin_dir)

    def validate_uuid(self, _value):
        try:
            UUID(_value, version=4)
            return True
        except:
            return False

    def write_debug_info(self, _data):
        write_to_log(_data=_data, _category=EC_NOTIFICATION, _severity=SEV_DEBUG, _process_id=self.process_id)

    def call_hook(self, _hook_name, **kwargs):
        self.write_debug_info("Running hook " + _hook_name)
        for _curr_plugin_name, _curr_plugin in self.plugins.items():
            if ("failed" in _curr_plugin and _curr_plugin["failed"]):
               self.write_debug_info("Plugin " + _curr_plugin_name+ " marked failed, will not call its hook.")
               continue
            if "hooks" in _curr_plugin:
                if "hooks_instance" in _curr_plugin["hooks"]:
                    _hooks_instance = _curr_plugin["hooks"]["hooks_instance"]
                    if hasattr(_hooks_instance, _hook_name):
                        try:
                            self.write_debug_info("Calling " + _hook_name + " in " + _curr_plugin["description"])
                            getattr(_hooks_instance, _hook_name)(**kwargs)
                        except Exception as e:
                            write_to_log(
                                "An error occurred " + "Calling " + _hook_name + " in " + _curr_plugin_name + ":" + str(
                                    e),
                                _category=EC_SERVICE, _severity=SEV_ERROR)
                            if "failOnError" in _curr_plugin and _curr_plugin["failOnError"]:
                                write_to_log(
                                    "Setting " + _curr_plugin_name + " as Failed. No more hooks will be called for this plugin.",
                                    _category=EC_SERVICE, _severity=SEV_INFO)
                                _curr_plugin["failed"] = True
                            else:
                                write_to_log("Ignores error, this plugin will continue to attempt initialization.",
                                             _category=EC_SERVICE, _severity=SEV_INFO)

    def load_plugin(self, _plugins_dir, _plugin_name):
        # Load definitions.json

        _dirname = os.path.join(_plugins_dir, _plugin_name)
        # TODO: Here any check for licensing should be made to define if a plugin should be loaded.

        self.write_debug_info("Loading plugin: " + _dirname)

        _definitions_filename = os.path.join(_dirname, "definitions.json")
        if not os.path.exists(_definitions_filename):
            raise Exception(
                "Error loading plugin " + _dirname + ", definition file (" + _definitions_filename + ") missing.")

        with open(_definitions_filename) as _f_def:
            _definitions_data = json.load(_f_def)

        _plugin_data = _definitions_data["plugins"][_plugin_name]
        _plugin_data["baseDirectoryName"] = _dirname
        self.write_debug_info("Loading plugin in " + _plugin_data["description"])

        # Load schemas from /schema
        _schema_dir = os.path.join(_dirname, "schemas")
        if os.path.exists(_schema_dir):

            _schema_dir_list = os.listdir(_schema_dir)

            for _curr_file in _schema_dir_list:
                if os.path.splitext(_curr_file)[1] == ".json":
                    self.write_debug_info("Loading schema " + _curr_file)
                    with open(os.path.join(_schema_dir, _curr_file)) as _f_def:
                        _curr_schema = json.load(_f_def)
                    if "namespace" in _curr_schema:
                        # Initiate the namespace (so this row has effect, but should instead be a call. For readability)
                        self.namespaces[_curr_schema["namespace"]]
                        # Store schema among the unresolved ones
                        self._unresolved_schemas[_curr_schema["namespace"] + "://" + _curr_file] = _curr_schema
                    else:
                        self.write_debug_info("No namespace defined in " + _curr_file + ", ignoring.")
        else:
            self.write_debug_info("No schema folder, not loading schemas.")

        # Add server side stuff

        if "hooks" in _plugin_data:
            _broker_definition = _plugin_data["hooks"]
            _hooks_modulename = _broker_definition["hooks_module"]

            try:
                _module = importlib.import_module("plugins." + _plugin_name + "." + _hooks_modulename)
                _broker_definition["hooks_instance"] = _module
            except Exception as e:
                write_to_log("An error occurred importing " + _hooks_modulename + " in " + _plugin_data[
                    "description"] + ":" + str(e),
                             _category=EC_SERVICE, _severity=SEV_ERROR)
                if "failOnError" in _plugin_data and _plugin_data["failOnError"]:
                    write_to_log(
                        "Setting " + _hooks_modulename + " as Failed. No hooks will be called for this plugin.",
                        _category=EC_SERVICE, _severity=SEV_INFO)
                    _plugin_data["failed"] = True
                else:
                    write_to_log("Ignores error, the plugin will continue to attempt initialization.",
                                 _category=EC_SERVICE, _severity=SEV_INFO)

        # Add definitions
        self.namespaces.add_cumulatively(_definitions_data["namespaces"])

        return _plugin_data

    def refresh_plugins(self, _plugins_dir):
        # If < 30 seconds since last refresh (or some other principle)
        _curr_time = time.time()
        if self.last_refresh_time - _curr_time > 30:
            return

        # Reset unresolved schemas
        self._unresolved_schemas = {}

        # Find plugins directory

        if not os.path.exists(_plugins_dir):
            raise Exception("Plugin initialisation failed, no plugin directory where expected(" + _plugins_dir + ")")

        # Loop plugins
        _plugin_names = os.listdir(_plugins_dir)
        self.plugins = {}
        for _plugin_name in _plugin_names:
            if _plugin_name != "__pycache__" and os.path.isdir(os.path.join(_plugins_dir, _plugin_name)):
                self.plugins[_plugin_name] = self.load_plugin(_plugins_dir, _plugin_name)
                self.write_debug_info("Loaded plugin " + _plugin_name)

        # Manually add the optimal framework ("of") namespace
        self.namespaces["of"]["schemas"] = [_curr_ref for _curr_ref in self.schema_tools.json_schema_objects.keys()]
        self.schema_tools.resolver.handlers = {"of": self.uri_handler}

        # Add same resolver for all the rest of the namespaces (these resolvers will persist throughout the system)
        self.schema_tools.resolver.handlers.update(
            {_curr_namespace: self.uri_handler for _curr_namespace in self.namespaces})

        # Resolve all schemas

        for _curr_schema_key, _curr_schema in self._unresolved_schemas.items():
            _resolved_schema = self.schema_tools.resolveSchema(_curr_schema)
            self.namespaces[_resolved_schema["namespace"]]["schemas"].append(_curr_schema_key)
            self.schema_tools.json_schema_objects[_curr_schema_key] = _resolved_schema

        self.write_debug_info("Schemas in " + str(", ").join(
            [_curr_plugin["description"] for _curr_plugin in self.plugins.values()]) + " loaded and resolved:  " +
                              str.join(", ",
                                       ["\"" + _curr_schema["title"] + "\"" for _curr_schema in
                                        self._unresolved_schemas.values()]))

        # Remember refresh
        self.last_refresh_time = _curr_time

    def refresh_static(self, _web_config):
        """
        This function regenerates all the static content that is used to initialize the user interface parts of the
        plugins.
        :param _web_config: An instance of the CherryPy web configuration
        """

        def make_deps(_controller):
            _result = "[" + str(",").join(['"' + _curr_dep + '"' for _curr_dep in _controller["dependencies"]])
            return _result + ", " + _curr_controller["name"] + "]"

        _imports = ""
        _controllers = ""
        _directives = ""
        _routes = ""
        _systemjs = ""
        _admin_menus = []
        # has_right(id_right_admin_everything, kwargs["user"])
        for _curr_plugin_key, _curr_plugin_info in self.plugins.items():
            # Add any plugin configuration for the Admin user interface
            if "admin-ui" in _curr_plugin_info:

                _curr_ui_def = _curr_plugin_info["admin-ui"]
                if "mountpoint" not in _curr_ui_def:
                    write_to_log("Error loading admin-ui for " + _curr_plugin_key + " no mount point.",
                                 _category=EC_SERVICE, _severity=SEV_ERROR)
                    continue
                _mount_point = _curr_ui_def["mountpoint"]

                if _mount_point[0] == "/":
                    write_to_log(
                        "Not mounting " + _mount_point + ", cannot mount admin-specific ui under root(root can "
                                                         "never depend on admin), use root-ui instead.",
                        _category=EC_SERVICE, _severity=SEV_ERROR)
                    continue
                # Mount the static content at a mount point somewhere under /admin
                _web_config.update({
                    "/admin/" + _mount_point: {
                        "tools.staticdir.on": True,
                        "tools.staticdir.dir": os.path.join(_curr_plugin_info["baseDirectoryName"], "admin-ui"),
                        "tools.trailing_slash.on": True
                    }
                })

                _systemjs += "System.config({\"packages\": {\"" + _mount_point + "\": {\"defaultExtension\": \"ts\"}}});\n"

                # Create imports and declarations for controllers and their dependencies
                if "controllers" in _curr_ui_def:
                    for _curr_controller in _curr_ui_def["controllers"]:
                        _imports += "import {" + _curr_controller["name"] + "} from \"" + _curr_controller[
                            "module"] + "\"\n"
                        _controllers += '    app.controller("' + _curr_controller["name"] + '", ' + make_deps(
                            _curr_controller) + ");\n"

                # Create imports and declarations for directives
                if "directives" in _curr_ui_def:
                    for _curr_directive in _curr_ui_def["directives"]:
                        _imports += "import {" + _curr_directive["name"] + "} from \"" + _curr_directive[
                            "module"] + "\"\n"
                        _directives += '    app.directive("' + _curr_directive["name"] + '", ' + _curr_directive[
                            "name"] + ");\n"

                # Add any angular routes
                if "routes" in _curr_ui_def:
                    for _curr_route in _curr_ui_def["routes"]:
                        _routes += "    .when(\"" + _curr_route["path"] + "\", " + json.dumps(
                            _curr_route["route"]) + ")\n"

                # Add menus
                if "menus" in _curr_ui_def:
                    _admin_menus += _curr_ui_def["menus"]

        _result = _imports + "\nexport function initPlugins(app){\n" + _controllers + "\n" + _directives + "\n};\n" + \
                "export function initRoutes($routeProvider) {\n$routeProvider" + _routes + "return $routeProvider }"

        self.admin_ui_init = _result
        self.admin_systemjs_init = _systemjs
        self.admin_menus = _admin_menus

    @cherrypy.expose(alias="admin_init.ts")
    @aop_check_session
    def initialize_admin_plugins(self, **kwargs):
        return self.admin_ui_init

    @cherrypy.expose(alias="admin_menus.json")
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def initialize_admin_menu(self, **kwargs):
        # TODO: Mirror rights here?
        return self.admin_menus

    @cherrypy.expose(alias="admin_jspm_config.js")
    def initialize_admin_systemjs(self, **kwargs):
        return self.admin_systemjs_init

    def uri_handler(self, uri):
        """

        Handle all schema references, also for unresolved schemas

        :param uri: The uri to handle
        :return: The schema
        """
        if uri in self.schema_tools.json_schema_objects:
            return self.schema_tools.json_schema_objects[uri]
        else:
            return self._unresolved_schemas[uri]
