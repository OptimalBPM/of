"""
The setup module handles all Setup related tasks:

Install/remove plugins and their dependencies
Update OF and its dependencies using pip
Manage folder location
Manage startup scripts
Be scriptable
Create a settings file format
Manage databases
Handle certificate (for now, or should they be in the db?)
Update Plugins using git


Deps: dulwich

"""
import os
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import json
from distlib.compat import ZipFile
from dulwich import porcelain

from of.common.dictionaries import set_property_if_in_dict
from of.common.internal import not_implemented
from of.common.settings import JSONXPath

default_config_repo = "https://github.com/OptimalBPM/of-config.git"

class Setup():

    """Location of the setup configuration file"""
    setup_location = None

    """Location of the setup configuration file"""
    install_location = None
    """The location or the plugins, if not set plugins are installed into the config_location/plugins-folder"""
    plugins_location = None

    """The URL of the config repository"""
    install_repository_url = None

    """An dict of the plugins"""
    plugins = None

    def __init__(self, _setup_definition=None, _filename=None, *args, **kw):
        if _setup_definition is not None:
            self.read_settings(_setup_definition)

    def load_install(self, _install_folder):

        _exp_path = os.path.expanduser(_install_folder)
        _plugins_folder = None

        # Does the config file exist?
        if os.path.exists(os.path.join(_exp_path, "config.json")):
            _config = JSONXPath(os.path.join(_exp_path, "config.json"))
            _plugins_folder = _config.get_path("broker/pluginsFolder", _default="plugins")

        if _plugins_folder is None:
            # If there is no config file, try with the default location for the plugins folder
            _plugins_folder = os.path.join(_exp_path, "plugins")

        self.plugins = []

        # Enumerate plugins
        if not os.path.exists(_plugins_folder):
            # TODO: Write warning to status
            pass
        else:
            # Loading
            _plugin_names = os.listdir(_plugins_folder)

            for _plugin_name in _plugin_names:
                # Only look att non-hidden and non system directories
                if os.path.isdir(os.path.join(_plugins_folder, _plugin_name)) and _plugin_name[0:2] != "__" and \
                    _plugin_name[0] != ".":
                    _definitions = JSONXPath(os.path.join(_plugins_folder, "definitions.json"))
                    _description = _definitions.get("plugins/" + _plugin_name + "/description","No description found in plugin definition")
                    self.plugins.append({"name": _plugin_name, "description": _description})


    def install_plugins(self):
        pass

    def read_settings(self, _setup_definition):
        set_property_if_in_dict(self,"install_location", _setup_definition, _convert_underscore=True)
        set_property_if_in_dict(self,"plugins_folder", _setup_definition, _convert_underscore=True)
        set_property_if_in_dict(self, "install_repository_url", _setup_definition,
                                _default_value=default_config_repo, _convert_underscore=True)
        set_property_if_in_dict(self, "plugins", _setup_definition,  _convert_underscore=True)

    @not_implemented
    def write_settings(self):
        pass
    @not_implemented
    def uninstall_config(self):
        pass

    @not_implemented
    def uninstall_plugin(self):
        pass

    def install_config(self):
        # Set folder location at ~/optimalframework if not set
        if self.install_location is None:
            _folder_location = os.path.expanduser("~/optimalframework")
        else:
            _folder_location = os.path.expanduser(self.install_location)
        if not os.path.exists(_folder_location):
            # Clone the config repo
            _repo = porcelain.clone(source= self.install_repository_url, target= _folder_location, checkout=True)
        else:
            raise Exception("Error installing the configuration files at \"" + _folder_location + "\", directory already exists.")

    def install_plugin_binaries(self, _folder):
        try:
            with open(os.path.join(_folder, "definitions.json"), "r") as f:
                _settings = json.load(f)
            try:
                for _curr_plugin_name, _curr_plugin_value in _settings["plugins"].items():
                    if "binaries" in _curr_plugin_value:
                        for _curr_binary in _curr_plugin_value["binaries"]:
                            _source_file = urlopen(_curr_binary["url"])
                            _tempfile = tempfile.TemporaryFile(mode='w+b')
                            sys.stdout.write("Downloading " + _curr_binary["url"] + " (" + str(_source_file.info()['Content-Length']) + " bytes) into temporary area...")
                            sys.stdout.flush()
                            _tempfile.write(_source_file.read())
                            print("..done.")
                            _target_folder = os.path.join(_folder, _curr_binary["target"])
                            sys.stdout.write("Extracting all files into " + _target_folder)
                            sys.stdout.flush()
                            with ZipFile(_tempfile) as _zipfile:
                                _zipfile.extractall(path=_target_folder)
                            _tempfile.close()
                            print("..done.")

            except HTTPError as e:
                print("An error occured when downloading a binary (" + _curr_binary["url"] + "): " + str(e))
            except URLError as e:
                print("An URL-related error occurred when downloading binary (" + _curr_binary["url"] + "): " + str(e))
        except Exception as e:
            print("An error occurred installing binaries in "+ _folder + ":" + str(e))


    def install_plugin(self, _plugins_location, _plugin_name, _plugin_info):
        # TODO: Add branch..
        _curr_target = os.path.join(_plugins_location, _plugin_name)
        porcelain.clone(source=_plugin_info["url"], target=_curr_target, checkout=True)

        self.install_plugin_binaries(_curr_target)

    def install_plugins(self):
        # Set plugin location to config location/plugins if not set
        if self.plugins_location is None:
            _plugins_location = os.path.join(os.path.expanduser(self.install_location), "plugins")
        else:
            _plugins_location = os.path.expanduser(self.plugins_location)
            if os.path.exists(_plugins_location):
                raise Exception(
                    "Error installing the configuration files at \"" + _plugins_location + "\", directory already exists.")
            else:
                os.mkdir(_plugins_location)


        for _plugin_name, _plugin_info in self.plugins.items():
            self.install_plugin(_plugins_location, _plugin_name, _plugin_info)

    def install(self):

        _log = "Installation starting..."
        self.install_config()
        self.install_plugins()

        # TODO: Fix rights for logging if on linux..
        _log += "Installation finished."

        return _log