import unittest
import model
import datetime
from time import sleep


class UnitTestEntry(unittest.TestCase):
    def test_init(self):
        '''
        test the Entry constructor
        '''
        # Test without arguments
        with self.assertRaises(TypeError):
            e = model.Entry()

    def test_equal(self):
        '''
        Test the __eq__ check
        '''
        e = model.Entry("a")
        e1 = model.Entry("b")
        sleep(1)
        e2 = model.Entry("a")
        x = model.Module(name="")

        self.assertEqual(
            e == x, False, "Comparing to wrong Type did not return NotImplemented")
        self.assertEqual(
            e == e, True, "Comparison between same instance did not return equality")
        self.assertEqual(
            e == e1, False, "Comparison of different objects returned equality")
        self.assertEqual(
            e == e2, False, "Comparison of different objects returned equality")

    def test_stop(self):
        '''
        test the Entry.stop() method
        hard coded timeout is used
        '''
        timeout = 10
        e = model.Entry("")
        sleep(timeout)
        duration = e.stop()

        expDelta = datetime.timedelta(seconds=timeout)

        self.assertAlmostEqual(first=expDelta,
                               second=duration,
                               msg="Duration of entry deviated too much", delta=datetime.timedelta(seconds=0.1))

    def test_get_duration(self):
        '''
        test the Entry.get_duration() method
        hard coded timeout is used
        '''
        timeout = 10
        e = model.Entry("")
        sleep(timeout)
        duration_before_stop = e.get_duration()
        sleep(timeout)
        duration = e.stop()

        # Test if duration is correct before entry was stopped
        self.assertAlmostEqual(
            first=duration_before_stop,
            second=datetime.timedelta(seconds=timeout),
            msg="Duration before entry was stopped deviated too much",
            delta=datetime.timedelta(seconds=0.1))

        # Test if duration is correct after entry was stopped
        self.assertAlmostEqual(
            first=e.get_duration(),
            second=datetime.timedelta(seconds=2*timeout),
            msg="Duration after entry was stopped deviated too much",
            delta=datetime.timedelta(seconds=0.1))

        # Test if stop() and get_duration() return same duration
        self.assertEqual(first=duration, second=e.get_duration(),
                         msg="duration returned by stop()\
                         and get_duration() are not equal")

        # Test if duration is constant after stop() was called
        sleep(5*timeout)
        self.assertEqual(first=duration, second=e.get_duration(),
                         msg="duration changed after stop()")

    def test_to_json(self):
        '''test the to_json method of Entry'''
        e = model.Entry("test_category", "test_comment")
        e.stop()
        json_data = e.to_json()
        self.assertEqual(e.id, json_data["id"], "ID does not match")
        self.assertEqual(
            e.category, json_data["category"], "Category does not match")
        self.assertEqual(
            e.comment, json_data["comment"], "Comment does not match")
        self.assertEqual(e.start_time.isoformat(),
                         json_data["start_time"], "Start time does not match")
        self.assertEqual(e.stop_time.isoformat(),
                         json_data["stop_time"], "Stop time does not match")

    def test_from_json(self):
        '''test the from_json method of Entry'''
        e = model.Entry("test_category", "test_comment")
        e.stop()
        json_data = e.to_json()
        e_from_json = model.Entry.from_json(json_data)
        self.assertEqual(e.id, e_from_json.id, "ID does not match")
        self.assertEqual(e.category, e_from_json.category,
                         "Category does not match")
        self.assertEqual(e.comment, e_from_json.comment,
                         "Comment does not match")
        self.assertEqual(e.start_time, e_from_json.start_time,
                         "Start time does not match")
        self.assertEqual(e.stop_time, e_from_json.stop_time,
                         "Stop time does not match")


class UnitTestModule(unittest.TestCase):
    def test_init(self):
        '''test the module constructor'''

        # test with missing argument
        with self.assertRaises(TypeError):
            mod = model.Module()

        # test if start and planned end are set correctly
        mod = model.Module(name="test")
        start = datetime.datetime.now()
        self.assertAlmostEqual(first=start, second=mod.start,
                               msg="start time of the module\
                                 was not set correctly",
                               delta=datetime.timedelta(seconds=1))

        self.assertEqual(first=mod.plannedEnd,
                         second=mod.start,
                         msg="planned end was net set correctly")

        self.assertTrue(len(mod.entries) == 0, msg="entry list is not empty")

    def test_equal(self):
        '''
        Test the __eq__ check
        '''
        m = model.Module("a")
        m1 = model.Module("b")
        sleep(1)
        m2 = model.Module("a")
        e = model.Entry("")

        self.assertEqual(
            m == e, False, "Comparing to wrong Type did not return NotImplemented")
        self.assertEqual(
            m == m, True, "Comparison between same instance did not return equality")
        self.assertEqual(
            m == m1, False, "Comparison of different objects returned equality")
        self.assertEqual(
            m == m2, False, "Comparison of different objects returned equality")

    def test_start_module(self):
        '''test the start_module function'''

        mod = model.Module("test")

        # test with missing argument
        with self.assertRaises(TypeError):
            mod.start_module()

        # test for different durations
        values = [0, 1, 100]
        for n_weeks in values:
            mod.start_module(duration=n_weeks)
            self.assertEqual(
                first=mod.plannedEnd,
                second=mod.start + datetime.timedelta(weeks=n_weeks),
                msg="Planned end was not stet to start + duration")

    def test_set_plannedEnd(self):
        '''test the set_plannedEnd function'''
        mod = model.Module("test")

        values = [0, 1, 100]
        for n_weeks in values:
            mod.set_plannedEnd(duration=n_weeks)
            self.assertEqual(
                first=mod.plannedEnd,
                second=mod.start + datetime.timedelta(weeks=n_weeks),
                msg="Planned end was not stet to start + duration")

    def test_addEntry(self):
        ''' tests if an entry is added correctly'''

        mod = model.Module("test")

        # test with missing argument
        with self.assertRaises(TypeError):
            mod.add_entry()

        self.assertTrue(len(mod.entries) == 0, msg="entry list is not empty")

        # test to add an entry
        start_time = datetime.datetime.now()
        entry = mod.add_entry(category="")
        self.assertTrue(len(mod.entries) == 1, msg="wrong len of entry list")

        self.assertAlmostEqual(first=start_time, second=entry.start_time,
                               msg="Added entry was not started correctly",
                               delta=datetime.timedelta(seconds=0.1))

    def test_removeEntry(self):
        ''' tests if an entry is removed correctly'''

        mod = model.Module("test")

        # test with missing argument
        with self.assertRaises(TypeError):
            mod.remove_entry()

        # generate data
        e = mod.add_entry(category="")
        e1 = mod.add_entry(category="a")

        # remove entry
        mod.remove_entry(e)
        self.assertEqual(len(mod.entries), 1,
                         "Wrong length of list after removing entry")

        # remove non existing entry
        with self.assertRaises(ValueError):
            mod.remove_entry(e)

        mod.remove_entry(e1)
        self.assertEqual(len(mod.entries), 0,
                         "Wrong length of list after removing entry")

    def test_get_durations(self):
        ''' tests if the durations are returned correct'''

        mod = model.Module("test")

        data_categories = ["a", "b", "c", "d", "e", "f"]
        data_durations = [1, 10, 100]

        # create data and reference
        ref_sum = 0
        ref_list = []
        for cat in data_categories:
            cat_dur = 0
            for dur in data_durations:
                # create data
                e = mod.add_entry(category=cat)
                e.stop_time = e.start_time + datetime.timedelta(seconds=dur)
                cat_dur += dur

            # create reference
            ref_sum += cat_dur
            ref_list.append({"Name": cat,
                             "Duration": datetime.timedelta(seconds=cat_dur)})

        durations, sum = mod.get_durations()

        self.assertEqual(first=datetime.timedelta(seconds=ref_sum), second=sum,
                         msg="Total duration was not calculated correctly")

        self.assertListEqual(list1=ref_list, list2=durations,
                             msg="Lists are not equal")

    def test_get_categories(self):
        ''' tests if the categories are returned correct'''

        mod = model.Module("test")

        data_categories = ["a", "b", "c", "d", "e", "f"]
        data_durations = [1, 10, 100]

        # create data
        for cat in data_categories:
            for dur in data_durations:
                e = mod.add_entry(category=cat)
                e.stop_time = e.start_time + datetime.timedelta(seconds=dur)

        categories = mod.get_categories()
        self.assertListEqual(list1=data_categories, list2=categories,
                             msg="List of categories is wrong")

    def test_to_json(self):
        '''test the to_json method of Module'''
        mod = model.Module("test_module")
        entry = mod.add_entry("test_category", "test_comment")
        entry.stop()
        json_data = mod.to_json()
        self.assertEqual(mod.id, json_data["id"], "ID does not match")
        self.assertEqual(mod.name, json_data["name"], "Name does not match")
        self.assertEqual(mod.ECTS, json_data["ECTS"], "ECTS does not match")
        self.assertEqual(mod.start.isoformat(),
                         json_data["start"], "Start time does not match")
        self.assertEqual(mod.plannedEnd.isoformat(),
                         json_data["plannedEnd"], "Planned end does not match")
        self.assertEqual(len(mod.entries), len(
            json_data["entries"]), "Entries length does not match")

    def test_from_json(self):
        '''test the from_json method of Module'''
        mod = model.Module("test_module")
        entry = mod.add_entry("test_category", "test_comment")
        entry.stop()
        json_data = mod.to_json()
        mod_from_json = model.Module.from_json(json_data)
        self.assertEqual(mod.id, mod_from_json.id, "ID does not match")
        self.assertEqual(mod.name, mod_from_json.name, "Name does not match")
        self.assertEqual(mod.ECTS, mod_from_json.ECTS, "ECTS does not match")
        self.assertEqual(mod.start, mod_from_json.start,
                         "Start time does not match")
        self.assertEqual(mod.plannedEnd, mod_from_json.plannedEnd,
                         "Planned end does not match")
        self.assertEqual(len(mod.entries), len(
            mod_from_json.entries), "Entries length does not match")


class UnitTestSemester(unittest.TestCase):
    def test_init(self):
        '''tests constructor of class Semester'''
        # test for missing argument
        with self.assertRaises(TypeError):
            sem = model.Semester()

        sem = model.Semester(name="test")
        self.assertTrue(len(sem.modules) == 0, msg="entry list is not empty")

    def test_equal(self):
        '''
        Test the __eq__ check
        '''
        s = model.Semester("a")
        s1 = model.Semester("b")
        sleep(1)
        s2 = model.Semester("a")
        e = model.Entry("")

        self.assertEqual(
            s == e, False, "Comparing to wrong Type did not return NotImplemented")
        self.assertEqual(
            s == s, True, "Comparison between same instance did not return equality")
        self.assertEqual(
            s == s1, False, "Comparison of different objects returned equality")
        self.assertEqual(
            s == s2, False, "Comparison of different objects returned equality")

    def test_add_module(self):
        '''tests if modules can be added to semester'''
        sem = model.Semester("semester")
        mod = model.Module("module")

        # check if list is empty
        self.assertEqual(first=0, second=len(sem.modules),
                         msg="list of modules is not empty")

        # test if adding a module works
        sem.add_module(mod)
        self.assertEqual(first=1, second=len(sem.modules),
                         msg="list of modules is not empty")

        # try to add wrong type
        entry = model.Entry(category="cat")
        with self.assertRaises(TypeError):
            sem.add_module(entry)

        self.assertEqual(first=1, second=len(sem.modules),
                         msg="list of modules is not empty")

    def test_add_entry(self):
        '''tests if entries are created correctly
        and are added to the module
        '''
        sem = model.Semester("semester")

        # wrong arguments
        with self.assertRaises(TypeError):
            sem.add_entry(moduleName="mod")
        with self.assertRaises(TypeError):
            sem.add_entry(category="cat")
        with self.assertRaises(TypeError):
            sem.add_entry()

        # check if module is generated and entry is added
        entry = sem.add_entry(moduleName="mod", category="cat")
        self.assertEqual(first=1, second=len(sem.modules),
                         msg="list of modules has wrong length")
        self.assertEqual(first=1, second=len(sem.modules[0].entries),
                         msg="list of entries in mod has wrong length")

        # check if existing module is used and entry is added
        entry = sem.add_entry(moduleName="mod", category="cat")
        self.assertEqual(first=1, second=len(sem.modules),
                         msg="list of modules has wrong length")
        self.assertEqual(first=2, second=len(sem.modules[0].entries),
                         msg="list of entries in mod has wrong length")

    def test_remove_entry(self):
        '''tests if entries are removed correctly
        and if modules without entries are deleted
        '''
        sem = model.Semester("semester")

        # wrong arguments
        with self.assertRaises(TypeError):
            sem.remove_entry(moduleName="mod")
        with self.assertRaises(TypeError):
            sem.remove_entry(category="cat")
        with self.assertRaises(TypeError):
            sem.remove_entry()

        # generate data
        mod, entry = sem.add_entry(moduleName="mod", category="cat")
        _, entry2 = sem.add_entry(
            moduleName="mod", category="cat", comment="a")
        mod2, entry3 = sem.add_entry(moduleName="mod2", category="cat")

        # remove existing entry
        sem.remove_entry(mod, entry)
        self.assertEqual(len(sem.modules), 2,
                         "Wrong length of module list after removing an entry")

        self.assertEqual(len(mod.entries), 1,
                         "Wrong length of entry list after removing entry \
                            from module")

        # remove non existing entry
        with self.assertRaises(ValueError):
            sem.remove_entry(mod, entry)

        # remove last entry of module
        sem.remove_entry(mod, entry2)
        self.assertEqual(len(sem.modules), 1,
                         "Wrong length of module list after removing an entry")

    def test_get_durations(self):
        '''test if correct module durations are returned'''

        sem = model.Semester("semester")
        data_modules = ["mod1", "mod2"]
        data_categories = ["a", "b", "c", "d", "e", "f"]
        data_durations = [1, 10, 100]

        # generate data and reference
        ref_list = []
        ref_sum = 0
        for mod in data_modules:
            mod_duration = 0
            for cat in data_categories:
                for dur in data_durations:
                    _, entry = sem.add_entry(moduleName=mod, category=cat)
                    entry.stop_time = entry.start_time \
                        + datetime.timedelta(seconds=dur)
                    mod_duration += dur
            ref_list.append({"Name": mod,
                             "Duration": datetime.timedelta(
                                 seconds=mod_duration)})
            ref_sum += mod_duration

        durations, sum = sem.get_durations()
        self.assertEqual(first=datetime.timedelta(seconds=ref_sum), second=sum,
                         msg="Total duration was not calculated correctly")

        self.assertListEqual(list1=ref_list, list2=durations,
                             msg="Lists are not equal")

    def test_get_module(self):
        '''test if a module can be searched by name'''

        sem = model.Semester("sem")

        with self.assertRaises(TypeError):
            sem.get_module()

        # generate data
        module_data = ["mod1", "mod2", "mod3"]
        for mod_name in module_data:
            mod = model.Module(name=mod_name)
            sem.add_module(mod)

        for mod_name in module_data:
            mod = sem.get_module(mod_name)
            self.assertEqual(first=mod_name, second=mod.name,
                             msg="found module has wrong name")

        mod = sem.get_module("invalidName")
        self.assertIsNone(obj=mod,
                          msg="searching with invalidName returned module")

    def test_get_categories(self):
        '''test if all used categories are returned'''

        sem = model.Semester("sem")

        # generate data
        module_data = ["mod1", "mod11", "mod2"]
        for mod_name in module_data:
            mod = model.Module(name=mod_name)
            mod.add_entry("cat_"+mod_name)
            sem.add_module(mod)

        ref_lst = ["cat_"+mod_name for mod_name in module_data]
        mod_lst = sem.get_categories()
        self.assertEqual(ref_lst, mod_lst, "sem.get_categories did not return \
                         expected list")

        mod_lst = sem.get_categories(modName="mod")
        self.assertEqual(ref_lst, mod_lst, "sem.get_categories did not return \
                         expected list")

        ref_lst = ["cat_mod1", "cat_mod11"]
        mod_lst = sem.get_categories(modName="mod1")
        self.assertEqual(ref_lst, mod_lst, "sem.get_categories did not return \
                         expected list")

    def test_to_json(self):
        '''test the to_json method of Semester'''
        sem = model.Semester("test_semester")
        mod = sem.add_module(model.Module("test_module"))
        json_data = sem.to_json()
        self.assertEqual(sem.id, json_data["id"], "ID does not match")
        self.assertEqual(sem.name, json_data["name"], "Name does not match")
        self.assertEqual(sem.ECTS, json_data["ECTS"], "ECTS does not match")
        self.assertEqual(sem.plannedEnd.isoformat() if sem.plannedEnd else None,
                         json_data["plannedEnd"], "Planned end does not match")
        self.assertEqual(len(sem.modules), len(
            json_data["modules"]), "Modules length does not match")

    def test_from_json(self):
        '''test the from_json method of Semester'''
        sem = model.Semester("test_semester")
        mod = sem.add_module(model.Module("test_module"))
        json_data = sem.to_json()
        sem_from_json = model.Semester.from_json(json_data)
        self.assertEqual(sem.id, sem_from_json.id, "ID does not match")
        self.assertEqual(sem.name, sem_from_json.name, "Name does not match")
        self.assertEqual(sem.ECTS, sem_from_json.ECTS, "ECTS does not match")
        self.assertEqual(sem.plannedEnd, sem_from_json.plannedEnd,
                         "Planned end does not match")
        self.assertEqual(len(sem.modules), len(
            sem_from_json.modules), "Modules length does not match")


class UnitTestStudy(unittest.TestCase):
    def test_init(self):
        '''tests the constructor of Study'''

        # test call with wrong type
        with self.assertRaises(TypeError):
            model.Study()

        with self.assertRaises(TypeError):
            model.Study(ECTS=5)

        with self.assertRaises(TypeError):
            model.Study(hoursPerECTS=30)

        with self.assertRaises(TypeError):
            model.Study(plannedEnd=datetime.datetime.now())

    def test_add_semester(self):
        '''tests if adding semesters works'''

        study = model.Study(
            ECTS=180, hoursPerECTS=30, plannedEnd=datetime.datetime.now())

        # wrong arguments
        with self.assertRaises(TypeError):
            study.add_semester()

        with self.assertRaises(TypeError):
            study.add_semester(semester="")

        self.assertEqual(first=0, second=len(study.semesters),
                         msg="list of semesters is not empty")

        # test if adding a semester works
        sem = model.Semester(name="semester")
        study.add_semester(sem)

        self.assertEqual(first=1, second=len(study.semesters),
                         msg="wrong length of list of semesters")

    def test_add_entry(self):
        '''tests if adding an entry works'''

        study = model.Study(
            ECTS=180, hoursPerECTS=30, plannedEnd=datetime.datetime.now())

        # wrong arguments
        with self.assertRaises(TypeError):
            study.add_entry()
        with self.assertRaises(TypeError):
            study.add_entry(semesterName="")
        with self.assertRaises(TypeError):
            study.add_entry(semesterName="", moduleName="")
        with self.assertRaises(TypeError):
            study.add_entry(moduleName="", category="")

        # check if semester is generated and module and entry are added
        entry = study.add_entry(semesterName="sem", moduleName="mod",
                                category="cat")
        self.assertEqual(first=1, second=len(study.semesters),
                         msg="list of semesters has wrong length")
        self.assertEqual(first=1, second=len(study.semesters[0].modules),
                         msg="list of moduels in sem has wrong length")
        self.assertEqual(first=1,
                         second=len(study.semesters[0].modules[0].entries),
                         msg="list of entries in mod has wrong length")

        # check if existing semester is used and module and entry are added
        entry = study.add_entry(semesterName="sem", moduleName="mod1",
                                category="cat")
        self.assertEqual(first=1, second=len(study.semesters),
                         msg="list of semesters has wrong length")
        self.assertEqual(first=2, second=len(study.semesters[0].modules),
                         msg="list of modules in sem has wrong length")
        self.assertEqual(first=1,
                         second=len(study.semesters[0].modules[1].entries),
                         msg="list of entries in mod has wrong length")

    def test_remove_entry(self):
        '''tests if removing an entry works'''

        study = model.Study(
            ECTS=180, hoursPerECTS=30, plannedEnd=datetime.datetime.now())

        # wrong arguments
        with self.assertRaises(TypeError):
            study.remove_entry()
        with self.assertRaises(TypeError):
            study.remove_entry(semesterName="")
        with self.assertRaises(TypeError):
            study.remove_entry(semesterName="", moduleName="")
        with self.assertRaises(TypeError):
            study.remove_entry(moduleName="", category="")

        # generate data
        sem, mod, entry = study.add_entry(semesterName="sem", moduleName="mod",
                                          category="cat")
        _, mod1, entry1 = study.add_entry(semesterName="sem", moduleName="mod1",
                                          category="cat")
        sem2, _, entry2 = study.add_entry(semesterName="sem2", moduleName="mod1",
                                          category="cat")

        study.remove_entry(sem, mod, entry)
        self.assertEqual(len(study.semesters), 2,
                         "Wrong amount of semesters after removing entry")
        self.assertEqual(len(sem.modules), 1,
                         "Wrong length of module list after removing entry")

        # remove non existing entry
        with self.assertRaises(ValueError):
            study.remove_entry(sem, mod, entry)

        study.remove_entry(sem, mod1, entry1)
        self.assertEqual(len(study.semesters), 1,
                         "Wrong amount of semesters after removing entry")

    def test_get_durations(self):
        '''test if correct semester durations are returned'''

        study = model.Study(
            ECTS=180, hoursPerECTS=30, plannedEnd=datetime.datetime.now())
        data_semesters = ["sem1", "sem2"]
        data_modules = ["mod1", "mod2"]
        data_categories = ["a", "b", "c", "d", "e", "f"]
        data_durations = [1, 10, 100]

        # generate data and reference
        ref_list = []
        ref_sum = 0
        for sem in data_semesters:
            sem_duration = 0
            for mod in data_modules:
                mod_duration = 0
                for cat in data_categories:
                    for dur in data_durations:
                        _, _, entry = study.add_entry(semesterName=sem,
                                                      moduleName=mod, category=cat)
                        entry.stop_time = entry.start_time \
                            + datetime.timedelta(seconds=dur)
                        mod_duration += dur

                sem_duration += mod_duration

            ref_list.append({"Name": sem,
                            "Duration": datetime.timedelta(
                                seconds=sem_duration)})
            ref_sum += sem_duration

        # check total duration and list
        durations, sum = study.get_durations()
        self.assertEqual(first=datetime.timedelta(seconds=ref_sum), second=sum,
                         msg="Total duration was not calculated correctly")

        self.assertListEqual(list1=ref_list, list2=durations,
                             msg="Lists are not equal")

    def test_get_semester(self):
        '''test if a semester can be searched by name'''

        study = model.Study(
            ECTS=180, hoursPerECTS=30, plannedEnd=datetime.datetime.now())

        with self.assertRaises(TypeError):
            study.get_semester()

        # generate data
        semester_data = ["sem1", "sem2", "sem3"]
        for sem_name in semester_data:
            sem = model.Semester(name=sem_name)
            study.add_semester(sem)

        # test if semesters can be found
        for sem_name in semester_data:
            sem = study.get_semester(sem_name)
            self.assertEqual(first=sem_name, second=sem.name,
                             msg="found module has wrong name")

        sem = study.get_semester("invalidName")
        self.assertIsNone(obj=sem,
                          msg="searching with invalidName returned module")

    def test_get_modules(self):
        '''test if all used modules are returned'''
        study = model.Study(180, 30, datetime.datetime.now())

        # generate data
        ref_lst = []
        ref_lst2 = []
        sem_data = ["sem1", "sem11", "sem2"]
        for sem_name in sem_data:
            sem = model.Semester(name=sem_name)
            m, _ = sem.add_entry(moduleName="mod_"+sem_name, category="")
            study.add_semester(sem)
            ref_lst.append(m)
            if ("sem1" in sem_name):
                ref_lst2.append(m)

        sem_lst = study.get_modules()
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

        sem_lst = study.get_modules(semName="sem")
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

        sem_lst = study.get_modules(semName="sem1")
        self.assertEqual(ref_lst2, sem_lst, "study.get_modules did not return \
                         expected list")

    def test_get_categories(self):
        '''test if all used modules are returned'''
        study = model.Study(180, 30, datetime.datetime.now())

        # generate data
        sem_data = ["sem1", "sem11", "sem2"]
        mod_data = ["mod1", "mod11", "mod2"]
        ref_lst = []
        for sem_name in sem_data:
            for mod_name in mod_data:
                study.add_entry(semesterName=sem_name, moduleName=mod_name,
                                category="cat_"+mod_name+"_"+sem_name)
                ref_lst.append("cat_"+mod_name+"_"+sem_name)

        sem_lst = study.get_categories()
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

        sem_lst = study.get_categories(semName="sem")
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

        ref_lst = []
        for sem_name in sem_data:
            if "sem1" in sem_name:
                for mod_name in mod_data:
                    ref_lst.append("cat_"+mod_name+"_"+sem_name)

        sem_lst = study.get_categories(semName="sem1")
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

        ref_lst = []
        for sem_name in sem_data:
            if "sem1" in sem_name:
                for mod_name in mod_data:
                    if "mod1" in mod_name:
                        ref_lst.append("cat_"+mod_name+"_"+sem_name)

        sem_lst = study.get_categories(semName="sem1", modName="mod1")
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

    def test_set_last_information(self):
        '''test if setting the last information works'''
        study = model.Study(180, 30, datetime.datetime.now())

        sem, mod, entry = study.add_entry(
            "semester", "module", "category", "comment")
        with self.assertRaises(TypeError):
            study.set_last_information("a", "b", "c")
        with self.assertRaises(TypeError):
            study.set_last_information(mod, mod, entry)
        with self.assertRaises(TypeError):
            study.set_last_information(sem, sem, entry)
        with self.assertRaises(TypeError):
            study.set_last_information(sem, mod, mod)

        study.set_last_information(sem, mod, entry)
        self.assertEqual(sem, study.last_semester,
                         "last semester was not set correctly")
        self.assertEqual(mod, study.last_module,
                         "last module was not set correctly")
        self.assertEqual(entry, study.last_entry,
                         "last entry was not set correctly")

    def test_get_last_information(self):
        '''test if reading the last information works'''
        study = model.Study(180, 30, datetime.datetime.now())

        sem, mod, entry = study.add_entry(
            "semester", "module", "category", "comment")
        s, m, e = study.get_last_information()

        self.assertIsNone(s, "last semester was not set correctly")
        self.assertIsNone(m, "last module was not set correctly")
        self.assertIsNone(e, "last entry was not set correctly")

        study.set_last_information(sem, mod, entry)
        s, m, e = study.get_last_information()

        self.assertEqual(sem, s, "last semester was not set correctly")
        self.assertEqual(mod, m, "last module was not set correctly")
        self.assertEqual(entry, e, "last entry was not set correctly")

    def test_to_json(self):
        '''test the to_json method of Study'''
        study = model.Study(180, 30, datetime.datetime.now())
        sem, mod, entry = study.add_entry(
            "test_semester", "test_module", "test_category", "test_comment")
        study.set_last_information(sem, mod, entry)
        json_data = study.to_json()
        self.assertEqual(study.ECTS, json_data["ECTS"], "ECTS does not match")
        self.assertEqual(
            study.hoursPerECTS, json_data["hoursPerECTS"], "Hours per ECTS does not match")
        self.assertEqual(study.plannedEnd.isoformat(),
                         json_data["plannedEnd"], "Planned end does not match")
        self.assertEqual(len(study.semesters), len(
            json_data["semesters"]), "Semesters length does not match")
        self.assertEqual(study.last_semester.to_json(
        ), json_data["last_semester"], "Last semester does not match")
        self.assertEqual(study.last_module.to_json(),
                         json_data["last_module"], "Last module does not match")
        self.assertEqual(study.last_entry.to_json(),
                         json_data["last_entry"], "Last entry does not match")

    def test_from_json(self):
        '''test the from_json method of Study'''
        study = model.Study(180, 30, datetime.datetime.now())
        sem, mod, entry = study.add_entry(
            "test_semester", "test_module", "test_category", "test_comment")
        study.set_last_information(sem, mod, entry)
        json_data = study.to_json()
        study_from_json = model.Study.from_json(json_data)
        self.assertEqual(study.ECTS, study_from_json.ECTS,
                         "ECTS does not match")
        self.assertEqual(
            study.hoursPerECTS, study_from_json.hoursPerECTS, "Hours per ECTS does not match")
        self.assertEqual(
            study.plannedEnd, study_from_json.plannedEnd, "Planned end does not match")
        self.assertEqual(len(study.semesters), len(
            study_from_json.semesters), "Semesters length does not match")
        self.assertEqual(study.last_semester.id,
                         study_from_json.last_semester.id, "Last semester does not match")
        self.assertEqual(
            study.last_module.id, study_from_json.last_module.id, "Last module does not match")
        self.assertEqual(
            study.last_entry.id, study_from_json.last_entry.id, "Last entry does not match")


if __name__ == '__main__':
    unittest.main()
