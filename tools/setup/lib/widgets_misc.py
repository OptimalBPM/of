"""
Created on Oct 30, 2013

@author: Nicklas Boerjesson
"""
from tkinter import Frame, SUNKEN, StringVar, IntVar, ttk, YView, XView, Scrollbar, Canvas, \
    Variable, Text, Button
from tkinter.constants import E, W, LEFT, RIGHT, CENTER, TOP, BOTTOM, X, VERTICAL, FALSE, Y, BOTH, TRUE, NW, END


def make_entry(_master, _caption, _row, _split_sticky=None, _button_caption= None):
    """
    Creates a label, a property variable and text edit box(Entry) and sets stickiness.
    :param _master: The master widget
    :param _caption: The caption for the label
    :param _row: On what row it should be
    :param _split_sticky: Stick together or be apart.
    :return: Returns _variable (the property variable), _entry (the edit box) and _label (the label),
    """
    _label = ttk.Label(_master, text=_caption)
    _label.grid(column=0, row=_row, sticky=W)
    _variable = StringVar()
    _entry = ttk.Entry(_master, textvariable=_variable)
    if _split_sticky:
        _entry.grid(column=1, row=_row, sticky=E)
    else:
        _entry.grid(column=1, row=_row, sticky=W)
    if _button_caption is None:
        return _variable, _entry, _label
    else:
        _button = Button(_master, text=_button_caption)
        _button.grid(column=2, row=_row, sticky=W)
        return _variable, _entry, _label, _button


class Status_Bar(Frame):
    """
    The status bar visualizes progress and status.
    """
    task = None

    def __init__(self, _master):
        super(Status_Bar, self).__init__(_master, bd=1, relief=SUNKEN)

        self.task = StringVar()
        self.progress = IntVar()
        self.init_widgets()

    def update_task(self, _task, _progress):
        """ This function is used as an endpoint for for the
        bubbling notify_task call of the BPMFrame class.
        :param _task: Text that defines the task
        :param _progress: Text that describes the degree of progress
        """
        if _progress < 0:
            self.pb_progress.mode = 'indeterminate'
        else:
            self.pb_progress.mode = 'determinate'

        self.task.set(_task)
        self.progress.set(_progress)
        self.update_idletasks()

    def init_widgets(self):
        """
        Initialize visual elements.
        """

        self.l_task = ttk.Label(self, textvariable=self.task, width=70)
        self.l_task.pack(side=LEFT, fill=X)

        self.pb_progress = ttk.Progressbar(self, variable=self.progress, length=150)
        self.pb_progress.pack(side=RIGHT)


class Selector(Frame):
    """The Selector class implements a selector, label and variable(to hold the data)
    """
    caption = None
    """The caption of the selector"""
    caption_orientation = None
    """The orientation of the selector, can be "LEFT", "RIGHT", "TOP", "BOTTOM"."""
    value = None
    """The current value of the selector"""
    values = None
    """The selectable values"""

    onchange = None
    """The onchange-event is triggered when the value is changed."""
    do_not_propagate = False
    """If True, the onchange event isn't triggered on changing the value."""


    def __init__(self, _master, _values=None, _caption=None, _caption_orientation=None, _relief=None, _onchange=None):
        super(Selector, self).__init__(_master, bd=1, relief=_relief)

        self.value = StringVar()

        if _values:
            self.values = _values
        else:
            self.values = None

        if _caption:
            self.caption = _caption
        else:
            self.caption = None

        if _caption_orientation:
            self.caption_orientation = _caption_orientation
        else:
            self.caption_orientation = LEFT

        if _onchange:
            self.onchange = _onchange
            # Add handling when type is changed

        else:
            self.onchange = None

        do_not_propagate = False

        self.init_widgets()


    def set_but_do_not_propagate(self, _value):
        """Sets the value, but by setting the do_not_propagate-flag, the onchange event will not fire.
        :param _value: The new value
        """
        self.do_not_propagate = True
        self.value.set(_value)


    def _do_onchange(self, *args):
        """
        Calls onchange if assigned.
        :param args: a list of arguments.
        """
        if self.do_not_propagate == False and self.onchange:
            self.onchange(_current_index=0, _current_value=self.cb.get())
        else:
            self.do_not_propagate = False


    def init_widgets(self):
        """
        Initialize visual elements.
        """

        self.value = StringVar()
        self.cb = ttk.Combobox(self, textvariable=self.value, state='readonly')
        self.cb['values'] = self.values
        self.cb.current(0)

        self.l_caption = ttk.Label(self, text=self.caption)

        _cb_o = None
        if self.caption_orientation == LEFT:
            _cb_o = RIGHT
        elif self.caption_orientation == RIGHT:
            _cb_o = LEFT
        elif self.caption_orientation == TOP:
            _cb_o = BOTTOM
        elif self.caption_orientation == BOTTOM:
            _cb_o = TOP

        self.cb.pack(side=_cb_o)
        self.l_caption.pack(side=self.caption_orientation)

        self.value.trace('w', self._do_onchange)


class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        self._canvas = canvas
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
            if interior.winfo_reqheight() != canvas.winfo_height():
                # update the canvas's height to fit the inner frame
                canvas.config(height=interior.winfo_reqheight())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            """
            This function is called when the canvas is configured, that is on resize and so on,
            """
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
            if interior.winfo_reqheight() != canvas.winfo_height():
                # update the inner frame's height to fill the canvas
                canvas.itemconfigure(interior_id, height=canvas.winfo_height())

        canvas.bind('<Configure>', _configure_canvas)

        return


class BaseFrame(Frame, YView, XView):
    """
    This class introduces all properties that a frame in should hold.
    """

    def notify_task(self, _task, _progress):
        """
        This function checks if the master widget has a notify_task function, and if so, calls it.
        This way, notifications travel upwards in the widget structure until someone has a notify_task that's different.
        See the main_tk_replicator.ReplicatorMain for an example,

        :param _task: Text that defines the task
        :param _progress: Text that describes the degree of progress
        """
        if self.master:
            if hasattr(self.master, "notify_task"):
                self.master.notify_task(_task, _progress)
            else:
                print(
                    self.__class__.__name__ + ": Internal deficiency, " + self.master.__class__.__name__ + " should have a notify_task function\nTask:\n" + _task + "\n" + str(
                        _progress))
        else:
            print("Task:\n" + _task + "\n" + str(_progress))


    def notify_messagebox(self, _title, _message, _kind=None):
        """
        This function checks if the master widget has a notify_messagebox function, and if so, calls it.
        This way, messagebox calls travel upwards in the widget structure until someone has a notify_messagebox that's
        different.
        See the main_tk_replicator.ReplicatorMain for an example,

         :param _title: The title of the message box.
         :param _message: The message to be shown in the text area.
         :param _kind: Can be "message", "warning" or None.
        """

        if self.master:
            if hasattr(self.master, "notify_messagebox"):
                self.master.notify_messagebox(_title, _message, _kind=None)
            else:
                print(
                    self.__class__.__name__ + ":Internal deficiency, " + self.master.__class__.__name__ + " should have a notify_messagebox function.\nTitle:" + _title + "\n" + _message)
        else:
            print("Title:" + _title + "\n" + _message)





class TextExtension(Frame):
    """Extends Frame.  Intended as a container for a Text field.  Better related data handling
    and has Y scrollbar."""


    def __init__(self, master, textvariable=None, *args, **kwargs):

        super(TextExtension, self).__init__(master)
        # Init GUI

        self._y_scrollbar = Scrollbar(self, orient=VERTICAL)

        self._text_widget = Text(self, yscrollcommand=self._y_scrollbar.set, *args, **kwargs)
        self._text_widget.pack(side=LEFT, fill=BOTH, expand=1)


        self._y_scrollbar.config(command=self._text_widget.yview)
        self._y_scrollbar.pack(side=RIGHT, fill=Y)

        if textvariable is not None:
            if not (isinstance(textvariable, Variable)):
                raise TypeError("tkinter.Variable type expected, " + str(type(textvariable)) + " given.".format(type(textvariable)))
            self._text_variable = textvariable
            self.var_modified()
            self._text_trace = self._text_widget.bind('<<Modified>>', self.text_modified)
            self._var_trace = textvariable.trace("w", self.var_modified)

    def text_modified(self, *args):
            if self._text_variable is not None:
                self._text_variable.trace_vdelete("w", self._var_trace)
                self._text_variable.set(self._text_widget.get(1.0, END))
                self._var_trace = self._text_variable.trace("w", self.var_modified)
                self._text_widget.edit_modified(False)

    def var_modified(self, *args):
        self.set_text(self._text_variable.get())
        self._text_widget.edit_modified(False)

    def unhook(self):
        if self._text_variable is not None:
            self._text_variable.trace_vdelete("w", self._var_trace)


    def clear(self):
        self._text_widget.delete(1.0, END)

    def set_text(self, _value):
        self.clear()
        if (_value is not None):
            self._text_widget.insert(END, _value)
