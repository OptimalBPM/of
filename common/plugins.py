"""
This module handles the plugin structure of the  the Optimal BPM Admin API
Created on Jan 22, 2016

@author: Nicklas Boerjesson

"""
import importlib
import json
import os
import time
from uuid import UUID
import sys
from urllib.parse import urlparse

from of.common.cumulative_dict import CumulativeDict
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

    """Reference to the namespaces"""
    namespaces = None
    """The process id (not pid)"""
    process_id = None

    """Do not prefix modules with "plugin." for this plugin.
    This is usually used for testing when the plugin tests are loading the broker."""
    no_package_name_override = None

    def __init__(self, _plugin_dir, _schema_tools, _namespaces, _process_id, _no_package_name_override=None):
        # TODO: Create a dicts schema
        self.schema_tools = _schema_tools
        self.last_refresh_time = -31
        self.namespaces = _namespaces
        self.process_id = _process_id
        self.no_package_name_override = _no_package_name_override

        # Add the parent of plugins to sys path
        sys.path.append(os.path.abspath(os.path.join(_plugin_dir, "..")))
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
                self.write_debug_info("Plugin " + _curr_plugin_name + " marked failed, will not call its hook.")
                continue
            if "hooks_instance" in _curr_plugin:
                _hooks_instance = _curr_plugin["hooks_instance"]
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
        try:
            # A plugin is defince by having a definitions.json-file in its root folder.
            _definitions_filename = os.path.join(_dirname, "definitions.json")
            if not os.path.exists(_definitions_filename):
                raise Exception(
                    "Error loading plugin " + _dirname + ", definition file (" + _definitions_filename + ") missing.")

            with open(_definitions_filename) as _f_def:
                _definitions_data = json.load(_f_def)

            _plugin_data = _definitions_data["plugins"][_plugin_name]
            _plugin_data["baseDirectoryName"] = _dirname
            self.write_debug_info("Loading plugin in " + _plugin_data["description"])

            # Add definitions
            if "namespaces" in _definitions_data:
                for _curr_namespace in _definitions_data["namespaces"]:
                    self.namespaces[_curr_namespace]
                self.namespaces.add_cumulatively(_definitions_data["namespaces"])
                # Add same resolver for the namespaces (these resolvers will persist throughout the system)
                self.schema_tools.resolver.handlers.update(
                    {_curr_namespace: self.uri_handler for _curr_namespace in _definitions_data["namespaces"]})

            self.plugins.add_cumulatively(_definitions_data["plugins"])

            # Load schemas from /schema
            _schema_dir = os.path.join(_dirname, "schemas", "namespaces")
            if os.path.exists(_schema_dir):

                _refs = self.schema_tools.load_schemas_from_directory(_schema_dir, self._unresolved_schemas)
                for _curr_schema_key in _refs:
                    _resolved_schema = self.schema_tools.resolveSchema(self._unresolved_schemas[_curr_schema_key])
                    self.namespaces[urlparse(_curr_schema_key).netloc.split(".")[0]]["schemas"].append(_curr_schema_key)
                    self.schema_tools.json_schema_objects[_curr_schema_key] = _resolved_schema

            else:
                self.write_debug_info("No schema folder, not loading schemas.")
        except Exception as e:
            write_to_log("An error occurred importing " + _plugin_name + ":" + str(e),
                         _category=EC_SERVICE, _severity=SEV_ERROR)
            write_to_log(
                "Setting " + _plugin_name + " as Failed. No dependent plugins will be loaded.",
                _category=EC_SERVICE, _severity=SEV_INFO)
            print("Setting " + _plugin_name + " as Failed. No dependent plugins will be loaded.")
            _plugin_data = {"failed": True, "description": _plugin_name + "(failed)"}
            return _plugin_data

        # Add server side stuff

        if "hooks_module" in _plugin_data:
            _hooks_modulename = _plugin_data["hooks_module"]
            if self.no_package_name_override == _plugin_name:
                # For testing, the plugin is itself loading its code.
                _module_ref = ".".join([_plugin_name, _hooks_modulename])
            else:
                _module_ref = ".".join(["plugins", _plugin_name, _hooks_modulename])

            try:
                _module = importlib.import_module(_module_ref)
                _plugin_data["hooks_instance"] = _module
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

        # Manually add the optimal framework ("of") namespace
        self.namespaces["of"]["schemas"] = [_curr_ref for _curr_ref in self.schema_tools.json_schema_objects.keys()]
        self.schema_tools.resolver.handlers = {"ref": self.uri_handler}

        # Loop plugins
        _plugin_names = os.listdir(_plugins_dir)
        self.plugins = CumulativeDict()
        for _plugin_name in _plugin_names:
            # Only look att non-hidden and non system directories
            if os.path.isdir(os.path.join(_plugins_dir, _plugin_name)) and _plugin_name[0:2] != "__" and _plugin_name[
                0] != ".":
                self.load_plugin(_plugins_dir, _plugin_name)
                self.write_debug_info("Loaded plugin " + _plugin_name)

        self.write_debug_info("Schemas in " + str(", ").join(
            [_curr_plugin["description"] for _curr_plugin in self.plugins.values()]) + " loaded and resolved:  " +
                              str.join(", ",
                                       ["\"" + _curr_schema["title"] + "\"" for _curr_schema in
                                        self._unresolved_schemas.values()]))

        # Remember refresh
        self.last_refresh_time = _curr_time

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
