import unittest
import model
import datetime
import controller
from time import sleep


class TimeTrackerUnitTest(unittest.TestCase):
    def setUp(self):
        self.study = model.Study(ECTS=180,hoursPerECTS=30,plannedEnd=datetime.datetime.now())
    
    def test_init(self):
        '''test the constructor of TimeTracker'''
        # wrong arguments
        with self.assertRaises(TypeError):
            tracker = controller.TimeTracker()
        with self.assertRaises(TypeError):
            tracker = controller.TimeTracker(ECTS=180)
        with self.assertRaises(TypeError):
            tracker = controller.TimeTracker(hoursPerECTS=30)
        with self.assertRaises(TypeError):
            tracker = controller.TimeTracker(
                plannedEnd=datetime.datetime.now())

    def test_start_tracking(self):
        '''test the start tracking function'''
        timeTracker = controller.TimeTracker(self.study)

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

        sem = timeTracker._study.get_semester("sem")
        mod = sem.get_module("mod")

        self.assertEqual(first=timeTracker.current_entry, second=mod.entries[0],
                         msg="Entry which was started is not current entry")

    def test_stop_tracking(self):
        '''test stopping the tracking'''
        timeTracker = controller.TimeTracker(self.study)

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
        sem = timeTracker._study.get_semester("sem")
        mod = sem.get_module("mod")
        stop = mod.entries[0].stop_time

        self.assertEqual(first=ref_stop, second=stop,
                         msg="Stop time of currently stopped entra is not\
                            datetime.now()")

    def test_timer_updates_status(self):
        '''test if the observer is called correctly'''
        timeTracker = controller.TimeTracker(self.study)

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

    def test_serialize_object(self):
        '''test the serialize_object method'''
        timeTracker = controller.TimeTracker(self.study)
        
        semester = model.Semester(name="sem")
        module = model.Module(name="mod")
        entry = model.Entry(category="cat", comment="com")
        
        semester_id = timeTracker.serialize_object(semester)
        module_id = timeTracker.serialize_object(module)
        entry_id = timeTracker.serialize_object(entry)
        
        self.assertTrue(semester_id.startswith("semester:"))
        self.assertTrue(module_id.startswith("module:"))
        self.assertTrue(entry_id.startswith("entry:"))

    def test_deserialize_object(self):
        '''test the deserialize_object method'''
        timeTracker = controller.TimeTracker(self.study)
        
        semester, module, entry = timeTracker._study.add_entry("sem", "mod", "cat", "com")
        
        semester_id = timeTracker.serialize_object(semester)
        module_id = timeTracker.serialize_object(module)
        entry_id = timeTracker.serialize_object(entry)
        
        deserialized_semester = timeTracker.deserialize_object(semester_id)
        deserialized_module = timeTracker.deserialize_object(module_id)
        deserialized_entry = timeTracker.deserialize_object(entry_id)
        
        self.assertEqual(semester, deserialized_semester)
        self.assertEqual(module, deserialized_module)
        self.assertEqual(entry, deserialized_entry)

    def test_get_filtered_data_list(self):
        '''test the get_filtered_data_list method'''
        timeTracker = controller.TimeTracker(self.study)
        
        semester = model.Semester(name="sem")
        module = model.Module(name="mod")
        entry = model.Entry(category="cat", comment="com")
        
        self.study.semesters.append(semester)
        semester.modules.append(module)
        module.entries.append(entry)
        
        filtered_data = timeTracker.get_filtered_data_list("sem", "mod", "cat")
        
        self.assertEqual(len(filtered_data), 1)
        self.assertEqual(filtered_data[0]["semester"], semester)
        self.assertEqual(filtered_data[0]["module"], module)
        self.assertEqual(filtered_data[0]["entry"], entry)

    def test_finish_module(self):
        '''test the finish_module method'''
        timeTracker = controller.TimeTracker(self.study)
        
        _,mod,_ = timeTracker._study.add_entry("sem", "mod", "cat", "com")
        
        timeTracker.finish_module("sem", "mod")
        time = datetime.datetime.now()
        
        self.assertAlmostEquals(mod.stop, time, delta=datetime.timedelta(seconds=1))

    def test_add_new_entry(self):
        '''test the add_new_entry method'''
        timeTracker = controller.TimeTracker(self.study)
        
        semester_name = "sem"
        module_name = "mod"
        category = "cat"
        comment = "com"
        start_time = datetime.datetime.now()
        stop_time = datetime.datetime.now()
        
        sem, mod, entry = timeTracker.add_new_entry(semester_name, module_name, category, comment, start_time, stop_time)
        
        self.assertEqual(entry.start_time, start_time)
        self.assertEqual(entry.stop_time, stop_time)
        self.assertEqual(entry.category, category)
        self.assertEqual(entry.comment, comment)

    def test_remove_entry(self):
        '''test the remove_entry method'''
        timeTracker = controller.TimeTracker(self.study)
        
        semester = model.Semester(name="sem")
        module = model.Module(name="mod")
        entry = model.Entry(category="cat", comment="com")
        
        self.study.semesters.append(semester)
        semester.modules.append(module)
        module.entries.append(entry)
        
        timeTracker.remove_entry(semester, module, entry)
        
        self.assertEqual(len(module.entries), 0)

    def test_edit_entry(self):
        '''test the edit_entry method'''
        timeTracker = controller.TimeTracker(self.study)
        
        semester = model.Semester(name="sem")
        module = model.Module(name="mod")
        entry = model.Entry(category="cat", comment="com")
        
        self.study.semesters.append(semester)
        semester.modules.append(module)
        module.entries.append(entry)
        
        edit_semester_name = "new_sem"
        edit_module_name = "new_mod"
        edit_category = "new_cat"
        edit_comment = "new_com"
        edit_start_time = datetime.datetime.now()
        edit_stop_time = datetime.datetime.now()
        edit_module_stop = datetime.datetime.now()
        
        timeTracker.edit_entry(semester, module, entry, edit_semester_name, edit_module_name, edit_category, edit_comment, edit_start_time, edit_stop_time, edit_module_stop)
        
        self.assertEqual(len(module.entries), 0)
        new_semester = timeTracker.get_semester(edit_semester_name)
        new_module = new_semester.get_module(edit_module_name)
        new_entry = new_module.entries[0]
        
        self.assertEqual(new_entry.category, edit_category)
        self.assertEqual(new_entry.comment, edit_comment)
        self.assertEqual(new_entry.start_time, edit_start_time)
        self.assertEqual(new_entry.stop_time, edit_stop_time)
        self.assertEqual(new_module.stop, edit_module_stop)


if __name__ == '__main__':
    unittest.main()
