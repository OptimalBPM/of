"""
Created on Oct 20, 2013

@author: Nicklas Boerjesson
"""
import json
import os
import sys
from _thread import start_new_thread
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from tkinter import Tk, ttk, filedialog, SUNKEN, StringVar, Button, BooleanVar, messagebox, Toplevel, Entry, Text
from tkinter.messagebox import askquestion, askokcancel, OK

from urllib.parse import unquote

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

        if _setup_filename is not None and _setup is not None:
            self.setup_to_gui()

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.resize()

        self.parent.mainloop()

    def resize(self):
        """
        Resize the window, set the width what the internal windows need.
        """
        self._canvas.update_idletasks()
        self.fr_top_right.update_idletasks()
        self._canvas.config(width=self.interior.winfo_reqwidth() + 1, height=self.interior.winfo_reqheight())

    def on_dataset_columns_change(self, *args):
        # Columns have changed; force reload columns from structure
        self.fr_src_dataset.get_possible_references(True)
        self.fr_dest_dataset.get_possible_references(True)
        for curr_mapping in self.g_plugins.items:
            curr_mapping.fr_item.reload_references()


    def notify_task(self, _task, _progress):
        """Override as this is the top widget"""
        self.fr_Status_Bar.update_task(_task, _progress)

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
        if _plugin_folder is not None:
            self.plugins_folder.set(_plugin_folder)

    def on_select_install_folder(self, *args):
        _install_folder = filedialog.askdirectory(title="Choose install folder (usually in the \"~of\"-folder)")
        if _install_folder is not None:
            self.install_location.set(_install_folder)

    def on_select_installation(self, *args):
        _install_folder = filedialog.askdirectory(title="Select existing installation")
        if _install_folder is not None:
            self.install_location.set(_install_folder)
            self.setup.load_install(_install_folder=_install_folder)
            self.setup_to_gui()

    def install_thread_function(self, _name, _whatever):
        self.setup.install()
        self.notify_task('Installed.', 0)

    def on_install(self):
        self.gui_to_setup()
        self.notify_task('Installing..', 0)
        start_new_thread(self.install_thread_function, ("Install_thread", None))


    def on_uninstall(self):
        self.gui_to_setup()
        self.notify_task('Uninstalling..', 0)
        self.setup.install()
        self.notify_task('Uninstalled.', 0)


    def intercept_log(self, s):
        self.ta_log.insert("end", s)
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

        self.g_plugins = FrameList(self.fr_top_left, _detail_key_text="Plugins >>", bd=1, relief=SUNKEN)
        self.g_plugins.pack(side=TOP, fill=X)
        #self.g_plugins.on_delete = self.plugins_do_on_delete
        #self.g_plugins.on_detail = self.plugins_do_on_detail

        self.btn_append_mapping = Button(self.fr_top_left, text="Append mapping", command=self.on_append_mapping)
        self.btn_append_mapping.pack(side=TOP)

        # Plugin details
        self.fr_top_right = BaseFrame(self.fr_top)
        self.fr_top_right.pack(side=RIGHT, fill=Y)

        self.l_plugin = ttk.Label(self.fr_top_right, text="Plugin details")
        self.l_plugin.pack(side=TOP)
        self.fr_plugin = BaseFrame(self.fr_top_right, bd=1, relief=SUNKEN)
        self.fr_plugin.pack(side=TOP, fill=BOTH, expand=1)
        self.plugin_url = make_entry(self.fr_plugin, "Repository URL(http):", 0)



        # Install
        self.fr_install = ttk.Frame(self.fr_top_left)
        self.fr_install.pack(side=TOP, fill=BOTH, expand=1)



        self.fr_install_actions = ttk.Frame(self.fr_install)
        self.fr_install_actions.pack(side=TOP, fill=X)

        self.btn_install = Button(self.fr_install_actions, text="Install", command=self.on_install)
        self.btn_install.pack(side=LEFT)
        self.btn_uninstall = Button(self.fr_install_actions, text="Uninstall", command=self.on_uninstall)
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
        self.fr_bottom.pack(side=BOTTOM, fill=X)

        self.fr_Status_Bar = Status_Bar(self.fr_bottom)
        self.fr_Status_Bar.pack(fill=X)
        self.resize()

    # #########################################################################
    # This section contains functions handling thawe entire setup(load/save/GUI)
    # #########################################################################

    def plugins_to_gui(self):
        # clear plugin list
        self.g_plugins.clear()

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

    def check_prerequisites_for_reload(self):
        """Can a reload be made using the current settings? If not, display cause in status field"""

        if self.fr_src_dataset is None:
            self.notify_task("Cannot reload: Source dataset must be specified.", 0)
            return False
        elif self.fr_dest_dataset is None:
            self.notify_task("Cannot reload: Destination dataset must be specified.", 0)
            return False
        _tmp = self.fr_src_dataset.check_reload()
        if _tmp:
            self.notify_task("Cannot reload source: " + _tmp, 0)
            return False
        _tmp = self.fr_dest_dataset.check_reload()
        if _tmp:
            self.notify_task("Cannot reload destination: " + _tmp, 0)
            return False
        else:
            return True


    def update_data(self, _refresh=None):
        """
        Reload all data into the GUI
        :param _refresh: Force reload of datasets
        :return:
        """

        if self.check_prerequisites_for_reload() is False:
            return

        self.notify_task("", 0)
        if len(self.setup.source.data_table) == 0 or _refresh:
            # Update settings
            self._gui_to_merge()

            # Update XPath references especially, since it addresses an XML structure, not a dataset.
            if isinstance(self.setup.source, XpathDataset):
                self.setup.source.field_xpaths = []
                self.setup.source.field_names = []
                for _curr_mapping_idx in range(0, len(self.g_plugins.items)):
                    self.setup.source.field_xpaths.append(
                        self.g_plugins.items[_curr_mapping_idx].fr_item.src_reference.get())
                    self.setup.source.field_names.append(
                        self.g_plugins.items[_curr_mapping_idx].fr_item.src_reference.get())

            self.setup.source.load()
        # Reset identity values
        self.reset_substitions_identity()
        # Is there any data?
        if len(self.setup.source.data_table) > 0:
            # Try to retain the approximate position in the table.
            if self._row_index < 0:
                self._row_index = 0
            elif self._row_index > len(self.setup.source.data_table) - 1:
                self._row_index = len(self.setup.source.data_table) - 1
            # Loop through mappings, update data and perform transformations
            # TODO: This certainly doesn't seem to belong here, should be extracted
            for _curr_mapping_idx in range(0, len(self.g_plugins.items)):
                _curr_frame = self.g_plugins.items[_curr_mapping_idx].fr_item
                _curr_frame.hide_error()
                _src_ref = _curr_frame.src_reference.get()
                try:
                    if isinstance(self.setup.source, XpathDataset):
                        _col_idx = self.setup.source.field_xpaths.index(_src_ref)
                    else:
                        _col_idx = self.setup.source.field_names.index(_src_ref)
                except ValueError:
                    _col_idx = -1

                if _col_idx > -1:
                    _curr_frame.curr_raw_data = self.setup.source.data_table[self._row_index][_col_idx]
                    try:
                        perform_transformations(_input=_curr_frame.curr_raw_data,
                                                _transformations=_curr_frame.mapping.transformations)
                    except Exception as e:
                        self.notify_task(
                            'Error in one of the transformations, mapping: ' + _src_ref + " error: " + str(e), 0)

                    _curr_frame.curr_data.set(str(_curr_frame.curr_raw_data))

                else:
                    _curr_frame.show_error(_msg="No mapping")
                    _curr_frame.curr_data.set("")

                    try:
                        _curr_frame.curr_raw_data = perform_transformations(_input=None,
                                                                            _transformations=
                                                                            _curr_frame.mapping.transformations)
                    except Exception as e:
                        self.notify_task(
                            'Error in one of the transformations, mapping: ' + _curr_frame.dest_reference.get() +
                            " error: " + str(e), 0)

                    _curr_frame.curr_data.set(str(_curr_frame.curr_raw_data))

                self.g_plugins.items[_curr_mapping_idx].fr_item.reload_references()


    # #########################################################
    # The following events deals with navigating the active dataset
    ##########################################################


    def on_refresh_plugins(self):
        """Triggered when the "Reload data"-button is pressed."""
        self.refresh_plugins()



    def dataset_frame_factory(self, _dataset=None, _dataset_type=None, _is_destination=False):
        """
        This is a factory function for creating matching frames(visual property editors) for the dataset classes.
        :param _dataset: The dataset, if existing.
        :param _dataset_type: The dataset type string representation ("RDBMS", and so on)
        """
        if _dataset:
            _dataset_type = self.dataset_instance_to_dataset_type(_dataset)

        if _dataset_type == "RDBMS":
            _tmp = FrameRDBMSDataset(self.fr_settings, _dataset=_dataset, _relief=SUNKEN,
                                     _is_destination=_is_destination)
            _tmp.subnet_ip = self.ip_address
        elif _dataset_type == "FLATFILE":
            _tmp = FrameFlatfileDataset(self.fr_settings, _dataset=_dataset, _relief=SUNKEN,
                                        _is_destination=_is_destination)
        elif _dataset_type == "XPATH":
            _tmp = FrameXPathDataset(self.fr_settings, _dataset=_dataset, _relief=SUNKEN,
                                     _is_destination=_is_destination)
        elif _dataset_type == "SPREADSHEET":
            _tmp = FrameSpreadsheetDataset(self.fr_settings, _dataset=_dataset, _relief=SUNKEN,
                                           _is_destination=_is_destination)
        else:
            raise Exception("Internal error, unsupported dataset type: " + str(_dataset_type))
        if self.setup_filename is not None:
            _tmp.base_path = os.path.dirname(self.setup_filename)
        return _tmp


    def on_src_dataset_type_change(self, _current_value):
        """
        Triggered when a user selects a different dataset type for the source dataset
        :param _current_value: A string describing what dataset type has been selected.
        """
        if self.fr_src_dataset is not None:
            self.fr_src_dataset.destroy()
        self.fr_src_dataset = self.dataset_frame_factory(_dataset_type=_current_value.upper(), _is_destination=False)
        self.setup.source = self.fr_src_dataset.dataset
        self.fr_src_dataset.grid(column=0, row=1)

    def on_dest_dataset_type_change(self, _current_value):
        """
        Triggered when a user selects a different dataset type for the destination dataset
        :param _current_value: A string describing what dataset type has been selected.
        """
        if self.fr_dest_dataset is not None:
            self.fr_dest_dataset.destroy()
        self.fr_dest_dataset = self.dataset_frame_factory(_dataset_type=_current_value.upper(), _is_destination=True)
        self.setup.destination = self.fr_dest_dataset.dataset
        self.fr_dest_dataset.grid(column=1, row=1)

    def get_source_references(self, _force=None):
        """
        Returns the possible field references from the source dataset
        :param _force: If True, forces a reload of the underlying dataset.
        """
        if self.fr_src_dataset is not None:
            try:
                return self.fr_src_dataset.get_possible_references(_force)
            except Exception as e:
                self.notify_messagebox(_title="Failed refreshing source references", _message="Error: " + str(e),
                                       _kind="warning")
                return []


    def get_destination_references(self, _force=None):
        """
        Returns the possible field references from the destination dataset
        :param _force: If True, forces a reload of the underlying dataset.
        """
        if self.fr_dest_dataset is not None:
            try:
                return self.fr_dest_dataset.get_possible_references(_force)
            except Exception as e:
                self.notify_messagebox(_title="Failed refreshing destination references", _message="Error: " + str(e),
                                       _kind="warning")
                return []


    ##########################################################
    # This section contains functions handling field mappings
    ##########################################################
    def mappings_to_gui(self):
        """Populates the GUI from the mappings list of the merge object"""

        self.g_plugins.clear()
        for _curr_mapping in self.setup.mappings:
            _new_item = self.g_plugins.append_item()
            _new_item.make_item(_class=FrameMapping, _mapping=_curr_mapping,
                                _on_get_source_references=self.get_source_references,
                                _on_get_destination_references=self.get_destination_references)


    def gui_to_mappings(self):
        """Gathers data from GUI into the mappings list of the merge object"""

        self.gui_to_transformations()
        for _curr_mapping in self.g_plugins.items:
            _curr_mapping.fr_item.gui_to_mapping()

        self.setup._mappings_to_fields(self.setup.source, _use_dest=False)
        self.setup._mappings_to_fields(self.setup.destination, _use_dest=True)


    def mappings_do_on_delete(self, _g_plugins, _item_frame):
        """Triggered if the "del"-button has been clicked"""
        self.setup.mappings.remove(_item_frame.fr_item.mapping)

    def mappings_do_on_move_up(self, _g_plugins, _item_frame):
        """Triggered if the up arrow-button has been clicked"""
        _curr_idx = self.setup.mappings.index(_item_frame.fr_item.mapping)
        self.setup.mappings.insert(_curr_idx - 1, self.setup.mappings.pop(_curr_idx))

    def mappings_do_on_move_down(self, _g_plugins, _item_frame):
        """Triggered if the down arrow-button has been clicked"""
        _curr_idx = self.setup.mappings.index(_item_frame.fr_item.mapping)
        self.setup.mappings.insert(_curr_idx + 1, self.setup.mappings.pop(_curr_idx))

    def on_append_mapping(self, *args):
        """Triggered if the "Append mapping"-button has been clicked."""
        _new_mapping = Mapping()
        self.setup.mappings.append(_new_mapping)
        _new_item = self.g_plugins.append_item()
        _new_item.make_item(_class=FrameMapping, _mapping=_new_mapping,
                            _on_get_source_references=self.get_source_references,
                            _on_get_destination_references=self.get_destination_references)


    def mappings_do_on_detail(self, _g_plugins, _item_frame):
        self.notify_task("", 0)
        if self.curr_mapping_frame:
            self.gui_to_transformations()
        self.g_transformations.clear()
        for _curr_transformation in _item_frame.fr_item.mapping.transformations:

            _frame_class = self._transformation_frame_class_lookup(_curr_transformation)
            if _frame_class:
                _new_item = self.g_transformations.append_item()
                _new_item.make_item(_class=_frame_class, _transformation=_curr_transformation)
        _item_frame['background'] = "dark grey"

        try:
            if _item_frame.fr_item.curr_raw_data is not None:
                perform_transformations(_input=_item_frame.fr_item.curr_raw_data,
                                        _transformations=_item_frame.fr_item.mapping.transformations)
        except Exception as e:
            self.notify_task(
                'Error in one of the transformations, mapping: ' + _item_frame.fr_item.mapping.src_reference + " error: " + str(
                    e), 0)

        if self.curr_mapping_frame:
            try:
                self.curr_mapping_frame['background'] = self['background']
            except Exception as e:
                raise Exception("Error setting background to: " + self['background'] + ":" + str(e))
        self.curr_mapping_frame = _item_frame

    ##########################################################
    # This section contains functions handling transformations
    ##########################################################
    def gui_to_transformations(self):
        """Gathers data from GUI into the transformation objects"""

        for _curr_transformation in self.g_transformations.items:
            _curr_transformation.fr_item.gui_to_transformation()


    def _transformation_frame_class_lookup(self, _transformation=None, _type=None):
        if _type is None:
            _type, _desc = transformation_to_type(_transformation)

        if _type == "Cast":
            return FrameTransformationCast
        if _type == "Trim":
            return FrameTransformationTrim
        if _type == "If empty":
            return FrameTransformationIfEmpty
        if _type == "Replace":
            return FrameTransformationReplace
        if _type == "Replace regex":
            return FrameTransformationReplaceRegex
        else:
            return None
            #raise Exception("Internal error, unsupported transformation type: " + str(_transformation_type))

    def transformations_do_on_delete(self, _g_transformations, _item_frame):
        self.curr_mapping_frame.fr_item.mapping.transformations.remove(_item_frame.fr_item.transformation)

    def transformations_do_on_move_up(self, _g_transformations, _item_frame):
        _curr_transformations = self.curr_mapping_frame.fr_item.mapping.transformations
        _curr_idx = _curr_transformations.index(_item_frame.fr_item.transformation)
        _curr_transformations.insert(_curr_idx - 1,
                                     _curr_transformations.pop(
                                         _curr_idx))

    def transformations_do_on_move_down(self, _g_transformations, _item_frame):
        _curr_transformations = self.curr_mapping_frame.fr_item.mapping.transformations
        _curr_idx = _curr_transformations.index(_item_frame.fr_item.transformation)
        _curr_transformations.insert(_curr_idx + 1,
                                     _curr_transformations.pop(
                                         _curr_idx))

    def on_append_transformation(self, *args):
        if self.curr_mapping_frame is not None:
            _new_transformation = type_to_transformation(self.sel_transformation_append_type.get())(
                _substitution=self.curr_mapping_frame.fr_item.mapping.substitution)
            self.curr_mapping_frame.fr_item.mapping.transformations.append(_new_transformation)
            _frame_class = self._transformation_frame_class_lookup(_new_transformation)
            if _frame_class:
                _new_item = self.g_transformations.append_item()
                _new_item.make_item(_class=_frame_class, _transformation=_new_transformation)

    def clear_transformation_events(self):
        for _curr_mapping in self.setup.mappings:
            for _curr_transformation in _curr_mapping.transformations:
                _curr_transformation.on_done = None

    ############################################################
    # This section contains functions handling the merge preview
    ############################################################

    def clear_preview(self):
        for _curr_item in self.gr_preview.get_children():
            self.gr_preview.delete(_curr_item)

    def reset_substitions_identity(self):
        """Reset substitions"""

        for _curr_mapping in self.setup.mappings:
            _curr_mapping.substitution.set_identity(0)

    def on_preview_merge(self, *args):
        self.do_merge(_commit=False)

    def on_commit_merge(self, *args):
        if askokcancel(title="Warning: committing merge", message="This will commit actual changes to the destination, "
                                                                  "do you want to proceed?") is True:
            self.do_merge(_commit=True)

    def do_merge(self, _commit=False):
        self._gui_to_merge()
        self.update_data(_refresh=True)
        self.setup.destination_log_level = DATASET_LOGLEVEL_DETAIL
        # Clear GUI events
        self.clear_transformation_events()
        self.setup.clear_log()
        try:
            _data_table, _log, _deletes, _inserts, _updates = self.setup.execute(_commit=_commit)
        except Exception as e:
            self.notify_messagebox("Error while merging", str(e))
            return

        # Call columns src/dest field names if they differ

        if len(self.setup.key_fields) > 0:
            _key_field = self.setup.key_fields[0]
        else:
            _key_field = 0

        self.clear_preview()

        self.gr_preview["columns"] = ["Change_Data"]
        self.gr_preview.column("Change_Data", width=500)

        self.gr_preview.heading("Change_Data", text="Change/Data")

        # Add a main for each action

        # Add deletes
        self.gr_preview.insert(parent="", index="end", iid="obpm_deletes", text="Deletes")
        if self.setup.delete:
            for _curr_row in _deletes:
                _curr_item_idx = self.gr_preview.insert(parent="obpm_deletes", index="end", iid="",
                                                        text=_curr_row[2][_key_field])
                _curr_value = ",".join([str(_item) for _item in _curr_row[2]])
                self.gr_preview.item(_curr_item_idx, values=[_curr_value])
                for _curr_column_idx in range(len(_curr_row[2])):
                    _curr_change_item_idx = self.gr_preview.insert(parent=_curr_item_idx, index="end", iid="", text=str(
                        self.setup.destination.field_names[_curr_column_idx]))
                    self.gr_preview.item(_curr_change_item_idx, values=[str(_curr_row[2][_curr_column_idx])])
        # Add inserts
        self.gr_preview.insert(parent="", index="end", iid="obpm_inserts", text="Inserts")
        if self.setup.insert:
            for _curr_row in _inserts:
                _curr_item_idx = self.gr_preview.insert(parent="obpm_inserts", index="end", iid="",
                                                        text=_curr_row[2][_key_field])
                _curr_value = ",".join([str(_item) for _item in _curr_row[2]])
                self.gr_preview.item(_curr_item_idx, values=[_curr_value])
                for _curr_column_idx in range(len(_curr_row[2])):
                    _curr_change_item_idx = self.gr_preview.insert(parent=_curr_item_idx, index="end", iid="", text=str(
                        self.setup.destination.field_names[_curr_column_idx]))
                    self.gr_preview.item(_curr_change_item_idx, values=[str(_curr_row[2][_curr_column_idx])])
        # Add updates
        self.gr_preview.insert(parent="", index="end", iid="obpm_updates", text="Updates")
        if self.setup.update:
            for _curr_row in _updates:
                _curr_item_idx = self.gr_preview.insert(parent="obpm_updates", index="end", iid="",
                                                        text=_curr_row[2][_key_field])
                _changes = []
                for _curr_column_idx in range(len(_curr_row[2])):
                    if _curr_row[2][_curr_column_idx] != _curr_row[3][_curr_column_idx]:
                        _curr_change_item_idx = self.gr_preview.insert(parent=_curr_item_idx, index="end", iid="",
                                                                       text=str(self.setup.destination.field_names[
                                                                           _curr_column_idx]))
                        self.gr_preview.item(_curr_change_item_idx, values=[
                            str(_curr_row[3][_curr_column_idx]) + "=>" + str(_curr_row[2][_curr_column_idx])])
                        _changes.append(str(self.setup.destination.field_names[_curr_column_idx]))
                _curr_value = ",".join([str(_item) for _item in _changes])
                self.gr_preview.item(_curr_item_idx, values=[_curr_value])

        # Add log
        self.gr_preview.insert(parent="", index="end", iid="obpm_log", text="Log")
        if _log is not None:
            for _curr_row in _log:
                _log_fields = _curr_row.split(";")
                _curr_item_idx = self.gr_preview.insert(parent="obpm_log", index="end", iid="", text=_log_fields[0])
                _curr_value = ",".join([unquote(str(_item)) for _item in _log_fields[1:]])
                self.gr_preview.item(_curr_item_idx, values=[_curr_value])

        # Add data table

        self.gr_preview.insert(parent="", index="end", iid="obpm_data_table", text="Result")
        if _data_table is not None:
            for _curr_row in _data_table:
                _curr_item_idx = self.gr_preview.insert(parent="obpm_data_table", index="end", iid="",
                                                        text=_curr_row[_key_field])
                _curr_value = ",".join([str(_item) for _item in _curr_row])
                self.gr_preview.item(_curr_item_idx, values=[_curr_value])
                for _curr_column_idx in range(len(_curr_row)):
                    _curr_change_item_idx = self.gr_preview.insert(parent=_curr_item_idx, index="end", iid="", text=str(
                        self.setup.destination.field_names[_curr_column_idx]))
                    self.gr_preview.item(_curr_change_item_idx, values=[str(_curr_row[_curr_column_idx])])
        if _commit == True:
            _simulation_expression = "Merge"
        else:
            _simulation_expression = "Simulated merge"

        if not (self.setup.insert or self.setup.delete or self.setup.update):
            self.notify_task(
                _simulation_expression + " done. (Expecting merge results? Neither insert, delete or update is selected)",
                100)
        else:
            self.notify_task(_simulation_expression + " done.", 100)

    def on_preview_selected(self, *args):
        _selection = self.gr_preview.selection()
        if len(_selection) > 0:
            _item = self.gr_preview.item(_selection[0])
            self.preview_detail.set(str(",".join([str(_item) for _item in _item["values"]])))
