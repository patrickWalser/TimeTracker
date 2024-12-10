import uuid
import datetime

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

    def to_json(self):
        '''converts the entry to a json object'''
        return {
            "id": self.id,
            "category": self.category,
            "comment": self.comment,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "stop_time": self.stop_time.isoformat() if self.stop_time else None
        }

    @classmethod
    def from_json(cls, data):
        '''creates an Entry object from a json object'''
        entry =  cls(
            category=data["category"],
            comment=data["comment"],
        )
        entry.id=data["id"]
        entry.start_time=datetime.datetime.fromisoformat(data["start_time"]) if data["start_time"] else None
        entry.stop_time=datetime.datetime.fromisoformat(data["stop_time"]) if data["stop_time"] else None
        return entry


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
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "ECTS": self.ECTS,
            "start": self.start.isoformat() if self.start else None,
            "plannedEnd": self.plannedEnd.isoformat() if self.plannedEnd else None,
            "entries": [entry.to_json() for entry in self.entries]
        }

    @classmethod
    def from_json(cls, data):
        module = cls(
            name=data["name"],
            ECTS=data["ECTS"],
        )
        module.entries = [Entry.from_json(entry) for entry in data["entries"]]
        module.id=data["id"]
        module.start=datetime.datetime.fromisoformat(data["start"]) if data["start"] else None
        module.plannedEnd=datetime.datetime.fromisoformat(data["plannedEnd"]) if data["plannedEnd"] else None
        return module


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
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "ECTS": self.ECTS,
            "plannedEnd": self.plannedEnd.isoformat() if self.plannedEnd else None,
            "modules": [module.to_json() for module in self.modules]
        }

    @classmethod
    def from_json(cls, data):
        semester = cls(
            name=data["name"],
            ECTS=data["ECTS"],
            plannedEnd=datetime.datetime.fromisoformat(data["plannedEnd"]) if data["plannedEnd"] else None
        )
        semester.id=data["id"]
        semester.modules = [Module.from_json(module) for module in data["modules"]]
        return semester


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

        self.last_semester = None
        self.last_module = None
        self.last_entry = None

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
                mod_lst.extend(s.modules)
        return mod_lst

    def get_categories(self, semName="", modName=""):
        '''get all categories of the semesters / modules

        gets semesters and modules containing the semName/modName
        and returns all categories
        semName: name which must be contained by the semesters
        modName: name which must be contained by the modules
        returns list of categories'''
        cat_lst = []
        mod_lst = self.get_modules(semName)
        
        for mod in mod_lst:
            if modName in mod.name:
                cat_lst.extend(mod.get_categories())
        tmp_dict = dict.fromkeys(cat_lst)
        return list(tmp_dict)

    def set_last_information(self, semester, module, entry):
        '''sets the last information

        semester: the last tracked semester
        module: the last tracked module
        entry: the last tracked entry
        '''
        if not isinstance(semester, Semester) \
                or not isinstance(module, Module) or not isinstance(entry, Entry):
            raise TypeError()

        self.last_semester = semester
        self.last_module = module
        self.last_entry = entry

    def get_last_information(self):
        '''get the information about the last tracking'''
        return self.last_semester, self.last_module, self.last_entry

    def to_json(self):
        return {
            "ECTS": self.ECTS,
            "hoursPerECTS": self.hoursPerECTS,
            "plannedEnd": self.plannedEnd.isoformat() if self.plannedEnd else None,
            "semesters": [semester.to_json() for semester in self.semesters],
            "last_semester": self.last_semester.to_json() if self.last_semester else None,
            "last_module": self.last_module.to_json() if self.last_module else None,
            "last_entry": self.last_entry.to_json() if self.last_entry else None
        }

    @classmethod
    def from_json(cls, data):
        study = cls(
            ECTS=data["ECTS"],
            hoursPerECTS=data["hoursPerECTS"],
            plannedEnd=datetime.datetime.fromisoformat(data["plannedEnd"]) if data["plannedEnd"] else None,
        )
        study.semesters = [Semester.from_json(semester) for semester in data["semesters"]]
        study.last_semester=Semester.from_json(data["last_semester"]) if data["last_semester"] != None else None
        study.last_module=Module.from_json(data["last_module"]) if data["last_module"] != None else None
        study.last_entry=Entry.from_json(data["last_entry"]) if data["last_entry"] != None else None
        return study