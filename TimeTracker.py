from my_accordion import Accordion
import tkinter as tk
from tkinter import messagebox, ttk, Frame, Menu
import datetime
import pickle
import json
import base64
from charts import ChartType, ChartFactory
from tkcalendar import DateEntry
import threading
import uuid


class Entry:
    '''Class Entry holds the information of an entry'''

    def __init__(self, category, comment=""):
        '''creates and starts an entry

        category: category of the entry as string
        comment: optional comment as string
        '''
        self.id = str(uuid.uuid4())
        self.start_time = datetime.datetime.now()
        self.stop_time = None
        self.category = category
        self.comment = comment

    def __eq__(self, other):
        '''can be used to compare Entry objects

        check is done based on the equality of the properties

        other: instance to be checked for equality

        returns: True if equal False if not
                  NotImplemented if other is no Entry
        '''
        if not isinstance(other, Entry):
            return NotImplemented

        return self.id == other.id

    def stop(self):
        '''stops the entry

        return: duration
        '''
        self.stop_time = datetime.datetime.now()
        return self.get_duration()

    def get_duration(self):
        '''get the duration

        return: duration as timedelta'''
        if self.stop_time is None:
            return datetime.datetime.now() - self.start_time
        else:
            return self.stop_time - self.start_time


class Module:
    '''
    Represents a Module with planned duration and amount of ECTS.
    Holds a list of Entries.
    '''

    def __init__(self, name, ECTS=5, duration=6):
        '''creates and starts the module.

        name: name of the module as string
        ECTS: amount of ECTS (credits) default = 5
        duration: planned duration of the module default = 6 weeks
        '''
        self.id = str(uuid.uuid4())
        self.entries = []
        self.name = name
        self.ECTS = ECTS
        self.start_module(duration=duration)

    def __eq__(self, other):
        '''can be used to compare Module objects

        check is done based on the equality of the properties

        other: instance to be checked for equality

        returns: True if equal False if not
                  NotImplemented if other is no Entry
        '''
        if not isinstance(other, Module):
            return NotImplemented

        return self.id == other.id

    def start_module(self, duration):
        '''Starts the module.

        duration: planned duration of the module in weeks
        '''
        self.start = datetime.datetime.now()
        self.plannedEnd = self.start + datetime.timedelta(weeks=duration)
        self.stop = None

    def add_entry(self, category, comment=""):
        '''creates an entry and adds it to the list of entries

        category: category of the entry
        comment: optional comment for the entry

        return: the created entry
        '''
        entry = Entry(category=category, comment=comment)
        self.entries.append(entry)
        return entry

    def remove_entry(self, entry):
        '''removes an entry

        entry: the entry to be removed
        '''
        self.entries.remove(entry)

    def get_durations(self):
        '''Creates a list of the duration of each entry

        return: durations, sum
        durations: a list of dictionaries containing Category and Duration
        sum: the sum of all durations
        '''
        durations = []
        sum = datetime.timedelta(seconds=0)
        for entry in self.entries:
            found = False
            for item in durations:
                # add duration if category exists already in durations
                if item['Name'] == entry.category:
                    item['Duration'] = item['Duration'] + entry.get_duration()
                    found = True
                    break

            # create a new item in durations if the category does not exist
            if not found:
                durations.append({"Name": entry.category,
                                  "Duration": entry.get_duration()})
            sum += entry.get_duration()
        return durations, sum

    def finish_module(self):
        '''stops the module'''
        self.stop = datetime.datetime.now()

    def get_categories(self):
        '''List all categories which are used in the entry list

        removes duplicates by converting list to dictionary and back

        return: list of categories
        '''
        lst = [e.category for e in self.entries]
        dictionary = dict.fromkeys(lst)
        return list(dictionary)


class Semester:
    '''
    Represents a Semester
    Holds a list of modules
    '''

    def __init__(self, name, ECTS = 0, plannedEnd = None):
        '''creates the semester
        
        name: the name of the semester
        ECTS: amount of ECTS in the semester
        plannedEnd: the plannedEnd of the semester
        '''
        self.id = str(uuid.uuid4())
        self.modules = []
        self.ECTS = ECTS
        self.plannedEnd = plannedEnd
        self.name = name

    def __eq__(self, other):
        '''can be used to compare Semester objects

        check is done based on the equality of the properties

        other: instance to be checked for equality

        returns: True if equal False if not
                  NotImplemented if other is no Entry
        '''
        if not isinstance(other, Module):
            return NotImplemented

        return self.id == other.id

    def add_module(self, module):
        '''adds a Module to the list

        module: the module to add

        raises TypeError if module is not of type Module
        '''
        if not isinstance(module, Module):
            raise TypeError
        self.modules.append(module)

    def add_entry(self, moduleName, category, comment=""):
        '''adds an entry

        if the module does not exist it is created
        moduleName: name of a module (is created if not existing in list)
        category: the category of the entry
        comment: an optional comment

        returns: the created entry
        '''
        mod = self.get_module(moduleName)
        if mod == None:
            mod = Module(moduleName)
            self.add_module(mod)
        entry = mod.add_entry(category=category, comment=comment)
        return mod, entry

    def remove_entry(self, module, entry):
        '''removes an entry

        if the module does not hold an entry anymore
        it is also removed

        module: the module
        entry: the entry
        '''
        mod = self.get_module(module.name)
        if mod is None:
            raise ValueError()
        mod.remove_entry(entry)
        if len(mod.entries) == 0:
            self.modules.remove(mod)

    def get_durations(self):
        '''Creates a list of the duration of each module

        return: durations, sum
        durations: a list of dictionaries containing Name and Duration
        sum: the sum of all durations
        '''
        durations = []
        sum = datetime.timedelta(seconds=0)
        for module in self.modules:
            entry_durations, module_duration = module.get_durations()
            durations.append(
                {"Name": module.name, "Duration": module_duration})
            sum += module_duration
        return durations, sum

    def get_module(self, name):
        '''get a module by its name

        name: moduleName to search for
        '''
        for m in self.modules:
            if m.name == name:
                return m
        return None

    def get_categories(self, modName=""):
        '''get all categories of the mods

        gets modules containing the modName and returns all categories
        modName: name which must be contained by a module
        '''
        cat_lst = []
        for mod in self.modules:
            if modName in mod.name:
                for cat in mod.get_categories():
                    cat_lst.append(cat)
        cat_dict = dict.fromkeys(cat_lst)
        return list(cat_dict)


class Study:
    '''Represents the Study

    Is top Layer of the data. Has amount of ECTS and hoursPerECTS
    Holds a list of semesters
    '''

    def __init__(self, ECTS, hoursPerECTS, plannedEnd):
        '''creates a study

        ECTS: amount of ECTS in the study
        hoursPerECTS: value how many work hours are necessary for each ECTS
        plannedEnd: the planned end of the study
        '''
        self.semesters = []
        self.ECTS = ECTS
        self.hoursPerECTS = hoursPerECTS
        self.plannedEnd = plannedEnd

    def add_semester(self, semester):
        '''adds a semester to the list

        semester: the semester to add

        raises TypeError if semester is not of type Semester
        '''
        if not isinstance(semester, Semester):
            raise TypeError

        self.semesters.append(semester)

    def add_entry(self, semesterName, moduleName, category, comment=""):
        '''adds an entry

        if the semester does not exist it is created
        semester: name of a module (is created if not existing in list)
        moduleName: name of a module (is created if not existing in list)
        category: the category of the entry
        comment: an optional comment

        returns: the created entry
        '''
        sem = self.get_semester(semesterName)
        if sem == None:
            sem = Semester(semesterName)
            self.add_semester(sem)
        mod, entry = sem.add_entry(moduleName=moduleName, category=category,
                                   comment=comment)
        return sem, mod, entry

    def remove_entry(self, semester, module, entry):
        '''removes an entry

        if the semester does not hold a module anymore it is deleted

        semester: the semester
        module: the module
        entry: the entry
        '''
        sem = self.get_semester(semester.name)
        if sem is None:
            raise ValueError
        sem.remove_entry(module, entry)
        if len(sem.modules) == 0:
            self.semesters.remove(sem)

    def get_durations(self):
        '''Creates a list of the duration of each semester

        return: durations, sum
        durations: a list of dictionaries containing Name and Duration
        sum: the sum of all durations
        '''
        durations = []
        sum = datetime.timedelta(seconds=0)
        for semester in self.semesters:
            module_durations, semester_duration = semester.get_durations()
            durations.append({"Name": semester.name,
                              "Duration": semester_duration})
            sum += semester_duration
        return durations, sum

    def get_semester(self, name):
        '''get a semester by its name

        name: semester name to search for
        '''
        for s in self.semesters:
            if s.name == name:
                return s
        return None

    def get_modules(self, semName=""):
        '''get all modules of the semesters

        gets semesters containing the semName and returns all modules
        semName: name which must be contained by the semesters
        returns list of modules
        '''
        mod_lst = []
        for s in self.semesters:
            if semName in s.name:
                mod_lst.extend([mod.name for mod in s.modules])
        tmp_dict = dict.fromkeys(mod_lst)
        return list(tmp_dict)

    def get_categories(self, semName="", modName=""):
        '''get all categories of the semesters / modules

        gets semesters and modules containing the semName/modName
        and returns all categories
        semName: name which must be contained by the semesters
        modName: name which must be contained by the modules
        returns list of categories'''
        cat_lst = []
        for sem in self.semesters:
            if semName in sem.name:
                for mod in sem.modules:
                    if modName in mod.name:
                        cat_lst.extend(mod.get_categories())
        tmp_dict = dict.fromkeys(cat_lst)
        return list(tmp_dict)


class TimeTracker:
    '''Main of the TimeTracker

    Holds a study.
    Holds the currentEntry.
    Holds the lastEntry.
    '''

    def __init__(self, study):
        '''creates a TimeTracker

        ECTS: number of total ECTS of the Study
        hoursPerECTS: defined number of hours used per ECTS (e.g. 30H/ECTS)
        '''
        self.study = study
        self.current_entry = None
        self.last_entry = None
        self.on_status_change = None
        self._timer = None
        self.on_treeview_update = None

    def start_tracking(self, semesterName, moduleName, category, comment=""):
        '''starts the tracking.

        Adds a new entry
        semesterName: name of the semester
        moduleName: name of the module
        category: the category
        comment: an optional comment
        '''
        self.current_semester, self.current_module, self.current_entry = self.study.add_entry(
            semesterName=semesterName, moduleName=moduleName,
            category=category, comment=comment)
        
        self._start_timer()

    def stop_tracking(self):
        ''' stops the current running entry'''

        if self.current_entry == None:
            raise RuntimeError("Currrently no tracking is active")

        self.current_entry.stop()
        self.last_semester = self.current_semester
        self.last_module = self.current_module
        self.last_entry = self.current_entry
        self.current_semester = None
        self.current_module = None
        self.current_entry = None

        # stop cyclic updates
        self._stop_timer()

        # notify observer
        if self.on_status_change:
            self.on_status_change(datetime.timedelta(0))

    def toggle_tracking(self, semester, module, category, comment=""):
        if self.current_entry:
            self.stop_tracking()
        else:
            self.start_tracking(semester, module, category, comment)
        
        if self.on_treeview_update:
            self.on_treeview_update()

    def _start_timer(self):
        """starts a timer for cyclic notification of observer"""
        def update():
            if self.current_entry and self.on_status_change:
                elapsed = datetime.datetime.now() - self.current_entry.start_time
                self.on_status_change(elapsed) # notfy the GUI
            self._timer = threading.Timer(1.0, update)
            self._timer.start()
        
        update()    # start first notification

    def _stop_timer(self):
        """Stops the timer for cyclic notifications"""
        if self._timer:
            self._timer.cancel()
            self._timer = None
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


SETTINGS_FILE = 'settings.json'

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

        # file menu for opening, saving, etc.
        menu = Menu(root)
        root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=lambda: self.new_tracker(edit=False))
        filemenu.add_command(label="Open", command=lambda: self.open_tracker())
        filemenu.add_command(label="Save as", command=lambda: self.save_as())
        filemenu.add_command(label="Edit", command=lambda: self.new_tracker(edit=True))

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(
            label="About", command=lambda: print("about clicked"))

        # separate window into frames using grid
        header_view = Frame(root)
        header_view.grid(row=0, column=0, sticky='news', padx=20, pady=10)

        # two different frames to switch between views
        tracker_view = Frame(root)
        tracker_view.grid(row=1, sticky='news', padx=20, pady=5)
        analyse_view = Frame(root)
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
                             self.print_chart(self.tracker.study)]).grid(row=0, column=1)

        # Tracker View
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
        # self.comment_txt = tk.Text(
        #    tracker_view, height=1, width=20).grid(row=0, column=7)

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

        self.tree.bind("<Double-Button-1>", self.tree_click)
        self.tree.pack(side='left')

        self.yscroll = ttk.Scrollbar(self.treeview_frame, orient=tk.VERTICAL,
                                     command=self.tree.yview,)
        self.tree['yscrollcommand'] = self.yscroll.set
        self.yscroll.pack(side='right', fill='y')

        self.treeview_frame.grid(row=2, columnspan=8, sticky='news')

        # Analyse View
        # TODO:
        self.accordion = None
        self.chart_frame = tk.Frame(analyse_view)
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
        # self.plot_frame.rowconfigure(1,weight=1)
        # self.plot_frame.columnconfigure(0, weight=1)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(0, self.initial_load)

        # TODO: updatechart  Scope when different tracker is loaded
        #self.chart_scope = self.tracker.study
        self.chart = None
        self.setup_observers()

    def setup_observers(self):
        '''register observers'''
        
        self.tracker.on_status_change = self.update_tracking_label

    def initial_load(self):
        '''load the initial data

        load data and update gui elements
        '''
        self.load_data()
        self.update_treeview()
        self.chart_scope = self.tracker.study

# Commands for the filemenu
    def new_tracker(self, edit):
        '''opens a window to create a new tracker
        
        edit: if the existing tracker should be edited
        '''
        # set name, planned end, num ECTS, hoursPerEcts
        # TODO: save the old tracker?
        new_window = tk.Toplevel(self.root)
        new_window.title("New Tracker")
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
            self.ECTS_var.set(self.tracker.study.ECTS)
            self.hoursPerECTS_var.set(self.tracker.study.hoursPerECTS)
            self.plannedEnd.set_datetime(self.tracker.study.plannedEnd)
            save_cmd = self.save_tracker
        else:
            save_cmd = self.save_new_tracker

        self.btn_new_tracker_save = tk.Button(
            new_window, text='save', command=lambda window=new_window: save_cmd(window)).grid(row=3, column=0)
        # TODO: remove that button

#TODO: call save_as after creating the tracker?
    def save_new_tracker(self, window):
        '''create the tracker and save it'''
        self.tracker = TimeTracker(self.ECTS_var.get(), self.hoursPerECTS_var.get(),
                                   self.plannedEnd.get_datetime())
        self.chart_scope = self.tracker.study
        window.destroy()
    
    def save_tracker(self, window):
        '''save an edited tracker
        
        destroys the window

        window: the window which is displayed
        '''
        self.tracker.study.ECTS = int(self.ECTS_var.get())
        self.tracker.study.hoursPerECTS = int(self.hoursPerECTS_var.get())
        self.tracker.study.plannedEnd = self.plannedEnd.get_datetime()

        self.chart_scope = self.tracker.study
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
            self.tracking_label.config(bg="lightgreen")
        else:
            self.start_stop_btn.config(text="Start")
            bgColor = self.root.cget("background")
            self.current_duration_label.configure(background=bgColor)
        
        self.update_treeview()

    def btn_finish_click(self):
        ''' finishes the module'''
        sem = self.tracker.study.get_semester(self.semester_var.get())
        mod = sem.get_module(self.module_var.get())
        mod.finish_module()

    def update_tracking_label(self, elapsed):
        '''update the current duration label'''
        if elapsed:
            self.current_duration_label.configure(text="Tracking for "+str(elapsed).split('.')[0])
        
    def update_label(self):
        '''update the current duration label

        is called every second
        '''
        # if tracking is running
        if self.is_tracking:
            duration = str(self.tracker.current_entry.get_duration()
                           ).split('.')[0]  # remove micros
            cat = self.tracker.current_entry.category
            mod = self.tracker.current_module.name
            self.current_duration_label.configure(
                text=f"Tracking: {cat} in module {mod} for {duration}")

            # call this method after one second
            self.root.after(1000, self.update_label)

    def update_combo_semesters(self):
        '''updates the values of the semester combobox'''
        semesters = [s.name for s in self.tracker.study.semesters]
        self.semester_combobox['values'] = semesters

    def update_combo_modules(self):
        '''
        updates the values of the modules combobox depending on the semesters combobox
        '''
        sem_name = self.semester_var.get()
        self.module_combobox['values'] = self.tracker.study.get_modules(
            semName=sem_name)

    def update_combo_categories(self):
        '''
        updates the values ot the categories combobox depending on the semester and module comboboxes
        '''
        sem_name = self.semester_var.get()
        mod_name = self.module_var.get()
        self.category_combobox['values'] = self.tracker.study.get_categories(
            semName=sem_name, modName=mod_name)

    def update_treeview(self):
        '''updates the treeview

        deletes all existing items and generates new items depending on the
        selected  semester, module and category

        serializes the data for the click event
        '''

        # clean all existing entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        semName = self.semester_var.get()
        modName = self.module_var.get()
        catName = self.category_var.get()

        for sem in self.tracker.study.semesters:
            if semName in sem.name or semName == "":
                for mod in sem.modules:
                    if modName in mod.name or modName == "":
                        for entry in mod.entries:
                            add = True
                            if (catName in entry.category or catName == ""):
                                start_time = entry.start_time.strftime(
                                    "%Y-%m-%d %H:%M:%S")
                                duration = str(entry.get_duration()).split('.')[
                                    0]  # remove micros
                                sem_obj = pickle.dumps(sem)
                                sem_base64 = base64.b64encode(
                                    sem_obj).decode('utf-8')
                                mod_obj = pickle.dumps(mod)
                                mod_base64 = base64.b64encode(
                                    mod_obj).decode('utf-8')
                                entry_obj = pickle.dumps(entry)
                                entry_base64 = base64.b64encode(
                                    entry_obj).decode('utf-8')
                                self.tree.insert(
                                    "", "end", text=sem.name,
                                    values=(mod.name, entry.category,
                                            entry.comment, start_time,
                                            duration), tags=(sem_base64, mod_base64, entry_base64,))

    def tree_click(self, event):
        '''click event of the treeview

        calls a new window to editor remove the clicked entry or create a
        new entry
        '''
        # deserialize the data
        selected = self.tree.focus()
        item = self.tree.item(selected)
        tags = item['tags']
        sem_base64 = tags[0]
        sem_pickle = base64.b64decode(sem_base64)
        sem = pickle.loads(sem_pickle)
        mod_base64 = tags[1]
        mod_pickle = base64.b64decode(mod_base64)
        mod = pickle.loads(mod_pickle)

        entry_base64 = tags[2]
        entry_pickle = base64.b64decode(entry_base64)
        entry = pickle.loads(entry_pickle)

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

        if mod.stop != None:
            self.module_end = DateTimeFrame(edit_window, label="Module end:")
            self.module_end.grid(row=3, columnspan=4, sticky='w')
            self.module_end.set_datetime(mod.stop)

        add_btn = tk.Button(edit_window, text="Save as new entry",
                            command=lambda s=sem, m=mod, e=entry: self.add_new_entry())
        add_btn.grid(row=4, column=0, sticky='news')
        edit_btn = tk.Button(edit_window, text='Save entry',
                             command=lambda s=sem, m=mod, e=entry: self.edit(s, m, e))
        edit_btn.grid(row=4, column=1, sticky='news')
        remove_btn = tk.Button(edit_window, text='Delete entry',
                               command=lambda s=sem, m=mod, e=entry: self.remove(s, m, e))
        remove_btn.grid(row=4, column=2, sticky='news')

    def remove(self, sem, mod, entry):
        '''remove an entry

        sem: the semester
        mod: the module
        entry: the entry
        '''
        self.tracker.study.remove_entry(sem, mod, entry)
        self.update_treeview()

    def add_new_entry(self):
        ''' add a new entry

        the values of the user controls are read

        returns the semester, module and entry
        '''
        semName = self.sem_var.get()
        modName = self.mod_var.get()
        catName = self.cat_var.get()
        comment = self.comment_var.get()
        s, m, e = self.tracker.study.add_entry(
            semName, modName, catName, comment)
        e.start_time = self.start_time.get_datetime()
        e.stop_time = self.stop_time.get_datetime()
        self.update_treeview()
        return s, m, e

    def edit(self, sem, mod, entry):
        ''' edit an entry

        the entry is deleted and a new one is created

        sem: the semester
        mod: the module
        entry: the entry
        '''
        self.remove(sem, mod, entry)
        s, m, e = self.add_new_entry()
        if mod.stop != None:
            m.stop = self.module_end.get_datetime()

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
        semesterNames = [sem.name for sem in self.tracker.study.semesters]
        for sec in self.accordion.sections:
            if sec.name not in semesterNames:
                # delete the section
                self.accordion.remove_section(sec)
                continue

            sem = self.tracker.study.get_semester(sec.name)
            moduleNames = [mod.name for mod in sem.modules]
            for entry in sec.sub_elements:
                if entry.name not in moduleNames:
                    # delete the entry
                    sec.remove_element(entry)
                    continue

        # add new entries
        for sem in self.tracker.study.semesters:
            foundSem = False
            for sec in self.accordion.sections:
                if sem.name == sec.name:
                    # found the semester, check for the modules and continue with next semester
                    foundSem = True
                    for mod in sem.modules:
                        foundMod = False
                        for entry in sec.sub_elements:
                            if mod.name == entry.name:
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
                for mod in sem.modules:
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
        if self.active_chart == ChartType.BURNDOWN:
            stopTimes = []
            values = []
            start = []
            total_work = 0
            planned_end = 0
            end = []
            if isinstance(scope, Study):
                total_work = scope.ECTS
                for sem in scope.semesters:
                    for mod in sem.modules:
                        start.append(mod.start)
                        end.append(mod.plannedEnd)
                        if mod.stop != None:
                            stopTimes.append(mod.stop)
                            values.append(mod.ECTS)
                end.append(scope.plannedEnd)
            elif isinstance(scope, Semester):
                # Only Modules which are already tracked are respected in the
                # diagram
                for mod in scope.modules:
                    start.append(mod.start)
                    end.append(mod.plannedEnd)
                    total_work += mod.ECTS
                    if mod.stop != None:
                        stopTimes.append(mod.stop)
                        values.append(mod.ECTS)
            elif isinstance(scope, Module):
                pass

            # get the latest planned end
            end.sort(reverse=True)
            planned_end = end[0].strftime('%Y.%m')

            # get the first start of a module
            start.sort()
            stopTimes.append(start[0])
            values.append(0)

            # sort the values
            sortedList = sorted(zip(stopTimes, values))
            a = [x.strftime('%Y.%m') for x, _ in sortedList]
            b = [x for _, x in sortedList]
            self.chart = ChartFactory.create_chart(
                self.active_chart, a, b, total_work, planned_end)
        else:
            durations, _ = scope.get_durations()
            names = [dur.get('Name')for dur in durations]
            values = [dur.get('Duration').total_seconds() for dur in durations]
            self.chart = ChartFactory.create_chart(
                self.active_chart, names, values)
        self.chart.plot(self.plot_frame)

    def save_data(self, filename=None):  # TODO: save in correct format
        '''saves the data

        Saves the timetracker to the specified file.
        If no file is specified the last used file is used
        If a file is specified it is saved as last used file

        filename: the file where to save the timetracker
        '''
        if filename is None:
            filename = "time_tracking_data.json"
        with open(filename, "wb") as file:
            pickle.dump(self.tracker, file, pickle.HIGHEST_PROTOCOL)
        self.settings['last_used_file'] = filename
        self.save_settings(self.settings)

    def load_data(self, filename=None):
        '''Loads a previous saved timetracker.

        Loads the tracker specified by filename.
        If no filename is specified the last used file is used.
        If there is no last used file of a previous started session a new tracker
        is started.

        filename: the Filename
        '''
        # no filename given search settings file
        if filename is None:
            self.settings = self.load_settings()
            filename = self.settings.get('last_used_file')
            if filename is None:    # no existing settings file start new tracker
                self.new_tracker()
                return
        try:
            with open(filename, "rb") as file:
                self.tracker = pickle.load(file)
                if (self.tracker.last_semester):
                    self.semester_var.set(self.tracker.last_semester.name)
                self.module_var.set(self.tracker.last_module.name)
                self.category_var.set(self.tracker.last_entry.category)
                self.comment_var.set(self.tracker.last_entry.comment)
                self.chart_scope = self.tracker.study
        except FileNotFoundError:
            self.new_tracker()
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Error while loading data: {e}")

    def save_settings(self, settings):
        '''saves the settings (last used file) to the SETTINGS_FILE path'''
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file)

    def load_settings(self):
        '''loads the settings (last used file) from thee SETTINGS_FILE path'''
        try:
            with open(SETTINGS_FILE, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def on_close(self):
        '''callback function for application shutdown

        saves the data to the last used filename
        '''
        filename = self.settings.get('last_used_file')
        self.save_data(filename)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()

    # model
    study = Study(180,30, datetime.datetime.now())

    # controller
    tracker = TimeTracker(study)

    # view
    app = TimeTrackerGUI(root, tracker)
    root.mainloop()
