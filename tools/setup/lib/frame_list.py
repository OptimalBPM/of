"""
Created on Jan 30, 2014

@author: Nicklas Boerjesson
"""
from tkinter.constants import W, RIGHT, Y, E, X, LEFT, BOTH, N
from tkinter import Tk, ttk, SUNKEN, StringVar, Button, Scrollbar, Canvas

from of.tools.setup.lib.widgets_misc import BaseFrame

__author__ = 'nibo'

class FrameListItem(BaseFrame):
    """This class has all the functionality needed to be part of a list of frames."""
    fr_item = None
    """A sub frame containing the content of the frame."""
    fr_control = None
    """A sub frame with navigator buttons and similar."""
    row__base_class = None
    """The class from which to instantiate the item frame. """

    def __init__(self, _master):
        super(FrameListItem, self).__init__(_master, relief=SUNKEN, bd=1)

        self.init_widgets()

    def make_item(self, _class,  **_create_params):
        """
        Instantiates the item frame.
        :param _class: Class reference
        :param _create_params: The params for the creation
        :return:
        """
        self.fr_item = _class(self, **_create_params)
        self.fr_item.pack(fill=BOTH, pady=5)

    def on_delete(self, *args):
        """If delete has been clicked, tell master to delete self."""
        self.master.do_on_delete(self)
    def on_move_up(self, *args):
        """If move up has been clicked, tell master to move self up."""
        self.master.do_on_move_up(self)
    def on_move_down(self, *args):
        """If move down has been clicked, tell master to move self down."""
        self.master.do_on_move_down(self)

    def on_detail(self):
        """If detail button is clicked, tell master to show details."""
        self.master.do_on_detail(self)

    def init_widgets(self,):

        self.fr_control = BaseFrame(self)
        self.fr_control.pack(side=RIGHT)

        self.btn_delete = Button(self.fr_control, text="del", command=self.on_delete, height = 1)
        self.btn_delete.grid(column=1, row=0, sticky=(N,W))
        self.btn_move_up = Button(self.fr_control, text="△", command=self.on_move_up)
        self.btn_move_up.grid(column=2, row=0, sticky=N)
        self.btn_move_down = Button(self.fr_control, text="▽", command=self.on_move_down)
        self.btn_move_down.grid(column=3, row=0, sticky=N)
        if self.master.detail_key_text:
            self.btn_detail_key = Button(self.fr_control, text=self.master.detail_key_text, command=self.on_detail)
            self.btn_detail_key.grid(column=4, row=0, sticky=N)



class FrameList(Canvas):
    """The FrameList manages a list of FrameListItems.
    """
    items = []
    """List of items"""
    scrollbar = None
    """The scrollbar of the list """
    on_insert = None
    """Event fired before an item is inserted"""
    on_delete = None
    """Event fired before an item is deleted"""
    on_append = None
    """Event fired before an item is appended"""
    on_move_up = None
    """Event fired before an item is moved up"""
    on_move_down = None
    """Event fired before an item is moved down"""

    detail_key_text = None
    """The caption of the detail button"""
    on_detail = None
    """Event fired when the detail button is clicked"""

    def __init__(self, _master, _detail_key_text = None, **kwargs):
        super(FrameList, self).__init__(_master, **kwargs)

        self.scrollbar = None

        self.on_delete = None
        self.on_move_up = None
        self.on_move_down = None
        self.on_detail = None
        self.detail_key_text = _detail_key_text

        self.items = []

    def clear(self):
        """Remove all items from the list"""
        for _curr in self.items:
            _curr.destroy()

        self.items.clear()


    def append_item(self):
        """Append a new item to the list"""
        _new = FrameListItem(self)
        if self.on_append:
            self.on_append(self, _new)
        self.items.append(_new)
        _new.pack(fill=X)
        return _new


    def do_on_delete(self, _item_frame):
        """
        Delete the item from the list.
        :param _item_frame: Item to delete

        """

        if self.on_delete:
            self.on_delete(self, _item_frame)

        self.items.remove(_item_frame)
        _item_frame.destroy()

    def repack_list(self):
        """Repack the list"""
        for _curr_item in self.items:
            _curr_item.pack_forget()

        for _curr_item in self.items:
            _curr_item.pack(fill=X)

    def do_on_move_up(self, _item_frame):
        """
        Move _item_frame one step up in the list
        :param _item_frame: The frame to move
        """

        _curr_idx = self.items.index(_item_frame)
        if _curr_idx > 0:
            if self.on_move_up:
                self.on_move_up(self, _item_frame)

            self.items.insert(_curr_idx-1, self.items.pop(_curr_idx))

            self.repack_list()

    def do_on_move_down(self, _item_frame):
        """
        Move _item_frame one step down in the list
        :param _item_frame: The frame to move
        """
        _curr_idx = self.items.index(_item_frame)
        if _curr_idx < len(self.items)-1:
            if self.on_move_down:
                self.on_move_down(self, _item_frame)

            self.items.insert(_curr_idx+1, self.items.pop(_curr_idx))

            self.repack_list()

    def do_on_detail(self, _item_frame):
        """
        Detail button is clicked in _item_frame, trigger event
        :param _item_frame: The frame to show details for
        """
        if self.on_detail:
            self.on_detail(self, _item_frame)

class FrameCustomItem(BaseFrame):
    """
    This class adds an error display label to the BPM frame, used by item frames in the frame list.
    """

    def __init__(self, _master):
        super(FrameCustomItem, self).__init__(_master)

        self._l_err = None

    def show_error(self, _msg = None):
        """
        Show an error label
        :param _msg: The error message
        """

        if self._l_err is None:
            self._l_err = ttk.Label(self, foreground='red', text = _msg)
            self._l_err.pack()
        else:
            self._l_err.text = _msg


    def hide_error(self):
        """Hide the error label"""
        if self._l_err:
            self._l_err.destroy()
            self._l_err = None