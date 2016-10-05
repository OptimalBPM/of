
import pip
import importlib

def install_packages(_package_names):
    """
    Install the packages listed if not present
    :param _package_names: A list of the packages
    :return:
    """
    _installed = []

    for _curr_package in _package_names:
        if importlib.util.find_spec(_curr_package) is None:
            print(_curr_package + " not installed, installing...")
            pip.main(['install', _curr_package])
            print(_curr_package + " installed...")
            _installed.append(_curr_package)
        else:
            print(_curr_package + " already installed, skipping...")

    return _installed

def uninstall_packages(_package_names):
    """
    Install the packages listed if not present
    :param _package_names: A list of the packages
    :return:
    """
    _removed = []


    for _curr_package in _package_names:
        if importlib.util.find_spec(_curr_package) is not None:
            print(_curr_package + " installed, uninstalling...")
            pip.main(['uninstall', _curr_package, '--yes'])
            print(_curr_package + " uninstalled...")
            _removed.append(_curr_package)
        else:
            print(_curr_package + " not installed, skipping...")

    return _removed

