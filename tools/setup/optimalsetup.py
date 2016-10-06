#!/usr/bin/env python3


"""
    ************
    Optimal Setup
    ************
    
    Optimal setup is an application that provides setup services for the Optimal framework.
    
    :copyright: Copyright 2010-2015 by Nicklas Boerjesson
    :license: BSD, see LICENSE for details.
"""

import sys



# Version and release information used by Sphinx for documentation and setuptools for package generation.


__version__ = '0.9'
__release__ = '0.9.0'
__copyright__ = '2010-2016, Nicklas Boerjesson'

import os
import json
import getopt

major, minor, micro, releaselevel, serial = sys.version_info

def check_prerequisites():



    if major == 2:
        raise Exception("\nERROR RUNNING INSTALLATION:\n"
                        "You are running the setup with Python " + str(major) + "." + str(minor) + "." + str(
            micro) + "!\n"
                     "Please install Python version 3.4 or higher and run with that version instead (python3 optimalsetup.py)")

    if major == 3 and minor < 4:
        _pythonversion = str(major) + "." + str(minor) + "." + str(micro)

        try:
            print("Python " + _pythonversion + " found, so checking if pip is installed..")
            import pip
            print("it was, continuing..")
        except ImportError:
            print("it wasn't, checking if easy_install is installed..")
            try:

                from setuptools.command import easy_install
                if minor == 3:
                    print("it was, installing pip..")
                    easy_install.main(["pip"])
                else:
                    print("it was, installing pip 7.1.2 because 8.x isn't compatible with 3.0-3.2..")
                    easy_install.main(["pip==7.1.2"])
            except ImportError:
                print("it wasn't, halting installation, raising error.")
                raise Exception("Error RUNNING INSTALLATION:\n"
                                "You are running the setup with Python " + _pythonversion + "!\n"
                                                                                            "It doesn't have pip package management installed as default and this installation failed to install it automatically.\n"
                                                                                            "PLease check the pip web site for instructions for your platform:\n"
                                                                                            "https://pip.pypa.io/en/stable/installing/")


def install_package(_package_name, _arguments= None):
    """
    Install the packages listed if not present
    :param _package_name: The package to install
    :param _argument: An optional argument
    :return:
    """
    _installed = []


    import pip

    _exists = None
    if minor < 3:
        import pkgutil
        _exists = pkgutil.find_loader(_package_name)

    elif minor == 3:
        import importlib
        _exists = importlib.find_loader(_package_name)
    else:
        import importlib
        _exists = importlib.util.find_spec(_package_name)

    if _exists is None:
        print(_package_name + " not installed, installing...")
        if _arguments is None:
            pip.main(['install', _package_name])
        else:
            pip.main(['install', _package_name] + _arguments)
        print(_package_name + " installed...")
        return True
    else:
        print(_package_name + " already installed, skipping...")
        return False


sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))




_help_msg = """
Usage: optimal_setup.py [OPTION]... -d [DEFINITION FILE]... -l [LOG LEVEL]
Set up and alter the Optimal Framework

This stand-alone tool facilitates setup

    -d, --definitionfile    Provide the path to an JSON definition file to describe the setup
    -e,                     Initialize editor
    -l, --log_level         Log level
    
    --help     display this help and exit
    --version  output version information and exit

Always back up your data!

"""


def init(_definitionfile):
    """Loads the definition file and extracts settings"""
    pass

def main():
    """Main program function"""
    
    _definitionfile = None
    _edit = None
    _log_level = None
    
    """Parse arguments"""
    try:
        _opts = None
        _args = None
        _opts, _args = getopt.getopt(sys.argv[1:],"ed:l:",["help","version","definitionfile=*.json", "log_level="])
    except getopt.GetoptError as err:
        print (str(err)+ "\n" +_help_msg + "\n Arguments: " + str(_args))
        sys.exit(2)

    if _opts:
        for _opt, _arg in _opts:

            if _opt == '-e':
                # Do not run the Setup, start the application instead
                _edit = True

            elif _opt in ("-d", "--definitionfile"):
                _definitionfile = _arg
            elif _opt in ("-l", "--log_level"):
                _log_level = _arg
            elif _opt == '--help':
                print(_help_msg)
                sys.exit()
            elif _opt == '--version':
                print(__version__)
                sys.exit()

        check_prerequisites()

        """If not installed, install GIT support"""
        install_package("dulwich", ["--global-option=--pure"])

        install_package("of")
        # Dynamically import after GIT support is installed
        from of.tools.setup.lib.setup import Setup


        if _definitionfile:
            """Load merge"""
            print(_definitionfile)


            with open(_definitionfile, "r") as f:
                _setup = Setup(_setup_definition=json.load(f))
        else:
            """Create empty"""

            _setup = Setup()




        if _log_level:
            _setup.log_level = int(_log_level)

        if _edit or not _definitionfile:
            """If the users wants to edit or haven't specified a definition file, start the editor"""
            # Bring up the GUI
            from of.tools.setup.lib.main_tk_setup import SetupMain
            SetupMain(_merge=_setup, _filename=_definitionfile)
        else:
            """Otherwise execute the installation"""
            _log =_setup.install()
            print(str(_log))
    else:
        print("Error: No options provided.\n" + _help_msg)


if __name__ == '__main__':
    main()