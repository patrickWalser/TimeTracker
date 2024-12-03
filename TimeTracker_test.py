import unittest
import TimeTracker
import datetime
from time import sleep


class UnitTestEnry(unittest.TestCase):
    def test_init(self):
        '''
        test the Entry constructor
        '''
        # Test without arguments
        with self.assertRaises(TypeError):
            e = TimeTracker.Entry()

    def test_equal(self):
        '''
        Test the __eq__ check
        '''
        e = TimeTracker.Entry("a")
        e1 = TimeTracker.Entry("b")
        sleep(1)
        e2 = TimeTracker.Entry("a")
        x = TimeTracker.Module(name="")

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
        e = TimeTracker.Entry("")
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
        e = TimeTracker.Entry("")
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


class UnitTestModule(unittest.TestCase):
    def test_init(self):
        '''test the module constructor'''

        # test with missing argument
        with self.assertRaises(TypeError):
            mod = TimeTracker.Module()

        # test if start and planned end are set correctly
        mod = TimeTracker.Module(name="test")
        start = datetime.datetime.now()
        self.assertAlmostEqual(first=start, second=mod.start,
                               msg="start time of the module\
                                 was not set correctly",
                               delta=datetime.timedelta(seconds=1))

        self.assertEqual(first=mod.plannedEnd,
                         second=mod.start + datetime.timedelta(weeks=6),
                         msg="planned end was net set correctly")

        self.assertTrue(len(mod.entries) == 0, msg="entry list is not empty")

    def test_equal(self):
        '''
        Test the __eq__ check
        '''
        m = TimeTracker.Module("a")
        m1 = TimeTracker.Module("b")
        sleep(1)
        m2 = TimeTracker.Module("a")
        e = TimeTracker.Entry("")

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

        mod = TimeTracker.Module("test")

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

    def test_addEntry(self):
        ''' tests if an entry is added correctly'''

        mod = TimeTracker.Module("test")

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

        mod = TimeTracker.Module("test")

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

        mod = TimeTracker.Module("test")

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

        mod = TimeTracker.Module("test")

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


class UnitTestSemester(unittest.TestCase):
    def test_init(self):
        '''tests constructor of class Semester'''
        # test for missing argument
        with self.assertRaises(TypeError):
            sem = TimeTracker.Semester()

        sem = TimeTracker.Semester(name="test")
        self.assertTrue(len(sem.modules) == 0, msg="entry list is not empty")

    def test_equal(self):
        '''
        Test the __eq__ check
        '''
        s = TimeTracker.Semester("a")
        s1 = TimeTracker.Semester("b")
        sleep(1)
        s2 = TimeTracker.Semester("a")
        e = TimeTracker.Entry("")

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
        sem = TimeTracker.Semester("semester")
        mod = TimeTracker.Module("module")

        # check if list is empty
        self.assertEqual(first=0, second=len(sem.modules),
                         msg="list of modules is not empty")

        # test if adding a module works
        sem.add_module(mod)
        self.assertEqual(first=1, second=len(sem.modules),
                         msg="list of modules is not empty")

        # try to add wrong type
        entry = TimeTracker.Entry(category="cat")
        with self.assertRaises(TypeError):
            sem.add_module(entry)

        self.assertEqual(first=1, second=len(sem.modules),
                         msg="list of modules is not empty")

    def test_add_entry(self):
        '''tests if entries are created correctly
        and are added to the module
        '''
        sem = TimeTracker.Semester("semester")

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
        sem = TimeTracker.Semester("semester")

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

        sem = TimeTracker.Semester("semester")
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

        sem = TimeTracker.Semester("sem")

        with self.assertRaises(TypeError):
            sem.get_module()

        # generate data
        module_data = ["mod1", "mod2", "mod3"]
        for mod_name in module_data:
            mod = TimeTracker.Module(name=mod_name)
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

        sem = TimeTracker.Semester("sem")

        # generate data
        module_data = ["mod1", "mod11", "mod2"]
        for mod_name in module_data:
            mod = TimeTracker.Module(name=mod_name)
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


class UnitTestStudy(unittest.TestCase):
    def test_init(self):
        '''tests the constructor of Study'''

        # test call with wrong type
        with self.assertRaises(TypeError):
            TimeTracker.Study()

        with self.assertRaises(TypeError):
            TimeTracker.Study(ECTS=5)

        with self.assertRaises(TypeError):
            TimeTracker.Study(hoursPerECTS=30)

        with self.assertRaises(TypeError):
            TimeTracker.Study(plannedEnd=datetime.datetime.now())

    def test_add_semester(self):
        '''tests if adding semesters works'''

        study = TimeTracker.Study(
            ECTS=180, hoursPerECTS=30, plannedEnd=datetime.datetime.now())

        # wrong arguments
        with self.assertRaises(TypeError):
            study.add_semester()

        with self.assertRaises(TypeError):
            study.add_semester(semester="")

        self.assertEqual(first=0, second=len(study.semesters),
                         msg="list of semesters is not empty")

        # test if adding a semester works
        sem = TimeTracker.Semester(name="semester")
        study.add_semester(sem)

        self.assertEqual(first=1, second=len(study.semesters),
                         msg="wrong length of list of semesters")

    def test_add_entry(self):
        '''tests if adding an entry works'''

        study = TimeTracker.Study(
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

        study = TimeTracker.Study(
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

        study = TimeTracker.Study(
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

        study = TimeTracker.Study(
            ECTS=180, hoursPerECTS=30, plannedEnd=datetime.datetime.now())

        with self.assertRaises(TypeError):
            study.get_semester()

        # generate data
        semester_data = ["sem1", "sem2", "sem3"]
        for sem_name in semester_data:
            sem = TimeTracker.Semester(name=sem_name)
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
        study = TimeTracker.Study(180, 30, datetime.datetime.now())

        # generate data
        sem_data = ["sem1", "sem11", "sem2"]
        for sem_name in sem_data:
            sem = TimeTracker.Semester(name=sem_name)
            sem.add_entry(moduleName="mod_"+sem_name, category="")
            study.add_semester(sem)

        ref_lst = ["mod_"+sem_name for sem_name in sem_data]
        sem_lst = study.get_modules()
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

        sem_lst = study.get_modules(semName="sem")
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

        ref_lst = ["mod_sem1", "mod_sem11"]
        sem_lst = study.get_modules(semName="sem1")
        self.assertEqual(ref_lst, sem_lst, "study.get_modules did not return \
                         expected list")

    def test_get_categories(self):
        '''test if all used modules are returned'''
        study = TimeTracker.Study(180, 30, datetime.datetime.now())

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


class TimeTrackerUnitTest(unittest.TestCase):
    def setUp(self):
        self.study = TimeTracker.Study(ECTS=180,hoursPerECTS=30,plannedEnd=datetime.datetime.now())
    
    def test_init(self):
        '''test the constructor of TimeTracker'''
        # wrong arguments
        with self.assertRaises(TypeError):
            tracker = TimeTracker.TimeTracker()
        with self.assertRaises(TypeError):
            tracker = TimeTracker.TimeTracker(ECTS=180)
        with self.assertRaises(TypeError):
            tracker = TimeTracker.TimeTracker(hoursPerECTS=30)
        with self.assertRaises(TypeError):
            tracker = TimeTracker.TimeTracker(
                plannedEnd=datetime.datetime.now())

    def test_start_tracking(self):
        '''test the start tracking function'''
        timeTracker = TimeTracker.TimeTracker(self.study)

        # wrong arguments
        with self.assertRaises(TypeError):
            timeTracker.start_tracking()
        with self.assertRaises(TypeError):
            timeTracker.start_tracking(semesterName="sem")
        with self.assertRaises(TypeError):
            timeTracker.start_tracking(semesterName="sem", moduleName="mod")

        self.assertIsNone(timeTracker.current_entry, "Current entry was set\
                          althoug start_tracking failed")

        # test starting an entry
        timeTracker.start_tracking(semesterName="sem", moduleName="mod",
                                   category="cat")

        self.assertIsNotNone(timeTracker.current_entry, "Current entry is None\
                             although tracking was started successfully")

        sem = timeTracker.study.get_semester("sem")
        mod = sem.get_module("mod")

        self.assertEqual(first=timeTracker.current_entry, second=mod.entries[0],
                         msg="Entry which was started is not current entry")

    def test_stop_tracking(self):
        '''test stopping the tracking'''
        timeTracker = TimeTracker.TimeTracker(self.study)

        # stop not running tracking
        with self.assertRaises(RuntimeError):
            timeTracker.stop_tracking()

        # stop a running entry
        timeTracker.start_tracking(semesterName="sem", moduleName="mod",
                                   category="cat")

        timeTracker.stop_tracking()

        self.assertIsNone(timeTracker.current_entry, "Current entry was not\
                          reset after stopping the tracking")

        ref_stop = datetime.datetime.now()
        sem = timeTracker.study.get_semester("sem")
        mod = sem.get_module("mod")
        stop = mod.entries[0].stop_time

        self.assertEqual(first=ref_stop, second=stop,
                         msg="Stop time of currently stopped entra is not\
                            datetime.now()")

    def test_timer_updates_status(self):
        '''test if the observer is called correctly'''
        timeTracker = TimeTracker.TimeTracker(self.study)

        updates = []

        def mock_status_change(elapsed):
            updates.append(elapsed)
        
        timeTracker.on_status_change = mock_status_change

        timeTracker.toggle_tracking("Sem","Mod","Cat","")
        sleep(2.5)
        timeTracker.toggle_tracking("Sem","Mod","Cat","")
        sleep(2)

        # start, 2 updates, stop
        self.assertEqual(len(updates), 4, "observer was not called 3 times within 3 seconds")

        for i in range(len(updates)):
            self.assertIsInstance(updates[i], datetime.timedelta, "observer did not pass correct datatype as parameter")
            if(i < len(updates) - 1):
                self.assertEqual(updates[i].seconds, i)
            else:
                self.assertEqual(updates[i].seconds, 0)
            


if __name__ == '__main__':
    unittest.main()
