from my_accordion import Accordion
import tkinter as tk
from tkinter import messagebox, ttk, Frame
import datetime
import pickle
import base64
from charts import ChartType, ChartFactory
from tkcalendar import DateEntry


class Entry:
    '''Class Entry holds the information of an entry'''

    def __init__(self, category, comment=""):
        '''creates and starts an entry

        category: category of the entry as string
        commen: optional comment as string
        '''
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

        return self.start_time == other.start_time and \
            self.stop_time == other.stop_time and \
            self.category == other.category and self.comment == other.comment

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

        return self.entries == other.entries and self.name == other.name and self.ECTS == other.ECTS and self.start == other.start and self.stop == other.stop and self.plannedEnd == other.plannedEnd


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
                if item['Name'] == entry.category:
                    item['Duration'] = item['Duration'] + entry.get_duration()
                    found = True
                    break

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

    def __init__(self, name):
        '''creates the semester'''
        self.modules = []
        self.ECTS = 0  # TODO: are ECTS necessary?
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
        
        return self.modules == other.modules and self.ECTS == other.ECTS and self.name == other.name
    
    def add_module(self, module: Module):
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

    def __init__(self, ECTS, hoursPerECTS):
        '''creates a study

        ECTS: amount of ECTS in the study
        hoursPerECTS: value how many work hours are necessary for each ECTS
        '''
        self.semesters = []
        self.ECTS = ECTS
        self.hoursPerECTS = hoursPerECTS

    def add_semester(self, semester: Semester):
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

    def __init__(self, ECTS, hoursPerECTS):
        '''creates a TimeTracker

        ECTS: number of total ECTS of the Study
        hoursPerECTS: defined number of hours used per ECTS (e.g. 30H/ECTS)
        '''
        self.study = Study(ECTS, hoursPerECTS)
        self.current_entry = None
        self.last_entry = None

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

class DateTimeFrame(Frame):
    def __init__(self, parent, label):
        super().__init__(parent)

        tk.Label(self, text=label).grid(row=0, column=0, sticky='w')
        tk.Label(self, text="Date:").grid(row=0, column=1, sticky='w')
        self.date = DateEntry(self)
        self.date.grid(row=0, column=2)

        tk.Label(self, text="Time:").grid(row=0, column=3, sticky='w')
        self.hour_entry = ttk.Combobox(self, values=[f"{i:02}" for i in range(24)], width=3)
        self.hour_entry.grid(row=0, column=4, sticky='w')
        
        self.minute_entry = ttk.Combobox(self, values=[f"{i:02}" for i in range(60)], width=3)
        self.minute_entry.grid(row=0, column=5, sticky='w')

    def set_datetime(self, datetime:datetime.datetime):
        if(datetime is None): #  leave empty
            return

        self.date.set_date(datetime)
        self.hour_entry.set(datetime.hour)
        self.minute_entry.set(datetime.minute)

    def get_datetime(self):
        date = self.date.get_date()
        h = int(self.hour_entry.get())
        m = int(self.minute_entry.get())
        return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=h,minute=m)

SETTINGS_FILE = 'settings.json'

class TimeTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TimeTracker")
        self.root.geometry('900x450')

        self.tracker = TimeTracker(180, 30)

        # separate window into frames using grid
        header_view = Frame(root)
        header_view.grid(row=0, column=0, sticky='news')

        # two different frames to switch between views
        tracker_view = Frame(root)
        tracker_view.grid(row=1, sticky='news')
        analyse_view = Frame(root)
        analyse_view.grid(row=1, sticky='news')

        # Buttons to switch between the two views
        self.tracker_btn = tk.Button(
            header_view, text="Tracker",
            command=lambda: tracker_view.tkraise()).grid(row=0, column=0)
        self.analyse_btn = tk.Button(
            header_view, text="Analyse",
            command=lambda: [analyse_view.tkraise(),
                             self.generate_accordion(analyse_view),
                             self.print_chart(self.tracker.study)]).grid(row=0, column=1)

        # Tracker View
        # self.label =tk.Label(tracker_view, text="Tracker View").pack()
        self.semester_label = tk.Label(
            tracker_view, text="Semester: ").grid(row=0, column=0)
        self.semester_var = tk.StringVar()
        self.semester_var.trace_add('write', self.combo_update)
        self.semester_combobox = ttk.Combobox(
            tracker_view, textvariable=self.semester_var,
            postcommand=self.update_combo_semesters)
        self.semester_combobox.grid(row=0, column=1)

        self.module_label = tk.Label(
            tracker_view, text="Module: ").grid(row=0, column=2)
        self.module_var = tk.StringVar()
        self.module_var.trace_add('write', self.combo_update)
        self.module_combobox = ttk.Combobox(
            tracker_view, textvariable=self.module_var,
            postcommand=self.update_combo_modules)
        self.module_combobox.grid(row=0, column=3)

        self.category_label = tk.Label(
            tracker_view, text="Category: ").grid(row=0, column=4)
        self.category_var = tk.StringVar()
        self.category_var.trace_add('write', self.combo_update)
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
        self.start_stop_btn.grid(row=1, column=0)

        finish_btn = tk.Button(tracker_view,text='Finish module', command= lambda:self.btn_finish_click())
        finish_btn.grid(row=1, column=1,sticky='news')

        self.current_duration_label = tk.Label(
            tracker_view, text="")
        self.current_duration_label.grid(
            row=1, column=2, columnspan=3, sticky="W")

        self.treeview_frame = Frame(tracker_view)

        self.tree = ttk.Treeview(self.treeview_frame, columns=(
            'Module', 'Category', 'Comment', 'Start', 'Duration'), height=7)
        self.tree.heading('#0', text='Semester')
        self.tree.heading('Module', text='Module')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Comment', text='Comment')
        self.tree.heading('Start', text='Start')
        self.tree.heading('Duration', text='Duration')

        self.tree.column('#0', minwidth=0, width=100, stretch=True)
        self.tree.column('Module', minwidth=0, width=100, stretch=True)
        self.tree.column('Category', minwidth=0, width=100, stretch=True)
        self.tree.column('Comment', minwidth=0, width=100, stretch=True)
        self.tree.column('Start', minwidth=0, width=100, stretch=True)
        self.tree.column('Duration', minwidth=0, width=100, stretch=True)

        self.tree.bind("<Double-Button-1>", self.tree_click)
        self.tree.pack(side='left')

        self.yscroll = ttk.Scrollbar(self.treeview_frame, orient=tk.VERTICAL,
                                     command=self.tree.yview,)
        self.tree['yscrollcommand'] = self.yscroll.set
        self.yscroll.pack(side='right', fill='y')

        self.treeview_frame.grid(row=2, columnspan=8)
        # Analyse View
        # TODO:
        self.chart_frame = tk.Frame(analyse_view)
        self.chart_frame.grid(row=0, column = 1, sticky='nw')
        self.active_chart = ChartType.PIE
        chart_frame_header = tk.Frame(self.chart_frame)
        chart_frame_header.grid(row=0, sticky='nw')
        btn_burndown = tk.Button(chart_frame_header,text="Burndown-Chart", command=lambda: self.set_active_chart(ChartType.BURNDOWN))
        btn_burndown.grid(row=0, column=0, sticky='nw')
        btn_pie = tk.Button(chart_frame_header, text="Pie-Chart", command=lambda: self.set_active_chart(ChartType.PIE))
        btn_pie.grid(row=0, column=1, sticky='nw')

        self.plot_frame = tk.Frame(self.chart_frame)
        self.plot_frame.grid(row=1, sticky = 'news')

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_data()
        self.update_treeview()

        self.chart_scope = self.tracker.study
        self.chart = None
        
        tracker_view.tkraise()

    def print_chart(self, scope):
        # prevent memory leak because matplotlib figure remains open
        # TODO: write to Testprotocol
        # TODO: Burndown check for instance of scope
        if self.chart:
            self.chart.destroy()

        if self.active_chart == ChartType.BURNDOWN:
            stopTimes = []
            values = []
            start = []
            total_work = 0
            planned_end = 0
            end = []
            if isinstance(scope,Study):
                total_work = scope.ECTS
                for sem in scope.semesters:
                    for mod in sem.modules:
                        start.append(mod.start)
                        end.append(mod.plannedEnd)
                        if mod.stop != None:
                            stopTimes.append(mod.stop)
                            values.append(mod.ECTS)
            elif isinstance(scope,Semester):
                # Only Modules which are already tracked are respected in the
                # diagram
                for mod in scope.modules:
                    start.append(mod.start)
                    end.append(mod.plannedEnd)
                    total_work += mod.ECTS
                    if mod.stop != None:
                        stopTimes.append(mod.stop)
                        values.append(mod.ECTS)
            elif isinstance(scope,Module):
                pass
            
            end.sort(reverse=True)
            planned_end = end[0]

            start.sort()
            stopTimes.append(start[0])
            values.append(0)

            sortedList = sorted(zip(stopTimes,values))
            a = [x for x,_ in sortedList]
            b = [x for _,x in sortedList]
            self.chart = ChartFactory.create_chart(self.active_chart, a, b, total_work, planned_end)
        else:
            durations,_ = scope.get_durations()
            names = [dur.get('Name')for dur in durations]
            values = [dur.get('Duration').total_seconds() for dur in durations]
            self.chart = ChartFactory.create_chart(self.active_chart, names, values)
        self.chart.plot(self.plot_frame)

    def set_active_chart(self, chart_type):
        self.active_chart = chart_type
        self.print_chart(self.chart_scope)

    def generate_accordion(self, parent):
        try:
            self.accordion.destroy()
        except:
            pass

        self.accordion = Accordion(parent)
        self.accordion.grid(row=0, column=0, sticky='ns')

        for sem in self.tracker.study.semesters:
            section = self.accordion.add_section(
                sem.name, lambda sem=sem: self.print_chart(sem))
            for mod in sem.modules:
                section.add_element(mod.name, lambda mod=mod: self.print_chart(mod))

    def update_label(self):
        if self.is_tracking:
            duration = str(self.tracker.current_entry.get_duration()
                        ).split('.')[0]  # remove micros
            cat = self.tracker.current_entry.category
            mod = self.tracker.current_module.name
            self.current_duration_label.configure(
                text=f"Tracking: {cat} in module {mod} for {duration}")

            self.root.after(1000, self.update_label)

    def combo_update(self, index, value, op):
        self.update_treeview()

    def tree_click(self, event):
        # todo implement editing
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

        # TODO: call a new window for editing
        # if edit -> delete curr entry and create new entry
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit entry")

        self.sem_var =tk.StringVar()
        sem_entry = tk.Entry(edit_window, textvariable=self.sem_var)
        sem_entry.grid(row=0, column= 0)
        self.sem_var.set(sem.name)
        
        self.mod_var =tk.StringVar()
        mod_entry = tk.Entry(edit_window, textvariable=self.mod_var)
        mod_entry.grid(row=0, column=1)
        self.mod_var.set(mod.name)

        self.cat_var = tk.StringVar()
        cat_entry = tk.Entry(edit_window, textvariable=self.cat_var)
        cat_entry.grid(row=0, column = 2)
        self.cat_var.set(entry.category)

        self.comment_var = tk.StringVar()
        comment_entry = tk.Entry(edit_window, textvariable=self.comment_var)
        comment_entry.grid(row=0, column=3)
        self.comment_var.set(entry.comment)

        self.start_time = DateTimeFrame(edit_window, label="start time:")
        self.start_time.grid(row=1, columnspan=4, sticky='w')
        self.start_time.set_datetime(entry.start_time)

        self.stop_time = DateTimeFrame(edit_window, label = "stop time:")
        self.stop_time.grid(row=2, columnspan=4, sticky='w')
        self.stop_time.set_datetime(entry.stop_time)

        if mod.stop != None:
            self.module_end = DateTimeFrame(edit_window, label = "Module end:")
            self.module_end.grid(row=3, columnspan=4, sticky='w')
            self.module_end.set_datetime(mod.stop)

        add_btn =tk.Button(edit_window, text = "Add new entry", command = lambda s = sem, m=mod, e=entry:self.add_new_entry())
        add_btn.grid(row=4, column = 0, sticky='news')
        edit_btn =tk.Button(edit_window, text='Edit entry', command = lambda s = sem, m=mod, e = entry: self.edit(s, m, e))
        edit_btn.grid(row=4, column=1, sticky='news')
        remove_btn = tk.Button(edit_window,text='Delete entry', command = lambda s = sem, m=mod, e = entry: self.remove(s, m, e))
        remove_btn.grid(row=4, column = 2, sticky='news')

    def remove(self, sem, mod, entry):
        self.tracker.study.remove_entry(sem, mod, entry)
        self.update_treeview()
        print("removed entry")

    def edit(self, sem, mod, entry):
        self.remove(sem, mod, entry)
        s,m,e = self.add_new_entry()
        if mod.stop !=  None:
            m.stop = self.module_end.get_datetime()

    def add_new_entry(self):
        semName = self.sem_var.get()
        modName = self.mod_var.get()
        catName = self.cat_var.get()
        comment = self.comment_var.get()
        s,m,e = self.tracker.study.add_entry(semName, modName, catName, comment)
        e.start_time = self.start_time.get_datetime()
        e.stop_time = self.stop_time.get_datetime()
        self.update_treeview()
        print("added entry")
        return s,m,e

    def btn_start_stop_click(self):
        if (self.is_tracking):
            # stop tracking
            self.tracker.stop_tracking()
            self.start_stop_btn.config(text="Start")
            bgColor = self.root.cget("background")
            self.current_duration_label.configure(background=bgColor)
            self.is_tracking = False
        else:
            # start tracking
            self.tracker.start_tracking(
                self.semester_var.get(), self.module_var.get(),
                self.category_var.get(), self.comment_var.get())
            # TODO: can comboboxes be blocked because tracking is active?
            self.start_stop_btn.config(text="Stop")
            self.current_duration_label.configure(background='light green')
            self.is_tracking = True
            self.update_label()

        self.update_treeview()

    def btn_finish_click(self):
        sem = self.tracker.study.get_semester(self.semester_var.get())
        mod = sem.get_module(self.module_var.get())
        mod.finish_module()

    def update_combo_semesters(self):
        semesters = [s.name for s in self.tracker.study.semesters]
        self.semester_combobox['values'] = semesters

    def update_combo_modules(self):
        sem_name = self.semester_var.get()
        self.module_combobox['values'] = self.tracker.study.get_modules(
            semName=sem_name)
        """
        if sem_name:
            sem_lst = [self.tracker.study.get_semester(sem_name)]
        else:
            sem_lst = self.tracker.study.semesters
        for sem in sem_lst:
            modules = [m.name for m in sem.modules]
        self.module_combobox['values'] = modules
        """

    def update_combo_categories(self):
        sem_name = self.semester_var.get()
        mod_name = self.module_var.get()
        self.category_combobox['values'] = self.tracker.study.get_categories(
            semName=sem_name, modName=mod_name)
        """
        sem = self.tracker.study.get_semester(self.semester_var.get())
        mod = sem.get_module(self.module_var.get())
        categories = mod.get_categories()
        self.category_combobox['values'] = list(categories)
        """

    def update_treeview(self):
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
                                sem_obj= pickle.dumps(sem)
                                sem_base64 = base64.b64encode(sem_obj).decode('utf-8')
                                mod_obj = pickle.dumps(mod)
                                mod_base64 = base64.b64encode(mod_obj).decode('utf-8')
                                entry_obj = pickle.dumps(entry)
                                entry_base64 = base64.b64encode(entry_obj).decode('utf-8')
                                self.tree.insert(
                                    "", "end", text=sem.name,
                                    values=(mod.name, entry.category,
                                            entry.comment, start_time,
                                            duration), tags=(sem_base64, mod_base64, entry_base64,))


    def save_data(self, filename= None):  # TODO: save in correct format
        if filename is None:
            filename = "time_tracking_data.json"
        with open(filename, "wb") as file:
            pickle.dump(self.tracker, file, pickle.HIGHEST_PROTOCOL)
        self.settings['last_used_file']= filename
        self.save_settings(self.settings)

    def load_data(self, filename=None):
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
                if(self.tracker.last_semester):
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
        with open(SETTINGS_FILE,'w') as file:
            json.dump(settings,file)

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def on_close(self):
        filename = self.settings.get('last_used_file')
        self.save_data(filename)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerGUI(root)
    root.mainloop()
