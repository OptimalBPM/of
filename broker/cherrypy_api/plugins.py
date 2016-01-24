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

from of.common.internal import make_log_prefix
from mbe.cherrypy import aop_check_session


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

    """An instance of the broker root object"""
    broker = None

    """A init string for the client"""
    admin_ui_init = None
    """A init string for SystemJS"""
    admin_systemjs_init = None
    """A list of the available menus"""
    admin_menus = None
    """Reference to the definition"""
    definitions = None

    def __init__(self, _plugin_dir, _schema_tools, _definitions, _log_prefix):

        self.schema_tools = _schema_tools
        self.last_refresh_time = -31
        self.definitions = _definitions
        self.refresh_plugins(_plugin_dir)
        self.log_prefix = _log_prefix

    def validate_uuid(self, _value):
        try:
            UUID(_value, version=4)
            return True
        except:
            return False


    def call_hook(self, _hook_name, **kwargs):
        print(self.log_prefix + "Running hook " + _hook_name)
        for _curr_plugin in self.plugins.values():
            if not("failed" in _curr_plugin and _curr_plugin["failed"]) and "hooks" in _curr_plugin:
                if "hooks_instance" in _curr_plugin["hooks"]:
                    _hooks_instance = _curr_plugin["hooks"]["hooks_instance"]
                    if hasattr(_hooks_instance, _hook_name):
                        try:
                            print(self.log_prefix + "Calling " + _hook_name + " in " + _curr_plugin["description"])
                            getattr(_hooks_instance, _hook_name)(**kwargs)
                        except Exception as e:
                            print(self.log_prefix + "An error occured "+ "Calling " + _hook_name + " in " + _curr_plugin["description"] + ":" + str(e))
                            if "FailOnError" in _curr_plugin and _curr_plugin["FailOnError"]:
                                print(self.log_prefix + "Setting as Failed. No more hooks will be called for this plugin.")
                                _curr_plugin["failed"] = True
                            else:
                                print(self.log_prefix + "Ignores error, this plugin will continue to attempt initialization.")




    def load_plugin(self, _dirname):
        # Load definitions.json


        # TODO: Here any check for licensing should be made to define if a plugin should be loaded.

        print("Loading plugin: " + _dirname)

        _definitions_filename = os.path.join(_dirname, "definitions.json")
        if not os.path.exists(_definitions_filename):
            raise Exception(
                "Error loading plugin " + _dirname + ", definition file (" + _definitions_filename + ") missing.")

        with open(_definitions_filename) as _f_def:
            _definitions = json.load(_f_def)

        _definitions["baseDirectoryName"] = _dirname
        print("Loading plugin in " + _definitions["description"])


        def set_unresolved(_name, _schema):
            _namespace = _schema["namespace"]
            if not _namespace in self._unresolved_schemas:
                self._unresolved_schemas[_namespace] = {_name: _schema}
            else:
                self._unresolved_schemas[_namespace][_name] = _schema


        # Load schemas from /schema
        _schema_dir = os.path.join(_dirname, "schemas")
        if os.path.exists(_schema_dir):

            self.schema_tools.load_schemas_from_directory(_schema_dir)
            _schema_dir_list = os.listdir(_schema_dir)

            for _curr_file in _schema_dir_list:
                if os.path.splitext(_curr_file)[1] == ".json":
                    print("Loading schema " + _curr_file)
                    with open(os.path.join(_schema_dir, _curr_file)) as _f_def:
                        _curr_schema = json.load(_f_def)
                    if "namespace" in _curr_schema:
                        self.definitions[_curr_schema["namespace"]]
                        set_unresolved(_curr_file, _curr_schema)
                    else:
                        print(make_log_prefix() + "No namespace defined in " + _curr_file + ", ignoring.")
        else:
            print(make_log_prefix() + "No schema folder, not loading schemas.")


        # Add server side stuff

        if "hooks" in _definitions:
            _broker_definition = _definitions["hooks"]
            hooks_modulename = _broker_definition["hooks_module"]
            sys.path.append(_dirname)
            try:
                _module = importlib.import_module(hooks_modulename)
            except Exception as e:
                print(self.log_prefix + "An error occured importing " + hooks_modulename + " in " + _definitions["description"] + ":" + str(e))
                if "FailOnError" in _definitions and _definitions["FailOnError"]:
                    print(self.log_prefix + "Setting as Failed. No more hooks will be called for this plugin.")
                    _definitions["failed"] = True
                else:
                    print(self.log_prefix + "Ignores error, this plugin will continue to attempt initialization.")

            _broker_definition["hooks_instance"] = _module


        # Add definitions
        self.definitions.add_cumulatively(_definitions["namespaces"])

        return _definitions

    def refresh_plugins(self, _plugin_dir):
        # If < 30 seconds since last refresh (or some other principle)
        _curr_time = time.time()
        if self.last_refresh_time - _curr_time > 30:
            return

        # Reset unresolved schemas
        self._unresolved_schemas = {}

        # Find plugins directory

        if not os.path.exists(_plugin_dir):
            raise Exception("Plugin initialisation failed, no plugin directory where expected(" + _plugin_dir + ")")

        # Loop plugins
        _dir_list = os.listdir(_plugin_dir)
        self.plugins = {}
        for _curr_file in _dir_list:
            if os.path.isdir(os.path.join(_plugin_dir, _curr_file)):
                self.plugins[_curr_file] = self.load_plugin(os.path.join(_plugin_dir, _curr_file))
                print("Loaded plugin " + _curr_file)


        # Add same resolver for all the rest of the namespaces (these resolvers will persist throughout the system)
        self.schema_tools.resolver.handlers.update(
            {_curr_namespace: self.uri_handler for _curr_namespace in self._unresolved_schemas.keys()})

        # Resolve all schemas
        for _curr_namespace_key, _curr_namespace in self._unresolved_schemas.items():
            for _curr_schema_key, _curr_schema in _curr_namespace.items():
                self.definitions[_curr_namespace_key]["schemas"][
                    _curr_schema_key] = self.schema_tools.resolveSchema(
                    _curr_schema)
            print("Schemas in " + _curr_namespace_key + " loaded and resolved:  " +
                  str.join(", ",
                           ["\"" + _curr_schema["title"] + "\"" for _curr_schema in
                            self.definitions[_curr_namespace_key]["schemas"].values()]))


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
        # has_right(object_id_right_admin_everything, kwargs["user"])
        for _curr_plugin_key, _curr_plugin_info in self.plugins.items():
            if "admin-ui" in _curr_plugin_info:
                _curr_client = _curr_plugin_info["admin-ui"]
                # Mount the static libraries
                _web_config.update({
                    _curr_client["mountpoint"]: {
                        "tools.staticdir.on": True,
                        "tools.staticdir.dir": os.path.join(_curr_plugin_info["baseDirectoryName"], "web",
                                                            "client"),
                        "tools.trailing_slash.on": True
                    }
                })
                if _curr_client["mountpoint"][0] == "/":
                    _systemjs += "System.config({\"packages\": {\"" + _curr_client["mountpoint"][1:] + "\": {\"defaultExtension\": \"ts\"}}});\n"
                else:
                    _systemjs += "System.config({\"packages\": {\"" + _curr_client["mountpoint"] + "\": {\"defaultExtension\": \"ts\"}}});\n"

                if "controllers" in _curr_client:
                    for _curr_controller in _curr_client["controllers"]:
                        _imports += "import {" + _curr_controller["name"] + "} from \"" + _curr_controller[
                            "module"] + "\"\n";
                        _controllers += '    app.controller("' + _curr_controller["name"] + '", ' + make_deps(
                            _curr_controller) + ");\n"
                if "directives" in _curr_client:
                    for _curr_directive in _curr_client["directives"]:
                        _imports += "import {" + _curr_directive["name"] + "} from \"" + _curr_directive[
                            "module"] + "\"\n";
                        _directives += '    app.directive("' + _curr_directive["name"] + '", ' + _curr_directive[
                            "name"] + ");\n"
                if "routes" in _curr_client:
                    for _curr_route in _curr_client["routes"]:
                        _routes += "    .when(\"" + _curr_route["path"] + "\", " + json.dumps(
                            _curr_route["route"]) + ")\n"


                if "admin_menus" in _curr_client:
                    _admin_menus += _curr_client["menus"]

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

        Handle all namespace references for unresolved schemas

        :param uri: The uri to handle
        :return: The schema
        """
        _scheme = urlparse(uri).scheme
        _netloc = urlparse(uri).netloc

        if _scheme in self.definitions and _netloc in self.definitions[_scheme]:
            return self.definitions[_scheme][_netloc]
        else:
            return self._unresolved_schemas[_scheme][_netloc]
