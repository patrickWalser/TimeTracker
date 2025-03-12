from my_accordion import Accordion
import tkinter as tk
from tkinter import messagebox, ttk, Frame, Menu
from charts import ChartType
import datetime
from date_time_frame import DateTimeFrame


class TimeTrackerGUI:
    '''The GUI which is shown.

    Handles all necessary events.
    '''

    def __init__(self, root, tracker):
        '''constructor of the UI

        initializes the UI, loads stored data, starts new tracker if needed
        '''
        self.root = root
        self.root.title("TimeTracker")
        self.root.geometry('880x600')
        self.tracker = tracker

        self.setup_menu()
        self.setup_views()
       
        # TODO: analyse_btn print chart is this correct or should load_data be called first?

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(0, self.initial_load)

        self.chart = None

    def setup_menu(self):
        '''setup the menu

        creates the file menu for opening, saving, etc.
        '''
        # file menu for opening, saving, etc.
        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=lambda: self.new_study(edit=False))
        filemenu.add_command(label="Open", command=lambda: self.open_study())
        filemenu.add_command(label="Save as", command=lambda: self.save_as())
        filemenu.add_separator()
        filemenu.add_command(label = "Edit Settings", command = lambda: self.edit_settings())
        editmenu = Menu(menu)
        menu.add_cascade(label="Edit", menu=editmenu)
        editmenu.add_command(label="Edit Study", command=lambda: self.new_study(edit=True))
        editmenu.add_command(label="Edit Semesters", command=lambda: self.edit_semesters())

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(
            label="About", command=lambda: messagebox.showinfo("About", "TimeTracker v0.1"))

    def setup_views(self):
        '''setup the views

        creates the UI elements for the tracker and analyse view 
        and the necessary buttons to switch between them
        '''
        # separate window into frames using grid
        header_view = Frame(self.root)
        header_view.grid(row=0, column=0, sticky='news', padx=20, pady=10)

        # two different frames to switch between views
        tracker_view = Frame(self.root)
        tracker_view.grid(row=1, sticky='news', padx=20, pady=5)
        analyse_view = Frame(self.root)
        analyse_view.grid(row=1, sticky='news', padx=20, pady=5)
        tracker_view.tkraise()

        # Buttons to switch between the two views
        self.tracker_btn = tk.Button(
            header_view, text="Tracker",
            command=lambda: tracker_view.tkraise()).grid(row=0, column=0)

        # switch the view, generate/ update UI elements from analyse view
        self.analyse_btn = tk.Button(
            header_view, text="Analyse",
            command=lambda: [analyse_view.tkraise(),
                             self.generate_accordion(analyse_view),
                             self.print_chart(self.tracker._study)]).grid(row=0, column=1)
        
        self.setup_tracker_view(tracker_view)
        self.setup_analyze_view(analyse_view)

    def setup_tracker_view(self, tracker_view):
        '''setup the tracker view

        creates the UI elements for the tracker view

        tracker_view: the frame where the tracker view is placed
        '''
        self.semester_label = tk.Label(
            tracker_view, text="Semester: ").grid(row=0, column=0)
        self.semester_var = tk.StringVar()
        self.semester_var.trace_add(
            'write', lambda a, b, c: self.update_treeview())
        self.semester_combobox = ttk.Combobox(
            tracker_view, textvariable=self.semester_var,
            postcommand=self.update_combo_semesters)
        self.semester_combobox.grid(row=0, column=1)

        self.module_label = tk.Label(
            tracker_view, text="Module: ").grid(row=0, column=2)
        self.module_var = tk.StringVar()
        self.module_var.trace_add(
            'write', lambda a, b, c: self.update_treeview())
        self.module_combobox = ttk.Combobox(
            tracker_view, textvariable=self.module_var,
            postcommand=self.update_combo_modules)
        self.module_combobox.grid(row=0, column=3)

        self.category_label = tk.Label(
            tracker_view, text="Category: ").grid(row=0, column=4)
        self.category_var = tk.StringVar()
        self.category_var.trace_add(
            'write', lambda a, b, c: self.update_treeview())
        self.category_combobox = ttk.Combobox(
            tracker_view, textvariable=self.category_var,
            postcommand=self.update_combo_categories)
        self.category_combobox.grid(row=0, column=5)

        self.comment_label = tk.Label(
            tracker_view, text="comment: ").grid(row=0, column=6)
        self.comment_var = tk.StringVar()
        self.comment_entry = tk.Entry(
            tracker_view, width=20, textvariable=self.comment_var)
        self.comment_entry.grid(row=0, column=7)

        self.is_tracking = False
        self.start_stop_btn = tk.Button(
            tracker_view, text="Start", command=self.btn_start_stop_click)
        self.start_stop_btn.grid(row=1, column=0, padx=0, pady=10)

        finish_btn = tk.Button(
            tracker_view, text='Finish module', command=lambda: self.btn_finish_click())
        finish_btn.grid(row=1, column=1, sticky='news', padx=0, pady=10)

        self.current_duration_label = tk.Label(
            tracker_view, text="")
        self.current_duration_label.grid(
            row=1, column=2, columnspan=3, sticky="W")

        # treeview to show the entries in a table
        self.treeview_frame = Frame(tracker_view)

        self.tree = ttk.Treeview(self.treeview_frame, columns=(
            'Module', 'Category', 'Comment', 'Start', 'Duration'), height=10)
        self.tree.heading('#0', text='Semester')
        self.tree.heading('Module', text='Module')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Comment', text='Comment')
        self.tree.heading('Start', text='Start')
        self.tree.heading('Duration', text='Duration')

        self.tree.column('#0', minwidth=0, width=140, stretch=True)
        self.tree.column('Module', minwidth=0, width=180, stretch=True)
        self.tree.column('Category', minwidth=0, width=120, stretch=True)
        self.tree.column('Comment', minwidth=0, width=120, stretch=True)
        self.tree.column('Start', minwidth=0, width=125, stretch=True)
        self.tree.column('Duration', minwidth=0, width=80, stretch=True)

        self.tree.bind("<Double-Button-1>", self.on_tree_item_click)
        self.tree.pack(side='left')

        self.yscroll = ttk.Scrollbar(self.treeview_frame, orient=tk.VERTICAL,
                                     command=self.tree.yview,)
        self.tree['yscrollcommand'] = self.yscroll.set
        self.yscroll.pack(side='right', fill='y')

        self.treeview_frame.grid(row=2, columnspan=8, sticky='news')
    
    def setup_analyze_view(self, analyze_view):
        '''setup the analyze view

        creates the UI elements for the analyze view

        analyze_view: the frame where the analyze view is placed
        '''
        self.accordion = None
        self.accordion_frame = analyze_view
        self.chart_frame = tk.Frame(analyze_view)
        self.chart_frame.grid(row=0, column=1, sticky='news')
        self.active_chart = ChartType.BURNDOWN
        chart_frame_header = tk.Frame(self.chart_frame)
        chart_frame_header.grid(row=0, sticky='nw')
        self.btn_burndown = tk.Button(chart_frame_header, text="Burndown-Chart",
                                 command=lambda: (self.set_active_chart(ChartType.BURNDOWN), self.format_buttons(ChartType.BURNDOWN)))
        self.btn_burndown.grid(row=0, column=0, sticky='nw')
        self.btn_pie = tk.Button(chart_frame_header, text="Pie-Chart",
                            command=lambda: (self.set_active_chart(ChartType.PIE), self.format_buttons(ChartType.PIE)))
        self.btn_pie.grid(row=0, column=1, sticky='nw')

        self.plot_frame = tk.Frame(self.chart_frame)
        self.plot_frame.grid(row=1, sticky='news')

    def setup_observers(self):
        '''register observers'''
        
        self.tracker.on_status_change = self.update_tracking_label
        self.tracker.on_treeview_update = self.update_treeview

    def initial_load(self):
        '''load the initial data

        load data and update gui elements
        '''
        self.load_data()
        self.update_treeview()
        self.setup_observers()
        self.generate_accordion(self.accordion_frame)
        self.format_buttons(self.active_chart)
        self.chart_scope = self.tracker._study

    def load_last_tracking(self):
        '''load the last tracking

        loads the last tracking from the tracker and updates the UI elements
        '''
        semName, modName, cat, comment = self.tracker.get_last_tracking_information()
        self.semester_var.set(semName)
        self.module_var.set(modName)
        self.category_var.set(cat)
        self.comment_var.set(comment)

# Commands for the filemenu
    def new_study(self, edit):
        '''opens a window to create a new tracker
        
        edit: if the existing tracker should be edited
        '''
        # set name, planned end, num ECTS, hoursPerEcts
        # TODO: save the old tracker?
        new_window = tk.Toplevel(self.root)
        new_window.title("New Study" if edit == False else "Edit Study")
        # force window to be in foreground
        new_window.grab_set()
        new_window.transient(self.root)

        tk.Label(new_window, text="Total Amount of ECTS").grid(row=0, column=0)
        self.ECTS_var = tk.StringVar()
        ECTS_entry = tk.Entry(new_window, textvariable=self.ECTS_var).grid(row=0, column=1)

        tk.Label(new_window, text="Hours per ECTS").grid(row=1, column=0)
        self.hoursPerECTS_var = tk.StringVar()
        hoursPerECTS_entry = tk.Entry(new_window, textvariable=self.hoursPerECTS_var).grid(row=1, column=1)

        self.plannedEnd = DateTimeFrame(new_window, "Planned end")
        self.plannedEnd.grid(row=2, column=0)

        if edit:
            ects,hours,plannedEnd = self.tracker.get_study_parameters()
            self.ECTS_var.set(ects)
            self.hoursPerECTS_var.set(hours)
            self.plannedEnd.set_datetime(plannedEnd)
            save_cmd = self.save_study
        else:
            save_cmd = self.save_new_study

        self.btn_new_tracker_save = tk.Button(
            new_window, text='save', command=lambda window=new_window: save_cmd(window)).grid(row=3, column=0)

        # set position of the window
        center_x, center_y = self.get_center_position(new_window)
        new_window.geometry(f"+{center_x}+{center_y}")

        self.root.after(800, lambda plannedEnd = self.plannedEnd: plannedEnd.initialize_date_entry())


# TODO: call save_as after creating the tracker?
    def save_new_study(self, window):
        '''create the study and save it
        
        destroys the window
        
        window: the window which is displayed
        '''
        self.chart_scope = self.tracker.create_new_study(
            int(self.ECTS_var.get()), 
            int(self.hoursPerECTS_var.get()), 
            self.plannedEnd.get_datetime()
        )
        window.destroy()

        self.save_as()
    
    def save_study(self, window):
        '''save an edited study
        
        destroys the window

        window: the window which is displayed
        '''
        self.tracker.update_study(
            int(self.ECTS_var.get()),
            int(self.hoursPerECTS_var.get()),
            self.plannedEnd.get_datetime()
        )

        # self.chart_scope = self.tracker._study
        window.destroy()

    def open_study(self):
        '''open a previously saved study from the filesystem'''
        data = [('json', '*.json')]
        filename = tk.filedialog.askopenfilename(
            filetypes=data, defaultextension=data)
        self.load_data(filename)

    def save_as(self):
        '''save the current study to the filesystem'''
        data = [('json', '*.json')]
        filename = tk.filedialog.asksaveasfilename(
            filetypes=data, defaultextension=data)
        self.save_data(filename)

    def edit_settings(self):
        '''edit the settings'''

        new_window = tk.Toplevel(self.root)
        new_window.title("Settings")
        # force window to be in foreground
        new_window.grab_set()
        new_window.transient(self.root)

        tk.Label(new_window, text="Default ECTS:").grid(row=0, column=0, sticky='w')
        self.ects_var = tk.StringVar()
        self.ects_entry = tk.Entry(new_window, textvariable=self.ects_var)
        self.ects_entry.grid(row=0, column=1, sticky='w')
        self.ects_var.set(self.tracker.settings.get("module_ECTS"))

        tk.Label(new_window, text="Default Duration (weeks):").grid(row=1, column=0, sticky='w')
        self.duration_var = tk.StringVar()
        self.duration_entry = tk.Entry(new_window, textvariable=self.duration_var)
        self.duration_entry.grid(row=1, column=1, sticky='w')
        self.duration_var.set(self.tracker.settings.get("module_duration"))

        tk.Button(new_window, text="Save", command=self.save_settings).grid(row=2, column=0, columnspan=2)

        # set position of the window
        center_x, center_y = self.get_center_position(new_window)
        new_window.geometry(f"+{center_x}+{center_y}")

    def save_settings(self):
        ects = int(self.ects_var.get())
        duration = int(self.duration_var.get())
        self.tracker.settings.set("module_ECTS", ects)
        self.tracker.settings.set("module_duration", duration)

    def edit_semesters(self):
        '''edit the semesters
        
        callback for the editmenu to set the number of ECTS and the planned end
        of the semesters.
        '''

        new_window = tk.Toplevel(self.root)
        new_window.title("Edit Semesters")
        # force window to be in foreground
        new_window.grab_set()
        new_window.transient(self.root)

        # create Treeview
        self.edit_semester_tree = ttk.Treeview(new_window, columns=("Semester", "ECTS", "plannedEnd"), show="headings")
        self.edit_semester_tree.heading("Semester", text="Semester")
        self.edit_semester_tree.heading("ECTS", text="ECTS")
        self.edit_semester_tree.heading("plannedEnd", text="plannedEnd")

        # insert data
        for sem in self.tracker.get_semesters():
            try:
                if sem.plannedEnd is None:
                    sem.plannedEnd = datetime.datetime.now()
            except:
                sem.plannedEnd = datetime.datetime.now()

            sem_serial = self.tracker.get_object_id(sem)

            date = sem.plannedEnd.strftime('%Y-%m-%d')
            self.edit_semester_tree.insert("", "end", values=(sem.name, sem.ECTS, date), tags=sem_serial)

        self.edit_semester_tree.pack(fill=tk.BOTH, expand=True)

        # bind doubleClick on cell
        self.edit_semester_tree.bind("<Double-1>", lambda event, window = new_window : self.edit_semester_on_double_click(event, window))

        # set position of the window
        center_x, center_y = self.get_center_position(new_window)
        new_window.geometry(f"+{center_x}+{center_y}")

    def edit_semester_on_double_click(self, event, parent):
        '''edit the semester on double click
        
        places an entry over the double clicked cell to edit the value
        saves on return, focus out or window close

        event: the event which was triggered
        parent: the parent window
        '''
        # identify cell under doubleclick
        itemID = self.edit_semester_tree.identify_row(event.y)
        column = self.edit_semester_tree.identify_column(event.x)

        item = self.edit_semester_tree.item(itemID)

        # lay a tk.Entry over the double clicked cell
        if item and column:
            # get column index
            col_index = int(column.replace("#", "")) - 1

            # get current value
            old_value = item["values"][col_index]

            # get position for the entry
            x, y, width, height = self.edit_semester_tree.bbox(itemID, column)

            # create entry
            self.double_click_entry = tk.Entry(parent)
            self.double_click_entry.place(x=x, y=y, width=width, height=height)
            self.double_click_entry.insert(0, old_value)
            self.double_click_entry.focus()

            # events to finish editing
            self.double_click_entry.bind("<Return>", lambda event: self.edit_semester_save(item, itemID, col_index, parent))
            self.double_click_entry.bind("<FocusOut>", lambda event: self.edit_semester_save(item, itemID, col_index, parent))
            parent.protocol("WM_DELETE_WINDOW", lambda : self.edit_semester_save(item, itemID, col_index, parent))

    def edit_semester_save(self, item, itemID, col_index, parent):
        '''save the edited semester

        validates the input and updates the treeview

        item: the item which was edited
        itemID: the id of the item
        col_index: the index of the column which was edited
        parent: the parent window
        '''

        new_value = self.double_click_entry.get()

        # update values in treeview
        values = list(item["values"])

        if self.validate_value_change(item, col_index, new_value):
            values[col_index] = new_value

        self.edit_semester_tree.item(itemID, values=values)

        self.double_click_entry.destroy()

        # reset callback to default
        parent.protocol("WM_DELETE_WINDOW", parent.destroy)

    def validate_value_change(self, item, col_index, new_value):
        '''validate the value change
        
        validates the new value and updates the semester
        
        item: the item which was edited
        col_index: the index of the column which was edited
        new_value: the new value
        
        returns True if the value is valid
        '''
        # deserialize the object
        tags = item['tags']
        sem = self.tracker.get_object_by_id(tags[0])

        header = self.edit_semester_tree.heading(col_index)['text']
        validFormat = False
        try:
            self.tracker.update_semester(sem, header, new_value)
            validFormat = True
        except ValueError as e:
            messagebox.showerror("Error", f"Error while updating the value: {e}")
        return validFormat

    def btn_start_stop_click(self):
        ''' start or stop the tracking

        Label and button text are updated
        '''

        started = self.tracker.toggle_tracking(self.semester_var.get(), self.module_var.get(),
                self.category_var.get(), self.comment_var.get())
        
        # update button text and label visibility
        if started:
            self.start_stop_btn.config(text="Stop")
            self.current_duration_label.config(bg="lightgreen")
        else:
            self.start_stop_btn.config(text="Start")
            bgColor = self.root.cget("background")
            self.current_duration_label.configure(background=bgColor)
            self.current_duration_label.configure(text="")

    def btn_finish_click(self):
        ''' finishes the module'''
        self.tracker.finish_module(self.semester_var.get(), self.module_var.get())

    def update_tracking_label(self, elapsed):
        '''update the current duration label'''
        if elapsed:
            self.current_duration_label.configure(text="Tracking for "+str(elapsed).split('.')[0])

    def update_combo_semesters(self):
        '''updates the values of the semester combobox'''
        self.semester_combobox['values'] = self.tracker.get_semester_names()

    def update_combo_modules(self):
        '''
        updates the values of the modules combobox depending on the semesters combobox
        '''
        sem_name = self.semester_var.get()
        self.module_combobox['values'] = self.tracker.get_module_names(
            semName=sem_name)

    def update_combo_categories(self):
        '''
        updates the values ot the categories combobox depending on the semester and module comboboxes
        '''
        sem_name = self.semester_var.get()
        mod_name = self.module_var.get()
        self.category_combobox['values'] = self.tracker.get_category_names(
            semName=sem_name, modName=mod_name)
   
    def update_treeview(self):
        '''updates the treeview

        deletes all existing items and generates new items depending on the
        selected  semester, module and category.

        Serializes the data for the click event
        '''

        semName = self.semester_var.get()
        modName = self.module_var.get()
        catName = self.category_var.get()

        treeview_data = self.tracker.get_filtered_data_list(semName,modName,catName)

        # clean all existing entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in treeview_data:
            semester = item['semester']
            module = item['module']
            entry = item['entry']
            tags = (self.tracker.get_object_id(semester), 
                    self.tracker.get_object_id(module), 
                    self.tracker.get_object_id(entry))
            start_time = entry.start_time.strftime(
                "%Y-%m-%d %H:%M:%S")
            duration = str(entry.get_duration()).split('.')[
                0]  # remove micros
            self.tree.insert("", "end", text=semester.name,
                             values=(module.name, entry.category,
                                     entry.comment, start_time,
                                     duration), tags=tags)

    def on_tree_item_click(self, event):
        '''click event of the treeview

        deserializes the data and opens a new window to edit or remove the clicked entry or create a new entry
        '''
        # deserialize the data
        selected = self.tree.focus()
        item = self.tree.item(selected)
        tags = item['tags']
        sem = self.tracker.get_object_by_id(tags[0])
        mod = self.tracker.get_object_by_id(tags[1], sem)
        entry = self.tracker.get_object_by_id(tags[2], mod)

        self.open_edit_entry_dialog(sem, mod, entry)
        

    def open_edit_entry_dialog(self, sem, mod, entry):
        '''open a dialog to edit the entry
        
        sem: the semester of the entry
        mod: the module of the entry
        entry: the entry to edit
        '''

        # new window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit entry")

        self.sem_var = tk.StringVar()
        sem_entry = tk.Entry(edit_window, textvariable=self.sem_var)
        sem_entry.grid(row=0, column=0)
        self.sem_var.set(sem.name)

        self.mod_var = tk.StringVar()
        mod_entry = tk.Entry(edit_window, textvariable=self.mod_var)
        mod_entry.grid(row=0, column=1)
        self.mod_var.set(mod.name)

        self.cat_var = tk.StringVar()
        cat_entry = tk.Entry(edit_window, textvariable=self.cat_var)
        cat_entry.grid(row=0, column=2)
        self.cat_var.set(entry.category)

        self.comment_var = tk.StringVar()
        comment_entry = tk.Entry(edit_window, textvariable=self.comment_var)
        comment_entry.grid(row=0, column=3)
        self.comment_var.set(entry.comment)

        self.start_time = DateTimeFrame(edit_window, label="start time:")
        self.start_time.grid(row=1, columnspan=4, sticky='w')
        self.start_time.set_datetime(entry.start_time)

        self.stop_time = DateTimeFrame(edit_window, label="stop time:")
        self.stop_time.grid(row=2, columnspan=4, sticky='w')
        self.stop_time.set_datetime(entry.stop_time)

        self.module_start = DateTimeFrame(edit_window, label="Module start:")
        self.module_start.grid(row=3, columnspan=4, sticky='w')
        self.module_start.set_datetime(mod.start)
        
        if mod.stop != None:
            self.module_end = DateTimeFrame(edit_window, label="Module end:")
            self.module_end.grid(row=4, columnspan=4, sticky='w')
            self.module_end.set_datetime(mod.stop)

        ects_label = tk.Label(edit_window, text="ECTS:")
        ects_label.grid(row=5, column=0)
        self.module_ects = tk.StringVar()
        ects_entry = tk.Entry(edit_window, textvariable = self.module_ects)
        ects_entry.grid(row=5, column=1)
        self.module_ects.set(mod.ECTS)

        duration_label = tk.Label(edit_window, text="Duration:")
        duration_label.grid(row=6, column=0)
        self.module_duration = tk.StringVar()
        duration_entry = tk.Entry(edit_window, textvariable = self.module_duration)
        duration_entry.grid(row=6, column=1)
        self.module_duration.set((mod.plannedEnd - mod.start).days // 7)

        add_btn = tk.Button(edit_window, text="Save as new entry",
                            command=lambda: 
                            self.tracker.add_new_entry(
                                self.sem_var.get(), self.mod_var.get(), 
                                self.cat_var.get(), self.comment_var.get(), 
                                self.start_time.get_datetime(), self.stop_time.get_datetime()))
        add_btn.grid(row=7, column=0, sticky='news')
        edit_btn = tk.Button(edit_window, text='Save entry',
                             command=lambda s=sem, m=mod, e=entry: 
                             self.tracker.edit_entry(
                                 s, m, e, self.sem_var.get(), 
                                self.mod_var.get(), self.cat_var.get(), 
                                self.comment_var.get(), self.start_time.get_datetime(), 
                                self.stop_time.get_datetime(), self.module_start.get_datetime(), 
                                self.module_end.get_datetime() if mod.stop != None else None, self.module_ects.get(), self.module_duration.get()))
        edit_btn.grid(row=7, column=1, sticky='news')
        remove_btn = tk.Button(edit_window, text='Delete entry',
                               command=lambda s=sem, m=mod, e=entry: 
                               self.tracker.remove_entry(s, m, e))
        remove_btn.grid(row=7, column=2, sticky='news')

        # set potition of the window
        center_x, center_y = self.get_center_position(edit_window)
        edit_window.geometry(f"+{center_x}+{center_y}")

        edit_window.after(800, lambda end=mod.stop:self.init_edit_entry_data(end))

    def init_edit_entry_data(self, end):
        self.start_time.initialize_date_entry()
        self.stop_time.initialize_date_entry()
        self.module_start.initialize_date_entry()
        if end != None:
            self.module_end.initialize_date_entry()

 # TODO: testing
    def generate_accordion(self, parent):
        '''generate an accordion

        generates an accordion depending on the data of the tracker

        parent: the frame where the accordion is placed
        '''
       
        # create a new accordion if none exists
        if self.accordion is None:
            self.accordion = Accordion(parent)
            self.accordion.grid(row=0, column=0, sticky='ns')

        # remove deleted entries
        semesterNames = self.tracker.get_semester_names()
        for sec in self.accordion.sections:
            if sec.name not in semesterNames:
                # delete the section
                self.accordion.remove_section(sec)
                continue

            moduleNames = self.tracker.get_module_names(sec.name)
            for element in sec.sub_elements:
                if element.name not in moduleNames:
                    # delete the entry
                    sec.remove_element(element)
                    continue

        # add new entries
        for sem in self.tracker.get_semesters():
            foundSem = False
            for sec in self.accordion.sections:
                if sem.name == sec.name:
                    # found the semester, check for the modules and continue with next semester
                    foundSem = True
                    for mod in self.tracker.get_modules(sem.name):
                        foundMod = False
                        for element in sec.sub_elements:
                            if mod.name == element.name:
                                # found the module continue with next module
                                foundMod = True
                                break
                        if not foundMod:
                            sec.add_element(
                                mod.name, lambda mod=mod: self.print_chart(mod))
                    break
            if not foundSem:
                section = self.accordion.add_section(
                    sem.name, lambda sem=sem: self.print_chart(sem))
                for mod in self.tracker.get_modules(sem.name):
                    # add all modules because whole section was added
                    section.add_element(
                        mod.name, lambda mod=mod: self.print_chart(mod))
        self.accordion.reorder()

    def format_buttons(self, chart_type):
        '''formats the buttons based on the active chart type'''
        if chart_type == ChartType.BURNDOWN:
            self.btn_burndown.config(relief=tk.SUNKEN, bg="lightblue")
            self.btn_pie.config(relief=tk.RAISED, bg="SystemButtonFace")
        elif chart_type == ChartType.PIE:
            self.btn_pie.config(relief=tk.SUNKEN, bg="lightblue")
            self.btn_burndown.config(relief=tk.RAISED, bg="SystemButtonFace")

    def set_active_chart(self, chart_type):
        '''sets the active chart type and prints the chart

        chart_type: the chart type to set
        '''
        self.active_chart = chart_type
        self.print_chart(self.chart_scope)

    def print_chart(self, scope):
        '''prints the chart

        generates the data depending on the scope, creates the chart defined
        by the active chart type and plots it

        scope: the data (study, Semester, Module) which will be printed
        '''
        self.chart_scope = scope
        # prevent memory leak because matplotlib figure remains open
        # TODO: write to Testprotocol
        # TODO: Burndown check for instance of scope
        if self.chart:  
            self.chart.destroy()
            
        # create data depending on the chart type
        try:
            self.chart = self.tracker.generate_chart(scope, self.active_chart)
        except ValueError:
            messagebox.showerror("Error", "Chart could not be generated with the selected data!")
            return
        
        self.chart.plot(self.plot_frame)

    def get_center_position(self, window):
        '''get the center position of the window using the geometry of the root window'''
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        window.update_idletasks()
        window_width = window.winfo_width()
        window_height = window.winfo_height()

        center_x = root_x + (root_width // 2) - (window_width // 2)
        center_y = root_y + (root_height // 2) - (window_height // 2)

        return center_x, center_y
    
    def save_data(self, filename=None):
        '''saves the data

        Saves the study to the specified file.
        If no file is specified the last used file is used
        If a file is specified it is saved as last used file

        filename: the file where to save the timetracker
        '''
        self.tracker.export_to_json(filename)

    def load_data(self, filename=None):
        '''Loads a previous saved study.

        Loads the study specified by filename.
        If no filename is specified the last used file is used.
        If there is no last used file of a previous started session a new tracker
        is started.

        filename: the Filename
        '''
        try:
            self.tracker.import_from_json(filename)
            self.load_last_tracking()
        except FileNotFoundError as e:
            messagebox.showinfo("Info", "No file found. Starting with new study")
            self.new_study(edit=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error while loading data: {e}")

    def on_close(self):
        '''callback function for application shutdown

        saves the data to the last used filename
        '''
        self.save_data()
        self.root.destroy()
