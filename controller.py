import datetime
import threading
import uuid
from model import Semester, Module, Entry

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
        self._study = study
        self.current_entry = None
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
        self.current_semester, self.current_module, self.current_entry = self._study.add_entry(
            semesterName=semesterName, moduleName=moduleName,
            category=category, comment=comment)
        
        self._start_timer()

    def stop_tracking(self):
        ''' stops the current running entry'''

        if self.current_entry == None:
            raise RuntimeError("Currrently no tracking is active")

        self.current_entry.stop()
        self._study.set_last_information(self.current_semester, self.current_module, self.current_entry)
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

    def serialize_object(self, obj):
        '''serializes an Objekt to a unique id'''
        try:
            if obj.id:
                pass
        except AttributeError:
            obj.id = str(uuid.uuid4())

        if isinstance(obj, Semester):
            return f"semester:{obj.id}"
        elif isinstance(obj, Module):
            return f"module:{obj.id}"
        elif isinstance(obj, Entry):
            return f"entry:{obj.id}"
        raise ValueError("Unsupported objext type for serialization")

    def deserialize_object(self, obj_id):
        '''deserializes from an id to an object'''

        obj_type, key = obj_id.split(":",1)
        if obj_type == "semester":
            for semester in self._study.semesters:
                if semester.id == key:
                    return semester
        elif obj_type == "module":
            for semester in self._study.semesters:
                for module in semester.modules:
                    if module.id == key:
                        return module
        elif obj_type == "entry":
            for semester in self._study.semesters:
                for module in semester.modules:
                    for entry in module.entries:
                        if entry.id == key:
                            return entry
        return None

    def get_filtered_data_list(self, selected_semester, selected_module, selected_category):
        filtered_data = []

        # filter by selected semester
        for semester in self._study.semesters:
            if selected_semester and semester.name != selected_semester:
                continue  # skip if semester names dont match

            # filter by selected module
            for module in semester.modules:
                if selected_module and module.name != selected_module:
                    continue  # skip if module names dont match

                for entry in module.entries:
                    if selected_category and entry.category != selected_category:
                        continue # skip if categories dont match

                    filtered_data.append({"semester":semester, "module":module, "entry":entry})

        return filtered_data
    
    def get_initial_entry(self):
        '''gets the information which should used at startup'''
        return self._study.get_last_information()
    
    def get_semester(self, semName):
        '''get a semester by its name'''
        return self._study.get_semester(semName)

    def get_semesters(self):
        '''get all semesters of the study'''
        return self._study.semesters
    
    def get_semester_names(self):
        ''' get all semester names of the study'''
        return [s.name for s in self.get_semesters()]

    def get_modules(self, semName):
        '''get all modules of a semester'''
        return self._study.get_modules(semName)
    
    def get_module_names(self, semName):
        '''get all module names of a semester'''
        return self.get_modules(semName)

    def get_category_names(self, semName, modName):
        '''get all category names of a module'''
        return self._study.get_categories(semName, modName)

