"""
Created on Feb 5, 2014

@author: Nicklas Boerjesson
"""
from tkinter import IntVar, StringVar, ttk, BooleanVar
from tkinter.constants import LEFT, X, RIGHT
from of.tools.setup.lib.frame_list import FrameCustomItem

__author__ = 'nibo'


def empty_when_none(_string=None):
    """If _string if None, return an empty string, otherwise return string.
    """
    if _string is None:
        return ""
    else:
        return str(_string)

class FramePlugin(FrameCustomItem):
    """Holds and visualizes a Map between two columns of different datasets"""
    row_index = None

    description = None
    plugins = None

    def __init__(self, _master, _plugin = None):
        super(FramePlugin, self).__init__(_master)


        # Add monitored variables.

        # Description
        self.description = StringVar()


        self.init_widgets()

        self.plugin = _plugin



        if _plugin is not None:
            self.plugin_to_gui()


    def plugin_to_gui(self):

        self.description.set(str(empty_when_none(self.plugin["description"])))

    def gui_to_plugin(self):

        self.plugin.description = self.plugin.description.get()


    def init_widgets(self):

        """Init all widgets"""

        # Source reference
        self.l_description = ttk.Label(self, textvariable=self.description)
        self.l_description.pack(side=LEFT)
        self.l_description["background"] = "#000000"







