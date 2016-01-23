"""
Contains functionality for reading settings from ini-files

:copyright: Copyright 2010-2014 by Nicklas Boerjesson
:license: BSD, see LICENSE for details.
"""

import configparser
import os


class INISettings(object):
    """This class is responsible for reading settings from ini-files and holding them in memory."""

    parser = None
    filename = None
    dirname = None
    def reload(self, _filename):
        """Reload all information"""
        self.parser.read(_filename)
        self.filename = _filename
        self.dirname = os.path.dirname(_filename)

    def handle_path(self, _path):
        if os.path.isabs(_path):
            return _path
        elif _path[0] == "~":
            return os.path.expanduser(_path)
        else:
            return os.path.join(self.dirname, _path)

    def get(self, _section, _option, _default=None):
        """Get a certain option"""
        if self.parser.has_section(_section):
            if not self.parser.has_option(_section, _option):
                return _default
            else:
                return self.parser.get(_section, _option)
        else:
            return _default


    def get_path(self, _section, _option, _default=None):
        return self.handle_path(self.get(_section, _option, _default))

    def __init__(self, _filename = None):
        """Constructor"""
        self.parser = configparser.ConfigParser()
        if _filename:
            self.filename = _filename
            # TODO: Add better config support.
            self.reload(_filename)
