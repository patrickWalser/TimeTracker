import tkinter as tk
from tkinter import messagebox, ttk, Frame
import datetime
import pickle

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

    def __init__(self, name, ECTS = 5, duration = 6):
        '''creates and starts the module.

        name: name of the module as string
        ECTS: amount of ECTS (credits) default = 5
        duration: planned duration of the module default = 6 weeks
        '''
        self.entries = []
        self.name = name
        self.ECTS = ECTS
        self.start_module(duration=duration)
    
    def start_module(self, duration):
        '''Starts the module.

        duration: planned duration of the module in weeks
        '''
        self.start = datetime.datetime.now()
        self.plannedEnd= self.start + datetime.timedelta(weeks=duration)

    def add_entry(self, category, comment=""):
        '''creates an entry and adds it to the list of entries

        category: category of the entry
        comment: optional comment for the entry

        return: the created entry
        '''
        entry = Entry(category= category, comment=comment)
        self.entries.append(entry)
        return entry
        
    def get_durations(self):
        '''Creates a list of the duration of each entry
        
        return: durations, sum
        durations: a list of dictionaries containing Category and Duration
        sum: the sum of all durations
        '''
        durations = []
        sum = datetime.timedelta(seconds=0)
        for entry in self.entries:
            durations.append({"Category":entry.category,
                              "Duration":entry.get_duration()})
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
        self.ECTS = 0 # TODO: are ECTS necessary?
        self.name = name

    def add_module(self, module:Module):
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
        return mod.add_entry(category= category, comment= comment)

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
            durations.append({"Name":module.name, "Duration":module_duration})
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

class Study:
    '''Represents the Study
    
    Is to top Layer of the data. Has amount of ECTS and hoursPerECTS
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

    def add_semester(self, semester:Semester):
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
        return sem.add_entry(moduleName=moduleName, category=category,
                      comment=comment)

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
            durations.append({"Name":semester.name, 
                              "Duration": semester_duration})
            sum += semester_duration
        return durations, sum

    def get_semester(self, name):
        '''get a module by its name
        
        name: semester name to search for
        '''
        for s in self.semesters:
            if s.name == name:
                return s
        return None

class TimeTracker:
    '''Main of the TimeTracker
    
    Holds a study.
    Holds the currentEntry
    '''
    def __init__(self, ECTS, hoursPerECTS):
        '''creates a TimeTracker
        
        ECTS: number of total ECTS of the Study
        hoursPerECTS: defined number of hours used per ECTS (e.g. 30H/ECTS)
        '''
        self.study = Study(ECTS, hoursPerECTS)
        self.current_entry = None

    def start_tracking(self, semesterName, moduleName, category, comment=""):
        '''starts the tracking.
        
        Adds a new entry
        semesterName: name of the semester
        moduleName: name of the module
        category: the category
        comment: an optional comment
        '''
        self.current_entry = self.study.add_entry(
            semesterName=semesterName, moduleName=moduleName,
            category=category, comment=comment)

    def stop_tracking(self):
        ''' stops the current running entry'''

        if self.current_entry == None:
            raise RuntimeError("Currrently no tracking is active")

        self.current_entry.stop()
        self.current_entry = None
        pass


class TimeTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TimeTracker")

        self.tracker = TimeTracker(180,30)
        self.load_data()

        # separate window into frames using grid
        header_view = Frame(root)
        header_view.grid(row=0, column = 0, sticky ='news')

        # two different frames to switch between views
        tracker_view = Frame(root)
        tracker_view.grid(row=1, sticky='news')
        analyse_view = Frame(root)
        analyse_view.grid(row=1, sticky='news')

        # Buttons to switch between the two views
        self.tracker_btn = tk.Button(header_view, text = "Tracker", command = lambda:tracker_view.tkraise()).grid(row=0, column=0)
        self.analyse_btn = tk.Button(header_view, text = "Analyse" , command = lambda:analyse_view.tkraise()).grid(row = 0, column=1)

        # Tracker View
        #self.label =tk.Label(tracker_view, text="Tracker View").pack()
        self.semester_label = tk.Label(tracker_view, text="Semester: ").grid(row=0, column=0)
        self.semester_var =tk.StringVar()
        self.semester_combobox = ttk.Combobox(tracker_view, textvariable=self.semester_var, postcommand=self.update_semesters)
        self.semester_combobox.grid(row=0, column = 1)

        self.module_label = tk.Label(tracker_view, text="Module: ").grid(row=0, column=2)
        self.module_var =tk.StringVar()
        self.module_combobox = ttk.Combobox(tracker_view, textvariable=self.module_var, postcommand=self.update_modules)
        self.module_combobox.grid(row=0, column = 3)

        self.category_label = tk.Label(tracker_view, text="Category: ").grid(row=0, column=4)
        self.category_var =tk.StringVar()
        self.category_combobox = ttk.Combobox(tracker_view, textvariable=self.category_var, postcommand=self.update_categories)
        self.category_combobox.grid(row=0, column = 5)

        self.comment_label =tk.Label(tracker_view, text="comment: ").grid(row=0,column=6)
        self.comment_var = tk.Text(tracker_view, height = 1,width = 20).grid(row=0, column=7)

        self.is_tracking = False
        self.start_stop_btn = tk.Button(tracker_view, text = "Start", command = self.btn_start_stop_click)
        self.start_stop_btn.grid(row = 1, column = 0)

        # TODO: update duration labels
        self.current_duration_label = tk.Label(tracker_view, text="current duration: ")
        self.current_duration_label.config(state="disabled")
        self.current_duration_label.grid(row=1, column=1)

        self.total_duration_label = tk.Label(tracker_view, text = "total duration: ")
        self.total_duration_label.config(state="disabled")
        self.total_duration_label.grid(row=1, column=2)

        self.tree = ttk.Treeview(tracker_view, columns=('Task', 'total duration'))
        self.tree.heading('Task', text='Task')
        self.tree.heading('total duration', text='total duration')
        self.tree.grid(row=2, columnspan=8)

        # Analyse View
        self.label_analyse = tk.Label(analyse_view, text="Analyse View").pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        tracker_view.tkraise()
        # TODO:

    def btn_start_stop_click(self):
        if(self.is_tracking):
            # stop tracking
            self.tracker.stop_tracking()
            self.start_stop_btn.config(text="Start")
            self.is_tracking = False
        else:
            # start tracking
            self.tracker.start_tracking(self.semester_var.get(), self.module_var.get(), self.category_var.get(),"" '''self.comment_var.get()''')
            # TODO: can comboboxes be blocked because tracking is active?
            self.start_stop_btn.config(text="Stop")
            self.is_tracking = True

    def start_tracking(self):
        pass

    def stop_tracking(self):
        pass

    def update_semesters(self):
        semesters = [s.name for s in self.tracker.study.semesters]
        self.semester_combobox['values'] = semesters

    def update_modules(self):
        sem = self.tracker.study.get_semester(self.semester_var.get())
        modules = [m.name for m in sem.modules]
        self.module_combobox['values'] = modules

    def update_categories(self):
        sem = self.tracker.study.get_semester(self.semester_var.get())
        mod = sem.get_module(self.module_var.get())
        categories = mod.get_categories()
        self.category_combobox['values']= list(categories)


    def save_data(self): # TODO: save in correct format
        with open("time_tracking_data.json","wb") as file:
            pickle.dump(self.tracker.study, file, pickle.HIGHEST_PROTOCOL)

    def load_data(self):
        try:
            with open("time_tracking_data.json", "rb") as file:
                self.tracker.study = pickle.load(file)
        except FileNotFoundError:
            self.tracker.study = Study(180,30)
        except Exception as e:
            messagebox.showerror("Error", f"Error while loading data: {e}")

    def on_close(self):
        self.save_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerGUI(root)
    root.mainloop()