"""
Contains functionality for reading settings from ini-files

:copyright: Copyright 2010-2014 by Nicklas Boerjesson
:license: BSD, see LICENSE for details.
"""

import configparser


class INISettings(object):
    """This class is responsible for reading settings from ini-files and holding them in memory."""

    parser = None
    filename = None

    def reload(self, _filename):
        """Reload all information"""
        self.parser.read(_filename)
        self.filename = _filename

    def get(self, _section, _option, _default=None):
        """Get a certain option"""
        if self.parser.has_section(_section):
            if not self.parser.has_option(_section, _option):
                return _default
            else:
                return self.parser.get(_section, _option)
        else:
            return _default

    def __init__(self, _filename = None):
        """Constructor"""
        self.parser = configparser.ConfigParser()
        if _filename:
            self.filename = _filename
            # TODO: Add better config support.
            self.reload(_filename)
