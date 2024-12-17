import os
import datetime
import threading
import uuid
import json
from model import Study, Semester, Module, Entry
from charts import ChartFactory, ChartType
from settings import Settings

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
        self.settings = Settings()

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
            if selected_semester and not semester.name.startswith(selected_semester):
                continue  # skip if semester names dont match

            # filter by selected module
            for module in semester.modules:
                if selected_module and not module.name.startswith(selected_module):
                    continue  # skip if module names dont match

                for entry in module.entries:
                    if selected_category and not entry.category.startswith(selected_category):
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
        return [m.name for m in self.get_modules(semName)]

    def get_category_names(self, semName, modName):
        '''get all category names of a module'''
        return self._study.get_categories(semName, modName)
    
    def finish_module(self, semester_name, module_name):
        '''finishes a module
        
        semester_name: name of the semester
        module_name: name of the module
        '''
        sem = self.get_semester(semester_name)
        mod = sem.get_module(module_name)
        mod.finish_module()
        if self.on_treeview_update:
            self.on_treeview_update()

    def add_new_entry(self, semester_name, module_name, category, comment, start_time, stop_time):
        '''adds a new entry
        
        semester_name: name of the semester
        module_name: name of the module
        category: the category
        comment: an optional comment
        start_time: the start time of the entry
        stop_time: the stop time of the entry
        '''
        sem, mod, entry = self._study.add_entry(semester_name, module_name, category, comment)
        entry.start_time = start_time
        entry.stop_time = stop_time
        
        if self.on_treeview_update:
            self.on_treeview_update()
        return sem, mod, entry

    def remove_entry(self, semester, module, entry):
        '''removes an entry
        
        removes also the semester or the module if they have no entries left

        semester: the semester of the entry
        module: the module of the entry
        entry: the entry to remove'''
        self._study.remove_entry(semester, module, entry)

        if self.on_treeview_update:
            self.on_treeview_update()

    def edit_entry(self, semester, module, entry, edit_semester_name, edit_module_name, edit_category, edit_comment, edit_start_time, edit_stop_time, edit_module_start, edit_module_stop):
        '''edits an entry
        
        removes the old entry and adds a new one with the new information

        semester: the semester of the entry
        module: the module of the entry
        entry: the entry to edit
        edit_semester_name: the new semester name
        edit_module_name: the new module name
        edit_category: the new category
        edit_comment: the new comment
        edit_start_time: the new start time
        edit_stop_time: the new stop time
        edit_module_stop: the new module stop time
        '''
        s,m,e = self.add_new_entry(edit_semester_name, edit_module_name, edit_category, edit_comment, edit_start_time, edit_stop_time)
        m.start = edit_module_start
        if edit_module_stop is not None:
            m.stop = edit_module_stop
        
        self.remove_entry(semester, module, entry)

    def generate_chart(self, scope, chart_type=ChartType.PIE):
        '''generates a chart

        scope: the data (study, Semester, Module) which will be printed
        chart_type: the type of the chart

        returns: the chart
        '''

        data = self._get_chart_data(scope, chart_type)
        chart = ChartFactory.create_chart(chart_type, *data)
        return chart

    def _get_chart_data(self, scope, chart_tpe=ChartType.PIE):
        '''gets the data for a chart

        scope: the data (study, Semester, Module) which will be printed
        chart_tpe: the type of the chart

        returns: the data for the chart
        '''

        if chart_tpe == ChartType.PIE:
            return self._get_pie_chart_data(scope)
        elif chart_tpe == ChartType.BURNDOWN:
            return self._get_burndown_chart_data(scope)
    
    def _get_pie_chart_data(self, scope):
        '''gets the data for a pie chart
        
        scope: the data (study, Semester, Module) which will be printed

        returns: the names and values for the chart
        '''

        durations, _ = scope.get_durations()
        names = [dur.get('Name')for dur in durations]
        values = [dur.get('Duration').total_seconds() for dur in durations]
        return names, values

    def _get_burndown_chart_data(self, scope):
        '''gets the data for a burndown chart

        scope: the data (study, Semester, Module) which will be printed

        returns: the stop times, values, total work and planned end
        '''

        if isinstance(scope, Study):
            total_work = scope.ECTS
            planned_end = scope.plannedEnd
            modules = [mod for sem in scope.semesters for mod in sem.modules]
        elif isinstance(scope, Semester):
            total_work = scope.ECTS if scope.ECTS != 0 else sum(mod.ECTS for mod in scope.modules)
            planned_end = scope.plannedEnd if scope.plannedEnd else 0
            modules = scope.modules
        elif isinstance(scope, Module):
            return

        start = []
        end = []
        stop_times_values = []

        for mod in modules:
            start.append(mod.start)
            end.append(mod.plannedEnd)
            if mod.stop is not None:
                stop_times_values.append((mod.stop, mod.ECTS))

        if planned_end == 0:
            planned_end = max(end)

        start.sort()
        stop_times_values.append((start[0], 0))

        # Sort the list of tuples
        stop_times_values.sort()

        # Extract the sorted stop_times and values
        stop_times, values = zip(*stop_times_values)

        return stop_times, values, total_work, planned_end
    
    def update_study(self, ECTS, hoursPerECTS, plannedEnd):
        '''updates the study

        ECTS: the new ECTS
        hoursPerECTS: the new hours per ECTS
        plannedEnd: the new planned end
        '''
        self._study.ECTS = ECTS
        self._study.hoursPerECTS = hoursPerECTS
        self._study.plannedEnd = plannedEnd
        if self.on_treeview_update:
            self.on_treeview_update()

    def create_new_study(self, ECTS, hoursPerECTS, plannedEnd):
        '''creates a new study

        ECTS: the new ECTS
        hoursPerECTS: the new hours per ECTS
        plannedEnd: the new planned end
        '''
        self._study = Study(ECTS, hoursPerECTS, plannedEnd)
        if self.on_treeview_update:
            self.on_treeview_update()
        
        return self._study
    
    def get_study_parameters(self):
        '''gets the study parameters

        returns: the ECTS, hours per ECTS and the planned end
        '''
        return self._study.ECTS, self._study.hoursPerECTS, self._study.plannedEnd
    
    def update_semester(self, semester_id, field, new_value):
        semester = next((sem for sem in self.get_semesters() if sem.id == semester_id), None)
        if semester:
            if field == "ECTS":
                try:
                    semester.ECTS = int(new_value)
                except ValueError:
                    raise ValueError("Invalid ECTS value! Enter a positive integer.")
            elif field == "plannedEnd":
                formats = ["%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d", "%m/%d/%Y"]
                for fmt in formats:
                    try:
                        semester.plannedEnd = datetime.datetime.strptime(new_value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError("Invalid date format! Enter the plannedEnd in one of the following formats: " + '; '.join(formats).replace('%',''))
            return semester
        else:
            raise ValueError("Semester not found")
    
    def export_to_json(self, filename):
        '''exports the study to a json file

        sets the last filename
        filename: the name of the file
        '''
        if filename is None:
            filename = self.settings.get("last_filename")
        with open(filename, 'w') as file:
            json.dump(self._study.to_json(), file, indent=4)
        self.settings.set("last_filename", filename)
        print(f"Data was successfully written to {filename}.")

    def import_from_json(self, filename):
        '''imports the study from a json file

        uses the last filename if no filename is given
        filename: the name of the file
        '''
        if filename is None:
            filename = self.settings.get("last_filename")
        if filename and os.path.exists(filename):
            with open(filename, 'r') as file:
                data = json.load(file)
            self._study = Study.from_json(data)
            self.settings.set("last_filename", filename)
            print(f"Data was successfully read from {filename}.")
        else:
            raise FileNotFoundError(f"File {filename} not found.")