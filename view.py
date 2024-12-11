from my_accordion import Accordion
import tkinter as tk
from tkinter import messagebox, ttk, Frame, Menu
import pickle
import json
import base64
from charts import ChartType, ChartFactory
from model import Study, Semester, Module
from controller import TimeTracker
from tkcalendar import DateEntry
import datetime

class DateTimeFrame(Frame):
    ''' a user control to combine selection of date and time

    extends Frame
    '''

    def __init__(self, parent, label):
        ''' constructor of the user control

        parent: the parent frame in which the DateTimeFrame is added
        label: the label to be displayed next to the controls.
        '''
        super().__init__(parent)

        tk.Label(self, text=label).grid(row=0, column=0, sticky='w')
        tk.Label(self, text="Date:").grid(row=0, column=1, sticky='w')
        self.date = DateEntry(self)
        self.date.grid(row=0, column=2)

        tk.Label(self, text="Time:").grid(row=0, column=3, sticky='w')
        self.hour_entry = ttk.Combobox(
            self, values=[f"{i:02}" for i in range(24)], width=3)
        self.hour_entry.grid(row=0, column=4, sticky='w')

        self.minute_entry = ttk.Combobox(
            self, values=[f"{i:02}" for i in range(60)], width=3)
        self.minute_entry.grid(row=0, column=5, sticky='w')

    def set_datetime(self, datetime):
        ''' set the value of the user control

        datetime: the datetime object to set
        '''
        if (datetime is None):  # leave empty
            return

        self.date.set_date(datetime)
        self.hour_entry.set(datetime.hour)
        self.minute_entry.set(datetime.minute)

    def get_datetime(self):
        ''' get the value of the user control as datetime

        returns datetime
        '''
        date = self.date.get_date()
        h = int(self.hour_entry.get())
        m = int(self.minute_entry.get())
        return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=h, minute=m)


# TODO: add menu to set end, study name?, create new study, save as,...


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
        self.setup_observers()

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
        filemenu.add_command(label="Open", command=lambda: self.open_tracker())
        filemenu.add_command(label="Save as", command=lambda: self.save_as())
        editmenu = Menu(menu)
        menu.add_cascade(label="Edit", menu=editmenu)
        editmenu.add_command(label="Edit Study", command=lambda: self.new_study(edit=True))
        editmenu.add_command(label="Edit Semesters", command=lambda: self.edit_semesters())

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(
            label="About", command=lambda: print("about clicked"))

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
            tracker_view, width=20, textvariable=self.comment_var).grid(row=0, column=7)

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
        self.chart_frame = tk.Frame(analyze_view)
        self.chart_frame.grid(row=0, column=1, sticky='news')
        self.active_chart = ChartType.PIE
        chart_frame_header = tk.Frame(self.chart_frame)
        chart_frame_header.grid(row=0, sticky='nw')
        btn_burndown = tk.Button(chart_frame_header, text="Burndown-Chart",
                                 command=lambda: self.set_active_chart(ChartType.BURNDOWN))
        btn_burndown.grid(row=0, column=0, sticky='nw')
        btn_pie = tk.Button(chart_frame_header, text="Pie-Chart",
                            command=lambda: self.set_active_chart(ChartType.PIE))
        btn_pie.grid(row=0, column=1, sticky='nw')

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
        self.chart_scope = self.tracker._study

# Commands for the filemenu
    def new_study(self, edit):
        '''opens a window to create a new tracker
        
        edit: if the existing tracker should be edited
        '''
        # set name, planned end, num ECTS, hoursPerEcts
        # TODO: save the old tracker?
        new_window = tk.Toplevel(self.root)
        new_window.title("New Study")
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
        # TODO: remove that button
        #self.btn_new_tracker_abort = tk.Button(
         #   new_window, text='abort', command=lambda: print("abort"))

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

    def open_tracker(self):
        '''open a previously saved tracker from the filesystem'''
        data = [('json', '*.json')]
        filename = tk.filedialog.askopenfilename(
            filetypes=data, defaultextension=data)
        self.load_data(filename)

    def save_as(self):
        '''save the current tracker to the filesystem'''
        data = [('json', '*.json')]
        filename = tk.filedialog.asksaveasfilename(
            filetypes=data, defaultextension=data)
        self.save_data(filename)
    def btn_start_stop_click(self):
        ''' start or stop the tracking

        Label and button text are updated
        '''

        self.tracker.toggle_tracking(self.semester_var.get(), self.module_var.get(),
                self.category_var.get(), self.comment_var.get())
        
        # update button text and label visibility
        if self.tracker.current_entry:
            self.start_stop_btn.config(text="Stop")
            self.current_duration_label.config(bg="lightgreen")
        else:
            self.start_stop_btn.config(text="Start")
            bgColor = self.root.cget("background")
            self.current_duration_label.configure(background=bgColor)
        
        self.update_treeview()

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
        selected  semester, module and category

        serializes the data for the click event
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
            tags = (self.tracker.serialize_object(semester), 
                    self.tracker.serialize_object(module), 
                    self.tracker.serialize_object(entry))
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

        calls a new window to editor remove the clicked entry or create a
        new entry
        '''
        # deserialize the data
        selected = self.tree.focus()
        item = self.tree.item(selected)
        tags = item['tags']
        sem = self.tracker.deserialize_object(tags[0])
        mod = self.tracker.deserialize_object(tags[1])
        entry = self.tracker.deserialize_object(tags[2])

        self.open_edit_entry_dialog(sem, mod, entry)
        

    def open_edit_entry_dialog(self, sem, mod, entry):

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

        add_btn = tk.Button(edit_window, text="Save as new entry",
                            command=lambda: 
                            self.tracker.add_new_entry(
                                self.sem_var.get(), self.mod_var.get(), 
                                self.cat_var.get(), self.comment_var.get(), 
                                self.start_time.get_datetime(), self.stop_time.get_datetime()))
        add_btn.grid(row=5, column=0, sticky='news')
        edit_btn = tk.Button(edit_window, text='Save entry',
                             command=lambda s=sem, m=mod, e=entry: 
                             self.tracker.edit_entry(
                                 s, m, e, self.sem_var.get(), 
                                self.mod_var.get(), self.cat_var.get(), 
                                self.comment_var.get(), self.start_time.get_datetime(), 
                                self.stop_time.get_datetime(), self.module_start.get_datetime(), 
                                self.module_end.get_datetime() if mod.stop != None else None))
        edit_btn.grid(row=5, column=1, sticky='news')
        remove_btn = tk.Button(edit_window, text='Delete entry',
                               command=lambda s=sem, m=mod, e=entry: 
                               self.tracker.remove_entry(s, m, e))
        remove_btn.grid(row=5, column=2, sticky='news')

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
        # prevent memory leak because matplotlib figure remains open
        # TODO: write to Testprotocol
        # TODO: Burndown check for instance of scope
        if self.chart:
            self.chart.destroy()

        # create data depending on the chart type
        self.chart = self.tracker.generate_chart(scope, self.active_chart)
        self.chart.plot(self.plot_frame)

    def save_data(self, filename=None):  # TODO: save in correct format
        '''saves the data

        Saves the timetracker to the specified file.
        If no file is specified the last used file is used
        If a file is specified it is saved as last used file

        filename: the file where to save the timetracker
        '''
        self.tracker.export_to_json(filename)

    def load_data(self, filename=None):
        '''Loads a previous saved timetracker.

        Loads the tracker specified by filename.
        If no filename is specified the last used file is used.
        If there is no last used file of a previous started session a new tracker
        is started.

        filename: the Filename
        '''
        try:
            self.tracker.import_from_json(filename)
        except Exception as e:
            messagebox.showerror("Error", f"Error while loading data: {e}")

    def on_close(self):
        '''callback function for application shutdown

        saves the data to the last used filename
        '''
        self.save_data()
        self.root.destroy()
