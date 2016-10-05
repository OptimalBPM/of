"""
Created on Oct 20, 2013

@author: Nicklas Boerjesson
"""
import json
import os

from tkinter import Tk, ttk, filedialog, SUNKEN, StringVar, Button, BooleanVar, messagebox, Toplevel, Entry, Text
from tkinter.messagebox import askquestion, askokcancel, OK

from urllib.parse import unquote

from tkinter.constants import E, W, N, S, LEFT, X, BOTTOM, TOP, Y, BOTH, RIGHT, END





class SetupMain(VerticalScrolledFrame):
    """The main class for the GUI of the application"""

    merge = None
    """This is the merge object of the application, it holds all settings for the merge operation"""
    filename = None
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

    def __init__(self, _merge=None, _filename=None, *args, **kw):

        self.parent = Tk()

        # Init oneself

        super(ReplicatorMain, self).__init__(self.parent, bd=1, relief=SUNKEN, *args, **kw)
        self.grid(stick=(E, W, N, S))

        self.suppress_errors = None

        self.merge = _merge
        self.filename = _filename

        self.fr_src_dataset = None
        self.fr_dest_dataset = None

        self.grid()
        self.ip_address = StringVar()
        self._row_index = 0
        self.init_GUI()

        if _filename is not None and _merge is not None:
            # _merge._load_datasets()
            self._merge_to_gui()


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
        for curr_mapping in self.g_mappings.items:
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


    def on_src_connect(self, *args):
        """Event handler for when the source connection is set"""
        self.fr_mapping.src_dal = self.fr_dataset_src.dal

    def on_dest_connect(self, *args):
        """Event handler for when the destination connection is set"""
        self.fr_mapping.dest_dal = self.fr_dataset_dest.dal

    def init_GUI(self):
        """Init main application GUI"""
        print("Initializing GUI...", end="")

        self.parent.title("Optimal Sync - Move that data - a part of Optimal BPM")
        self.interior.notify_task = self.notify_task
        self.interior.notify_messagebox = self.notify_messagebox

        self.fr_top = BPMFrame(self.interior)
        self.fr_top.pack(side=TOP, fill=BOTH, expand=1)

        self.fr_top_left = BPMFrame(self.fr_top)
        self.fr_top_left.pack(side=LEFT, fill=BOTH, expand=1)

        self.fr_rw = BPMFrame(self.fr_top_left)
        self.fr_rw.pack(side=TOP, fill=X)

        self.btn_Load_json_json = ttk.Button(self.fr_rw, text="Load", command=self.on_load_json)
        self.btn_Load_json_json.pack(side=LEFT)
        self.btn_Save_json = ttk.Button(self.fr_rw, text="Save", command=self.on_save_json)
        self.btn_Save_json.pack(side=LEFT)
        self.fr_subnet_sql = BPMFrame(self.fr_rw)
        self.l_ip = ttk.Label(self.fr_subnet_sql, text="IP(for subnet scan):")
        self.l_ip.pack(side=LEFT)
        self.ip_address.set("192.168.0.1")
        self.e_ip_address = ttk.Entry(self.fr_subnet_sql, textvariable=self.ip_address)
        self.e_ip_address.pack(side=RIGHT)
        self.fr_subnet_sql.pack(side=RIGHT)

        # datasets

        self.fr_datasets = BPMFrame(self.fr_top_left)
        self.fr_datasets.pack(side=TOP)

        self.sel_src_dataset_type = Selector(_master=self.fr_datasets,
                                             _values=('RDBMS', 'XPath', 'Flatfile', 'Spreadsheet'),
                                             _caption="Sources dataset type:",
                                             _onchange=self.on_src_dataset_type_change)
        self.sel_src_dataset_type.grid(column=0, row=0, sticky=W)

        self.sel_dest_dataset_type = Selector(_master=self.fr_datasets,
                                              _values=('RDBMS', 'XPath', 'Flatfile', 'Spreadsheet'),
                                              _caption="Destination dataset type:",
                                              _onchange=self.on_dest_dataset_type_change)
        self.sel_dest_dataset_type.grid(column=1, row=0, sticky=W)


        # Mappings

        self.fr_mapping_header = BPMFrame(self.fr_top_left)
        self.fr_mapping_header.pack(side=TOP)

        self.l_mapping = ttk.Label(self.fr_mapping_header, text="Mappings:")
        self.l_mapping.pack(side=TOP)

        self.fr_mapping_header_nav = BPMFrame(self.fr_mapping_header)
        self.fr_mapping_header_nav.pack(side=BOTTOM)

        self.btn_first = Button(self.fr_mapping_header_nav, text="<<", command=self.on_first)
        self.btn_first.pack(side=LEFT)
        self.btn_prev = Button(self.fr_mapping_header_nav, text="<", command=self.on_prev)
        self.btn_prev.pack(side=LEFT)

        self.btn_reload = Button(self.fr_mapping_header_nav, text="Reload data", command=self.on_reload_data)
        self.btn_reload.pack(side=LEFT)

        self.btn_next = Button(self.fr_mapping_header_nav, text=">", command=self.on_next)
        self.btn_next.pack(side=LEFT)
        self.btn_last = Button(self.fr_mapping_header_nav, text=">>", command=self.on_last)
        self.btn_last.pack(side=LEFT)

        self.g_mappings = FrameList(self.fr_top_left, _detail_key_text="Transformations >>", bd=1, relief=SUNKEN)
        self.g_mappings.pack(side=TOP, fill=X)
        self.g_mappings.on_delete = self.mappings_do_on_delete
        self.g_mappings.on_move_up = self.mappings_do_on_move_up
        self.g_mappings.on_move_down = self.mappings_do_on_move_down
        self.g_mappings.on_detail = self.mappings_do_on_detail

        self.btn_append_mapping = Button(self.fr_top_left, text="Append mapping", command=self.on_append_mapping)
        self.btn_append_mapping.pack(side=TOP)

        # Transformation
        self.fr_top_right = BPMFrame(self.fr_top)
        self.fr_top_right.pack(side=RIGHT, fill=Y)

        self.l_transformations = ttk.Label(self.fr_top_right, text="Transformations")
        self.l_transformations.pack(side=TOP)

        self.g_transformations = FrameList(self.fr_top_right, bd=1, relief=SUNKEN)
        self.g_transformations.pack(fill=BOTH, expand=1)
        self.g_transformations.on_delete = self.transformations_do_on_delete
        self.g_transformations.on_move_up = self.transformations_do_on_move_up
        self.g_transformations.on_move_down = self.transformations_do_on_move_down

        self.fr_append_transformation = ttk.Frame(self.fr_top_right)
        self.fr_append_transformation.pack(side=BOTTOM)

        self.btn_append_transformation = Button(self.fr_append_transformation, text="Append Transformation",
                                                command=self.on_append_transformation)
        self.btn_append_transformation.pack(side=LEFT)

        self.transformation_append_type = StringVar()
        self.sel_transformation_append_type = ttk.Combobox(self.fr_append_transformation,
                                                           textvariable=self.transformation_append_type,
                                                           state='readonly')
        self.sel_transformation_append_type['values'] = ["Replace", "Replace regex", "Cast", "If empty", "Trim"]
        self.sel_transformation_append_type.current(0)
        self.sel_transformation_append_type.pack(side=LEFT, fill=X)

        # Merge preview
        self.fr_Preview = ttk.Frame(self.fr_top_left)
        self.fr_Preview.pack(side=TOP, fill=BOTH, expand=1)

        self.fr_merge_actions = ttk.Frame(self.fr_Preview)
        self.fr_merge_actions.pack(side=TOP, fill=X)

        self.btn_execute_preview = Button(self.fr_merge_actions, text="Preview merge", command=self.on_preview_merge)
        self.btn_execute_preview.pack(side=LEFT)
        self.btn_execute_preview = Button(self.fr_merge_actions, text="Commit merge", command=self.on_commit_merge)
        self.btn_execute_preview.pack(side=LEFT)

        # Update
        self.merge_update = BooleanVar()
        self.e_merge_update = ttk.Checkbutton(self.fr_merge_actions, variable=self.merge_update)
        self.e_merge_update.pack(side=RIGHT)
        self.l_merge_update = ttk.Label(self.fr_merge_actions, text="Update: ")
        self.l_merge_update.pack(side=RIGHT)

        # Insert

        self.merge_insert = BooleanVar()
        self.e_merge_insert = ttk.Checkbutton(self.fr_merge_actions, variable=self.merge_insert)
        self.e_merge_insert.pack(side=RIGHT)
        self.l_merge_insert = ttk.Label(self.fr_merge_actions, text="Insert: ")
        self.l_merge_insert.pack(side=RIGHT)

        # Delete
        self.merge_delete = BooleanVar()
        self.e_merge_delete = ttk.Checkbutton(self.fr_merge_actions, variable=self.merge_delete)
        self.e_merge_delete.pack(side=RIGHT)
        self.l_merge_delete = ttk.Label(self.fr_merge_actions, text="Delete: ")
        self.l_merge_delete.pack(side=RIGHT)

        # Set post-merge SQL
        self.post_execute_sql = StringVar()
        self.btn_Post_Merge_SQL = ttk.Button(self.fr_merge_actions, text="Set post-merge SQL",
                                             command=self.on_post_merge_sql)
        self.btn_Post_Merge_SQL.pack(side=RIGHT, padx=30)

        # Preview
        self.gr_preview = ttk.Treeview(self.fr_Preview, columns=('size', 'modified'))
        self.gr_preview.pack(side=TOP, fill=BOTH, expand=1)
        self.gr_preview.bind("<<TreeviewSelect>>", self.on_preview_selected)
        self.preview_detail = StringVar()
        self.e_previev_detail = ttk.Entry(self.fr_Preview, textvariable=self.preview_detail)
        self.e_previev_detail.pack(side=BOTTOM, fill=X, expand=0)

        self.fr_bottom = BPMFrame(self.interior)
        self.fr_bottom.pack(side=BOTTOM, fill=X)

        self.fr_Status_Bar = Status_Bar(self.fr_bottom)
        self.fr_Status_Bar.pack(fill=X)

        print("done.")

    # #########################################################################
    # This section contains functions handling the entire merge(load/save/GUI)
    # #########################################################################

    def _merge_to_gui(self):
        """
        Populate the GUI from the merge class.
        """
        if self.fr_src_dataset is not None:
            self.fr_src_dataset.destroy()
        _src_type = self.dataset_instance_to_dataset_type(self.merge.source)
        self.sel_src_dataset_type.set_but_do_not_propagate(_src_type)
        self.fr_src_dataset = self.dataset_frame_factory(_dataset=self.merge.source, _is_destination=False)
        self.fr_src_dataset.grid(column=0, row=1)

        if self.fr_dest_dataset is not None:
            self.fr_dest_dataset.destroy()

        _dest_type = self.dataset_instance_to_dataset_type(self.merge.destination)
        self.sel_dest_dataset_type.set_but_do_not_propagate(_dest_type)
        self.fr_dest_dataset = self.dataset_frame_factory(_dataset=self.merge.destination, _is_destination=False)
        self.fr_dest_dataset.grid(column=1, row=1)

        self.mappings_to_gui()

        self.merge_insert.set(bool_to_binary_int(self.merge.insert))
        self.merge_delete.set(bool_to_binary_int(self.merge.delete))
        self.merge_update.set(bool_to_binary_int(self.merge.update))
        if self.merge.post_execute_sql is None:
            self.post_execute_sql.set("")
        else:
            self.post_execute_sql.set(self.merge.post_execute_sql)

        # Hereafter, update column list when they change
        self.fr_src_dataset.on_columns_change = self.on_dataset_columns_change
        self.fr_dest_dataset.on_columns_change = self.on_dataset_columns_change

    def _gui_to_merge(self):
        """Copy the data from the GUI to the merge object"""
        self.fr_src_dataset.write_to_dataset()
        self.merge.source = self.fr_src_dataset.dataset
        self.fr_dest_dataset.write_to_dataset()
        self.merge.destination = self.fr_dest_dataset.dataset

        self.gui_to_mappings()

        self.merge.insert = binary_int_to_bool(self.merge_insert.get())
        self.merge.delete = binary_int_to_bool(self.merge_delete.get())
        self.merge.update = binary_int_to_bool(self.merge_update.get())
        self.merge.post_execute_sql = self.post_execute_sql.get()

    def load_json(self, _filename):
        """Load an JSON into the merge object, and populate the GUI"""
        with open(_filename, "r") as _f:
            _json = json.load(_f)

        self.filename = _filename

        self.notify_task('Loading transformation..', 0)
        self.merge = Merge(_json=_json, _base_path=os.path.dirname(_filename))
        try:
            self.merge._load_datasets()
        except Exception as e:
            self.notify_messagebox("Error loading data", str(e))
            # Supress the following errors. There is no real errors that matters.
            self.suppress_errors = True
        self._merge_to_gui()
        self.suppress_errors = None
        self.notify_task('Loading transformation..done', 100)
        self.resize()


    def on_save_json(self, *args):
        """Triggered when save-button is clicked.
        Displays a save dialog, fetches GUI data into merge, and saves as JSON into the selected file."""
        self.notify_task('Saving..', 0)
        _filename = filedialog.asksaveasfilename(initialfile= self.filename, defaultextension=".json",
                                                 filetypes=[('JSON files', '.json'), ('all files', '.*')],
                                                 title="Choose location")
        if _filename:
            self._gui_to_merge()
            self.notify_task('Saving(Generating JS)..', 0)
            _json = self.merge.as_json()
            self.notify_task('Saving(Writing file)..', 50)
            with open (_filename, "w") as _f:
                json.dump(_json, fp=_f, sort_keys=True, indent=4)

            self.notify_task('Saving..done.', 100)
        else:
            self.notify_task('Saving cancelled.', 0)


    def on_load_json(self, *args):
        """Triggered when load-button is clicked.
        Displays a load dialog, clears the GUI, populates the merge and uppdates the GUI"""
        _filename = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[('JSON files', '.json'), ('all files', '.*')],
                                               title="Choose file")
        if _filename:
            self.g_transformations.clear()
            self.g_mappings.clear()
            self.clear_preview()
            self.curr_mapping_frame = None
            self._row_index = 0
            self.load_json(_filename)

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
        if len(self.merge.source.data_table) == 0 or _refresh:
            # Update settings
            self._gui_to_merge()

            # Update XPath references especially, since it addresses an XML structure, not a dataset.
            if isinstance(self.merge.source, XpathDataset):
                self.merge.source.field_xpaths = []
                self.merge.source.field_names = []
                for _curr_mapping_idx in range(0, len(self.g_mappings.items)):
                    self.merge.source.field_xpaths.append(
                        self.g_mappings.items[_curr_mapping_idx].fr_item.src_reference.get())
                    self.merge.source.field_names.append(
                        self.g_mappings.items[_curr_mapping_idx].fr_item.src_reference.get())

            self.merge.source.load()
        # Reset identity values
        self.reset_substitions_identity()
        # Is there any data?
        if len(self.merge.source.data_table) > 0:
            # Try to retain the approximate position in the table.
            if self._row_index < 0:
                self._row_index = 0
            elif self._row_index > len(self.merge.source.data_table) - 1:
                self._row_index = len(self.merge.source.data_table) - 1
            # Loop through mappings, update data and perform transformations
            # TODO: This certainly doesn't seem to belong here, should be extracted
            for _curr_mapping_idx in range(0, len(self.g_mappings.items)):
                _curr_frame = self.g_mappings.items[_curr_mapping_idx].fr_item
                _curr_frame.hide_error()
                _src_ref = _curr_frame.src_reference.get()
                try:
                    if isinstance(self.merge.source, XpathDataset):
                        _col_idx = self.merge.source.field_xpaths.index(_src_ref)
                    else:
                        _col_idx = self.merge.source.field_names.index(_src_ref)
                except ValueError:
                    _col_idx = -1

                if _col_idx > -1:
                    _curr_frame.curr_raw_data = self.merge.source.data_table[self._row_index][_col_idx]
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

                self.g_mappings.items[_curr_mapping_idx].fr_item.reload_references()


    # #########################################################
    # The following events deals with navigating the active dataset
    ##########################################################
    def on_prev(self):
        """Triggered when the "<"-button is pressed."""
        self._row_index -= 1
        self.update_data()

    def on_next(self):
        """Triggered when the ">"-button is pressed."""
        self._row_index += 1
        self.update_data()

    def on_reload_data(self):
        """Triggered when the "Reload data"-button is pressed."""
        self.update_data(_refresh=True)

    def on_first(self):
        """Triggered when the "<<"-button is pressed."""
        self._row_index = 0
        self.update_data()

    def on_last(self):
        """Triggered when the ">>!-button is pressed."""
        if len(self.merge.source.data_table) == 0:
            self.merge.source.load()
        self._row_index = len(self.merge.source.data_table) - 1
        self.update_data()

    def dataset_instance_to_dataset_type(self, _dataset):
        """
        Identify an instance of a dataset and return a string description.
        Used in the dataset type selector.
        :param _dataset: The dataset to identify
        """
        if isinstance(_dataset, RDBMSDataset):
            return "RDBMS"
        elif isinstance(_dataset, XpathDataset):
            return "XPATH"
        elif isinstance(_dataset, FlatfileDataset):
            return "FLATFILE"
        elif isinstance(_dataset, SpreadsheetDataset):
            return "SPREADSHEET"
        else:
            raise Exception("Internal error, unsupported dataset instance type: " + str(_dataset))

    def dataset_frame_factory(self, _dataset=None, _dataset_type=None, _is_destination=False):
        """
        This is a factory function for creating matching frames(visual property editors) for the dataset classes.
        :param _dataset: The dataset, if existing.
        :param _dataset_type: The dataset type string representation ("RDBMS", and so on)
        """
        if _dataset:
            _dataset_type = self.dataset_instance_to_dataset_type(_dataset)

        if _dataset_type == "RDBMS":
            _tmp = FrameRDBMSDataset(self.fr_datasets, _dataset=_dataset, _relief=SUNKEN,
                                     _is_destination=_is_destination)
            _tmp.subnet_ip = self.ip_address
        elif _dataset_type == "FLATFILE":
            _tmp = FrameFlatfileDataset(self.fr_datasets, _dataset=_dataset, _relief=SUNKEN,
                                        _is_destination=_is_destination)
        elif _dataset_type == "XPATH":
            _tmp = FrameXPathDataset(self.fr_datasets, _dataset=_dataset, _relief=SUNKEN,
                                     _is_destination=_is_destination)
        elif _dataset_type == "SPREADSHEET":
            _tmp = FrameSpreadsheetDataset(self.fr_datasets, _dataset=_dataset, _relief=SUNKEN,
                                           _is_destination=_is_destination)
        else:
            raise Exception("Internal error, unsupported dataset type: " + str(_dataset_type))
        if self.filename is not None:
            _tmp.base_path = os.path.dirname(self.filename)
        return _tmp


    def on_src_dataset_type_change(self, _current_value):
        """
        Triggered when a user selects a different dataset type for the source dataset
        :param _current_value: A string describing what dataset type has been selected.
        """
        if self.fr_src_dataset is not None:
            self.fr_src_dataset.destroy()
        self.fr_src_dataset = self.dataset_frame_factory(_dataset_type=_current_value.upper(), _is_destination=False)
        self.merge.source = self.fr_src_dataset.dataset
        self.fr_src_dataset.grid(column=0, row=1)

    def on_dest_dataset_type_change(self, _current_value):
        """
        Triggered when a user selects a different dataset type for the destination dataset
        :param _current_value: A string describing what dataset type has been selected.
        """
        if self.fr_dest_dataset is not None:
            self.fr_dest_dataset.destroy()
        self.fr_dest_dataset = self.dataset_frame_factory(_dataset_type=_current_value.upper(), _is_destination=True)
        self.merge.destination = self.fr_dest_dataset.dataset
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

        self.g_mappings.clear()
        for _curr_mapping in self.merge.mappings:
            _new_item = self.g_mappings.append_item()
            _new_item.make_item(_class=FrameMapping, _mapping=_curr_mapping,
                                _on_get_source_references=self.get_source_references,
                                _on_get_destination_references=self.get_destination_references)


    def gui_to_mappings(self):
        """Gathers data from GUI into the mappings list of the merge object"""

        self.gui_to_transformations()
        for _curr_mapping in self.g_mappings.items:
            _curr_mapping.fr_item.gui_to_mapping()

        self.merge._mappings_to_fields(self.merge.source, _use_dest=False)
        self.merge._mappings_to_fields(self.merge.destination, _use_dest=True)


    def mappings_do_on_delete(self, _g_mappings, _item_frame):
        """Triggered if the "del"-button has been clicked"""
        self.merge.mappings.remove(_item_frame.fr_item.mapping)

    def mappings_do_on_move_up(self, _g_mappings, _item_frame):
        """Triggered if the up arrow-button has been clicked"""
        _curr_idx = self.merge.mappings.index(_item_frame.fr_item.mapping)
        self.merge.mappings.insert(_curr_idx - 1, self.merge.mappings.pop(_curr_idx))

    def mappings_do_on_move_down(self, _g_mappings, _item_frame):
        """Triggered if the down arrow-button has been clicked"""
        _curr_idx = self.merge.mappings.index(_item_frame.fr_item.mapping)
        self.merge.mappings.insert(_curr_idx + 1, self.merge.mappings.pop(_curr_idx))

    def on_append_mapping(self, *args):
        """Triggered if the "Append mapping"-button has been clicked."""
        _new_mapping = Mapping()
        self.merge.mappings.append(_new_mapping)
        _new_item = self.g_mappings.append_item()
        _new_item.make_item(_class=FrameMapping, _mapping=_new_mapping,
                            _on_get_source_references=self.get_source_references,
                            _on_get_destination_references=self.get_destination_references)


    def mappings_do_on_detail(self, _g_mappings, _item_frame):
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
        for _curr_mapping in self.merge.mappings:
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

        for _curr_mapping in self.merge.mappings:
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
        self.merge.destination_log_level = DATASET_LOGLEVEL_DETAIL
        # Clear GUI events
        self.clear_transformation_events()
        self.merge.clear_log()
        try:
            _data_table, _log, _deletes, _inserts, _updates = self.merge.execute(_commit=_commit)
        except Exception as e:
            self.notify_messagebox("Error while merging", str(e))
            return

        # Call columns src/dest field names if they differ

        if len(self.merge.key_fields) > 0:
            _key_field = self.merge.key_fields[0]
        else:
            _key_field = 0

        self.clear_preview()

        self.gr_preview["columns"] = ["Change_Data"]
        self.gr_preview.column("Change_Data", width=500)

        self.gr_preview.heading("Change_Data", text="Change/Data")

        # Add a main for each action

        # Add deletes
        self.gr_preview.insert(parent="", index="end", iid="obpm_deletes", text="Deletes")
        if self.merge.delete:
            for _curr_row in _deletes:
                _curr_item_idx = self.gr_preview.insert(parent="obpm_deletes", index="end", iid="",
                                                        text=_curr_row[2][_key_field])
                _curr_value = ",".join([str(_item) for _item in _curr_row[2]])
                self.gr_preview.item(_curr_item_idx, values=[_curr_value])
                for _curr_column_idx in range(len(_curr_row[2])):
                    _curr_change_item_idx = self.gr_preview.insert(parent=_curr_item_idx, index="end", iid="", text=str(
                        self.merge.destination.field_names[_curr_column_idx]))
                    self.gr_preview.item(_curr_change_item_idx, values=[str(_curr_row[2][_curr_column_idx])])
        # Add inserts
        self.gr_preview.insert(parent="", index="end", iid="obpm_inserts", text="Inserts")
        if self.merge.insert:
            for _curr_row in _inserts:
                _curr_item_idx = self.gr_preview.insert(parent="obpm_inserts", index="end", iid="",
                                                        text=_curr_row[2][_key_field])
                _curr_value = ",".join([str(_item) for _item in _curr_row[2]])
                self.gr_preview.item(_curr_item_idx, values=[_curr_value])
                for _curr_column_idx in range(len(_curr_row[2])):
                    _curr_change_item_idx = self.gr_preview.insert(parent=_curr_item_idx, index="end", iid="", text=str(
                        self.merge.destination.field_names[_curr_column_idx]))
                    self.gr_preview.item(_curr_change_item_idx, values=[str(_curr_row[2][_curr_column_idx])])
        # Add updates
        self.gr_preview.insert(parent="", index="end", iid="obpm_updates", text="Updates")
        if self.merge.update:
            for _curr_row in _updates:
                _curr_item_idx = self.gr_preview.insert(parent="obpm_updates", index="end", iid="",
                                                        text=_curr_row[2][_key_field])
                _changes = []
                for _curr_column_idx in range(len(_curr_row[2])):
                    if _curr_row[2][_curr_column_idx] != _curr_row[3][_curr_column_idx]:
                        _curr_change_item_idx = self.gr_preview.insert(parent=_curr_item_idx, index="end", iid="",
                                                                       text=str(self.merge.destination.field_names[
                                                                           _curr_column_idx]))
                        self.gr_preview.item(_curr_change_item_idx, values=[
                            str(_curr_row[3][_curr_column_idx]) + "=>" + str(_curr_row[2][_curr_column_idx])])
                        _changes.append(str(self.merge.destination.field_names[_curr_column_idx]))
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
                        self.merge.destination.field_names[_curr_column_idx]))
                    self.gr_preview.item(_curr_change_item_idx, values=[str(_curr_row[_curr_column_idx])])
        if _commit == True:
            _simulation_expression = "Merge"
        else:
            _simulation_expression = "Simulated merge"

        if not (self.merge.insert or self.merge.delete or self.merge.update):
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
