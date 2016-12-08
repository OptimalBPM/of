"""
Created on Oct 20, 2013

@author: Nicklas Boerjesson
"""
import json
import os
import sys
from _thread import start_new_thread

from io import StringIO

from tkinter import Tk, ttk, filedialog, SUNKEN, StringVar, Button, BooleanVar, messagebox, Toplevel, Entry, Text

from tkinter.constants import E, W, N, S, LEFT, X, BOTTOM, TOP, Y, BOTH, RIGHT, END, WORD

from of.tools.setup.lib.frame_list import FrameList
from of.tools.setup.lib.frame_plugin import FramePlugin
from of.tools.setup.lib.widgets_misc import VerticalScrolledFrame, BaseFrame, TextExtension, Selector, Status_Bar, \
    make_entry


class SetupMain(VerticalScrolledFrame):
    """The main class for the GUI of the application"""

    setup = None
    """This is the merge object of the application, it holds all settings for the merge operation"""
    setup_filename = None
    """The name of the file containing the merge definition"""
    fr_src_dataset = None
    """The fram of the source dataset, contains a FrameCustomDataset descendant"""
    fr_dest_dataset = None
    """The fram of the source dataset, contains a FrameCustomDataset descendant"""
    suppress_errors = None
    """Do not show any errors"""
    _row_index = None
    """The current row in the dataset"""
    curr_mapping_frame = None
    """The currently selected mapping frame"""

    def __init__(self, _setup=None, _setup_filename=None, *args, **kw):

        self.parent = Tk()

        # Init oneself

        super(SetupMain, self).__init__(self.parent, bd=1, relief=SUNKEN, *args, **kw)
        self.grid(stick=(E, W, N, S))

        self.suppress_errors = None

        self.setup = _setup
        self.setup_filename = StringVar()
        self.setup_filename.set(_setup_filename)

        self.install_location = None
        self.plugins_folder = None
        self.install_repository_url = None
        self.fr_settings = None

        self.fr_dest_dataset = None

        self.grid()
        self.ip_address = StringVar()
        self._row_index = 0
        self.init_GUI()
        self.notify_task('GUI initiated.', 0)
        if _setup is not None:
            self.notify_task('Loading setup..', 0)
            self.setup_to_gui()
            self.notify_task('Setup loaded.', 100)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.resize()
        self.notify_task('Running. Welcome to the Optimal Framework setup application!', 100)
        self.parent.mainloop()


    def resize(self):
        """
        Resize the window, set the width what the internal windows need.
        """
        self._canvas.update_idletasks()
        self.fr_top_right.update_idletasks()

        self._canvas.config(width=self.interior.winfo_reqwidth() + 1, height=self.interior.winfo_reqheight()+1)

        self.fr_bottom.update_idletasks()

    def on_dataset_columns_change(self, *args):
        # Columns have changed; force reload columns from structure
        self.fr_src_dataset.get_possible_references(True)
        self.fr_dest_dataset.get_possible_references(True)
        for curr_mapping in self.g_plugins.items:
            curr_mapping.fr_item.reload_references()


    def notify_task(self, _task, _progress):
        """Override as this is the top widget"""
        self.fr_status_bar.update_task(_task, _progress)

    def notify_messagebox(self, _title, _message, _kind=None):
        """Override as this is the top class, default is error."""
        if self.suppress_errors is None:
            if _kind == "message":
                messagebox.showinfo(_title, _message)
            elif _kind == "warning":
                messagebox.showwarning(_title, _message)
            else:
                messagebox.showerror(_title, _message)

    def on_post_merge_sql(self, *args):
        # Show post-merge-SQL dialog
        _wdw = Toplevel()
        _wdw.geometry('+400+400')
        _wdw.e = TextExtension(_wdw, textvariable=self.post_execute_sql)
        _wdw.e.pack()
        _wdw.e.focus_set()
        _wdw.transient(self.parent)
        _wdw.grab_set()
        self.parent.wait_window(_wdw)
        _wdw.e.unhook()
        del (_wdw)


    def on_select_plugins_folder(self, *args):
        _plugin_folder = filedialog.askdirectory(title="Choose plugin folder (usually in the ")
        if _plugin_folder is not None or _plugin_folder != "":
            self.plugins_folder.set(_plugin_folder)

    def on_select_install_folder(self, *args):
        _install_folder = filedialog.askdirectory(title="Choose install folder (usually in the \"~of\"-folder)")
        if _install_folder is not None or _install_folder != "":
            self.install_location.set(_install_folder)

    def on_select_installation(self, *args):
        _install_folder = filedialog.askdirectory(title="Select existing installation")
        if _install_folder is not None or _install_folder != "":
            self.install_location.set(_install_folder)
            self.setup.load_install(_install_folder=_install_folder)
            self.setup_to_gui()

    def install_thread_function(self, _name, _whatever):
        self.setup.install()

        self.notify_task('Installed.', 100)

    def on_install(self):
        self.gui_to_setup()
        self.notify_task('Installing..', 0)
        start_new_thread(self.install_thread_function, ("Install_thread", None))


    def on_uninstall(self):
        self.gui_to_setup()
        self.notify_task('Uninstalling..', 0)
        self.setup.uninstall()
        self.notify_task('Uninstalled.', 100)


    def intercept_log(self, s):
        self.ta_log.insert("end", s)
        self.ta_log.see(END)
        self.parent.update_idletasks()

        return None

    def init_GUI(self):
        """Init main application GUI"""
        print("Initializing GUI...redirectind stdout/stderr to log window..", end="")


        self.parent.title("Optimal Framework setup")
        self.interior.notify_task = self.notify_task
        self.interior.notify_messagebox = self.notify_messagebox

        self.fr_top = BaseFrame(self.interior)
        self.fr_top.pack(side=TOP, fill=BOTH, expand=1)

        self.fr_top_left = BaseFrame(self.fr_top)
        self.fr_top_left.pack(side=LEFT, fill=BOTH, expand=1)

        self.fr_rw = BaseFrame(self.fr_top_left)
        self.fr_rw.pack(side=TOP, fill=X)

        self.btn_load_json_json = ttk.Button(self.fr_rw, text="Load", command=self.on_load_json)
        self.btn_load_json_json.pack(side=LEFT)
        self.btn_save_json = ttk.Button(self.fr_rw, text="Save", command=self.on_save_json)
        self.btn_save_json.pack(side=LEFT)
        self.btn_load_folder = ttk.Button(self.fr_rw, text="Existing", command=self.on_select_installation)
        self.btn_load_folder.pack(side=LEFT)
        self.fr_setup_filename = BaseFrame(self.fr_rw)
        self.l_setup_filename = ttk.Label(self.fr_setup_filename, text="Setup file:")
        self.l_setup_filename.pack(side=LEFT)
        self.setup_filename.set("")
        self.e_config_filename = ttk.Entry(self.fr_setup_filename, textvariable=self.setup_filename)
        self.e_config_filename.pack(side=RIGHT)

        self.fr_setup_filename.pack(side=RIGHT)

        # Settings

        self.fr_settings = BaseFrame(self.fr_top_left)
        self.fr_settings.pack(side=TOP, fill=BOTH)
        self.fr_settings.columnconfigure(2, weight=5)
        self.install_location,self.l_install_location, self.e_install_location,\
        self.b_install_location = make_entry(self.fr_settings, "Install location:", 0, _button_caption= "..")
        self.b_install_location.config(command = self.on_select_install_folder)
        self.plugins_folder, self.l_plugin_location, self.e_plugin_location, \
        self.b_plugins_folder = make_entry(self.fr_settings, "Plugins folder:", 1, _button_caption="..")
        self.b_plugins_folder.config(command = self.on_select_plugins_folder)
        self.install_repository_url,self.l_install_repository_url, \
        self.e_install_repository_url = make_entry(self.fr_settings, "Repository URL", 2)


        # Plugins

        self.fr_plugins_header = BaseFrame(self.fr_top_left)
        self.fr_plugins_header.pack(side=TOP)

        self.l_plugins = ttk.Label(self.fr_plugins_header, text="Plugins:")
        self.l_plugins.pack(side=TOP)

        self.fr_plugins_header_nav = BaseFrame(self.fr_plugins_header)
        self.fr_plugins_header_nav.pack(side=BOTTOM)



        self.btn_reload = Button(self.fr_plugins_header_nav, text="Refresh", command=self.on_refresh_plugins)
        self.btn_reload.pack(side=LEFT)

        self.g_plugins = FrameList(self.fr_top_left, _detail_key_text="Details >>", bd=1, relief=SUNKEN)
        self.g_plugins.pack(side=TOP, fill=X)
        #self.g_plugins.on_delete = self.plugins_do_on_delete
        #self.g_plugins.on_detail = self.plugins_do_on_detail


        # Plugin details
        self.fr_top_right = BaseFrame(self.fr_top)
        self.fr_top_right.pack(side=RIGHT, fill=Y)

        self.l_plugin = ttk.Label(self.fr_top_right, text="Plugin details")
        self.l_plugin.pack(side=TOP)
        self.fr_plugin = BaseFrame(self.fr_top_right, bd=1, relief=SUNKEN)
        self.fr_plugin.pack(side=TOP, fill=BOTH, expand=1)
        self.plugin_url,self.l_plugin_url, \
        self.e_plugin_url = make_entry(self.fr_plugin, "Repository URL(http):", 0)



        # Install
        self.fr_install = ttk.Frame(self.fr_top_left)
        self.fr_install.pack(side=TOP, fill=BOTH, expand=1)



        self.fr_install_actions = ttk.Frame(self.fr_install)
        self.fr_install_actions.pack(side=TOP, fill=X)

        self.btn_install = Button(self.fr_install_actions, text="Install", command=self.on_install)
        self.btn_install.pack(side=LEFT)
        self.btn_uninstall = Button(self.fr_install_actions, text="Uninstall (not implemented)", command=self.on_uninstall)
        self.btn_uninstall.pack(side=LEFT)



        # Preview

        self.ta_log = Text(self.fr_install, width = 100, height = 7, wrap = WORD)
        self.ta_log.pack(side=TOP, fill=BOTH, expand=1)

        self.log_out = StringIO()
        sys.stdout = self.log_out
        sys.stderr = self.log_out
        self.log_out._write = self.log_out.write
        self.log_out.write = self.intercept_log


        self.fr_bottom = BaseFrame(self.interior)
        self.fr_bottom.pack(side=BOTTOM, fill=BOTH)
        self.fr_bottom.config(height=30)

        self.fr_status_bar = Status_Bar(self.fr_bottom)
        self.fr_status_bar.pack(fill=BOTH)
        self.fr_status_bar.config(height=30)

        self.resize()

    # #########################################################################
    # This section contains functions handling thawe entire setup(load/save/GUI)
    # #########################################################################

    def on_plugin_detail(self, _framelist, _item):
        self.plugin_url.set(_item.fr_item.plugin["url"])

    def plugins_to_gui(self):
        if hasattr(self.setup, "plugins") and self.setup.plugins is not None:
            # clear plugin list
            self.g_plugins.clear()
            self.g_plugins.on_detail = self.on_plugin_detail
            # populate with plugins
            for _curr_plugin_key, _curr_plugin_value in self.setup.plugins.items():
                _new_item = self.g_plugins.append_item()
                _new_item.make_item(_class=FramePlugin, _name = _curr_plugin_key, _plugin=_curr_plugin_value)

    def setup_to_gui(self):
        """
        Populate the GUI from the setup class.
        """

        self.install_location.set(self.setup.install_location)
        self.plugins_folder.set(self.setup.plugins_folder)
        self.install_repository_url.set(self.setup.install_repository_url)
        self.plugins_to_gui()


    def on_save_json(self, *args):
        """Triggered when save-button is clicked.
        Displays a save dialog, fetches GUI data into merge, and saves as JSON into the selected file."""
        self.notify_task('Saving..', 0)
        _filename = filedialog.asksaveasfilename(initialdir=os.path.dirname(self.setup_filename.get()),
                                                 initialfile=os.path.basename(self.setup_filename.get())
                                                 , defaultextension=".json",
                                                 filetypes=[('JSON files', '.json'), ('all files', '.*')],
                                                 title="Choose location")
        if _filename:
            self.gui_to_setup()
            self.notify_task('Saving(Generating JS)..', 0)

            _dict = self.setup.as_dict()
            self.notify_task('Saving(Writing file)..', 50)
            with open (_filename, "w") as _f:
                json.dump(_dict, fp=_f, sort_keys=True, indent=4)

            self.notify_task('Saving..done.', 100)
        else:
            self.notify_task('Saving cancelled.', 0)


    def gui_to_plugin(self):

        self.setup.plugins = {}

        # populate with plugins
        for _curr_plugin in self.g_plugins.items:
            self.setup.plugins[_curr_plugin.fr_item.name] = _curr_plugin.fr_item.gui_to_plugin()

    def gui_to_setup(self):
        """
        Save the the GUI to the setup class.
        """

        self.setup.install_location = self.install_location.get()
        self.setup.plugins_folder = self.plugins_folder.get()
        self.setup.install_repository_url = self.install_repository_url.get()
        self.gui_to_plugin()



    def on_load_json(self, *args):
        """Triggered when load-button is clicked.
        Displays a load dialog, clears the GUI, populates the merge and uppdates the GUI"""
        _setup_filename = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[('JSON files', '.json'), ('all files', '.*')],
                                               title="Choose file")
        if _setup_filename is not None:
            self.notify_task('Loading setup..', 0)
            try:
                self.setup.load_from_file(_setup_filename=_setup_filename)
                self.setup_filename.set(_setup_filename)
            except Exception as e:
                self.notify_messagebox("Error loading data", str(e))
            self.setup_to_gui()

            self.notify_task('Loading setup..done', 100)
            self.resize()




    def on_refresh_plugins(self):
        """Triggered when the "Reload data"-button is pressed."""
        self.refresh_plugins()




