import unittest
import model
import datetime
import controller
from time import sleep
import tempfile
import os
import json
from charts import ChartType, PieChart, BurndownChart


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
        ref_stop = datetime.datetime.now()

        self.assertIsNone(timeTracker.current_entry, "Current entry was not\
                          reset after stopping the tracking")

        sem = timeTracker._study.get_semester("sem")
        mod = sem.get_module("mod")
        stop = mod.entries[0].stop_time
        self.assertAlmostEqual(first=ref_stop, second=stop, delta=datetime.timedelta(milliseconds=200),
                       msg="Stop time of currently stopped entry is not close to datetime.now()")

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

    def test_get_object_id(self):
        '''test the get_object_id method'''
        timeTracker = controller.TimeTracker(self.study)
        
        with self.assertRaises(ValueError):
            timeTracker.get_object_id(self.study)
        
        with self.assertRaises(AttributeError):
            timeTracker.get_object_id(None)

        semester = model.Semester(name="sem")
        module = model.Module(name="mod")
        entry = model.Entry(category="cat", comment="com")
        
        semester_id = timeTracker.get_object_id(semester)
        module_id = timeTracker.get_object_id(module)
        entry_id = timeTracker.get_object_id(entry)
        
        self.assertTrue(semester_id.startswith("semester:"))
        self.assertTrue(module_id.startswith("module:"))
        self.assertTrue(entry_id.startswith("entry:"))

        semester.id = None
        semester_id2 = timeTracker.get_object_id(semester)
        self.assertTrue(semester_id2.startswith("semester:"))
        self.assertNotEqual(semester_id, semester_id2)

    def test_get_object_by_id(self):
        '''test the get_object_by_id method'''
        timeTracker = controller.TimeTracker(self.study)
        
        semester, module, entry = timeTracker._study.add_entry("sem", "mod", "cat", "com")
        
        # get the ids
        semester_id = timeTracker.get_object_id(semester)
        module_id = timeTracker.get_object_id(module)
        entry_id = timeTracker.get_object_id(entry)
        
        # test getting objects by id
        deserialized_semester = timeTracker.get_object_by_id(semester_id)
        deserialized_module = timeTracker.get_object_by_id(module_id)
        deserialized_entry = timeTracker.get_object_by_id(entry_id)
        
        self.assertEqual(semester, deserialized_semester)
        self.assertEqual(module, deserialized_module)
        self.assertEqual(entry, deserialized_entry)

        # test getting objects by id with parent
        deserialized_moule = timeTracker.get_object_by_id(module_id, semester)
        deserialized_entry = timeTracker.get_object_by_id(entry_id, module)

        self.assertEqual(module, deserialized_moule)
        self.assertEqual(entry, deserialized_entry)

        # test getting unknown object by id
        unknown_object = timeTracker.get_object_by_id("unknown:123")
        self.assertIsNone(unknown_object)

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
        edit_module_start = datetime.datetime.now()
        edit_module_stop = datetime.datetime.now()

        timeTracker.edit_entry(semester, module, entry, edit_semester_name, edit_module_name, edit_category, edit_comment, edit_start_time, edit_stop_time, edit_module_start, edit_module_stop)
        
        self.assertEqual(len(module.entries), 0)
        new_semester = timeTracker.get_semester(edit_semester_name)
        new_module = new_semester.get_module(edit_module_name)
        new_entry = new_module.entries[0]
        
        self.assertEqual(new_entry.category, edit_category)
        self.assertEqual(new_entry.comment, edit_comment)
        self.assertEqual(new_entry.start_time, edit_start_time)
        self.assertEqual(new_entry.stop_time, edit_stop_time)
        self.assertEqual(new_module.start, edit_module_start)
        self.assertEqual(new_module.stop, edit_module_stop)

    def test_get_burndown_chart_data_study(self):
        '''test the _get_burndown_chart_data method for Study scope'''
        timeTracker = controller.TimeTracker(self.study)
        self.study.plannedEnd = datetime.datetime(2024, 12, 31)
        
        # Create mock data
        semester1 = model.Semester(name="sem1", ECTS=10, plannedEnd=datetime.datetime(2023, 12, 31))
        semester2 = model.Semester(name="sem2", ECTS=10, plannedEnd=datetime.datetime(2024, 12, 31))

        module1 = model.Module(name="mod1", ECTS=5)
        module1.start = datetime.datetime(2023, 1, 1)
        module1.plannedEnd = datetime.datetime(2023, 6, 30)
        module1.stop = datetime.datetime(2023, 6, 30)

        module2 = model.Module(name="mod2", ECTS=5)
        module2.start=datetime.datetime(2023, 7, 1)
        module2.plannedEnd=datetime.datetime(2023, 12, 31)
        module2.stop=datetime.datetime(2023, 12, 31)

        module3 = model.Module(name="mod3", ECTS=5)
        module3.start=datetime.datetime(2024, 1, 1)
        module3.plannedEnd=datetime.datetime(2024, 6, 30)
        module3.stop=datetime.datetime(2024, 6, 30)

        module4 = model.Module(name="mod4", ECTS=5)
        module4.start=datetime.datetime(2024, 7, 1)
        module4.plannedEnd=datetime.datetime(2024, 12, 31)
        module4.stop=datetime.datetime(2024, 12, 31)
        
        semester1.modules.extend([module1, module2])
        semester2.modules.extend([module3, module4])
        self.study.semesters.extend([semester1, semester2])
        
        # Get burndown chart data
        stop_times, values, total_work, planned_end = timeTracker._get_burndown_chart_data(self.study)
        
        # Assertions
        self.assertEqual(total_work, 180)
        self.assertEqual(planned_end, datetime.datetime(2024, 12, 31))
        self.assertEqual(stop_times, [datetime.datetime(2023, 1, 1), datetime.datetime(2023, 6, 30), datetime.datetime(2023, 12, 31), datetime.datetime(2024, 6, 30), datetime.datetime(2024, 12, 31)])
        self.assertEqual(values, [0, 5, 5, 5, 5])

    def test_get_burndown_chart_data_semester(self):
        '''test the _get_burndown_chart_data method for Semester scope'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Create mock data
        semester = model.Semester(name="sem", ECTS=10, plannedEnd=datetime.datetime(2023, 12, 31))
        
        module1 = model.Module(name="mod1", ECTS=5)
        module1.start=datetime.datetime(2023, 1, 1)
        module1.plannedEnd=datetime.datetime(2023, 6, 30)
        module1.stop=datetime.datetime(2023, 6, 30)

        module2 = model.Module(name="mod2", ECTS=5) 
        module2.start=datetime.datetime(2023, 7, 1)
        module2.plannedEnd=datetime.datetime(2023, 12, 31)
        module2.stop=datetime.datetime(2023, 12, 31)
        
        semester.modules.extend([module1, module2])
        self.study.semesters.append(semester)
        
        # Get burndown chart data
        stop_times, values, total_work, planned_end = timeTracker._get_burndown_chart_data(semester)
        
        # Assertions
        self.assertEqual(total_work, 10)
        self.assertEqual(planned_end, datetime.datetime(2023, 12, 31))
        self.assertEqual(stop_times, [datetime.datetime(2023, 1, 1), datetime.datetime(2023, 6, 30), datetime.datetime(2023, 12, 31)])
        self.assertEqual(values, [0, 5, 5])

    def test_get_burndown_chart_data_module(self):
        '''test the _get_burndown_chart_data method for Module scope'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Create mock data
        semester = model.Semester(name="sem", ECTS=10, plannedEnd=datetime.datetime(2023, 12, 31))
        module = model.Module(name="mod", ECTS=5)
        module.start=datetime.datetime(2023, 1, 1)
        module.plannedEnd=datetime.datetime(2023, 6, 30)
        module.stop=datetime.datetime(2023, 6, 30)
        
        semester.modules.append(module)
        self.study.semesters.append(semester)
        
        # Get burndown chart data
        result = timeTracker._get_burndown_chart_data(module)
        
        # Assertions
        self.assertIsNone(result)

    def test_export_to_json(self):
        '''test the export_to_json method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Save the current last_filename and set a temporary one
        prev_last_filename = timeTracker.settings.get("last_filename")
        last_filename = "tmp.json"
        timeTracker.settings.set("last_filename", last_filename)

        # Default file
        # Export data to JSON
        timeTracker.export_to_json(None)

        # Read file and check its content
        with open(last_filename, "r") as file:
            data = json.load(file)

        self.assertIn('ECTS', data)
        self.assertIn('hoursPerECTS', data)

        # Cleanup
        os.remove(last_filename)

        # Custom file
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Export data to JSON
        timeTracker.export_to_json(temp_filename)
        
        # Check if file exists
        self.assertTrue(os.path.exists(temp_filename))
        
        # Read the file and check its content
        with open(temp_filename, 'r') as file:
            data = json.load(file)
        
        self.assertIn('ECTS', data)
        self.assertIn('hoursPerECTS', data)
        
        # Clean up
        os.remove(temp_filename)

        # Reset the last_filename
        timeTracker.settings.set("last_filename", prev_last_filename)

    def test_import_from_json(self):
        '''test the import_from_json method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Save the current last_filename and set a temporary one
        prev_last_filename = timeTracker.settings.get("last_filename")
        last_filename = "tmp.json"
        timeTracker.settings.set("last_filename", last_filename)

        # Default file
        # Export data to JSON
        timeTracker.export_to_json(None)

        # Create a new TimeTracker instance and import data
        new_timeTracker = controller.TimeTracker(model.Study(ECTS=0, hoursPerECTS=0, plannedEnd=datetime.datetime.now()))
        new_timeTracker.import_from_json(None)

        # Check if the data was imported correctly
        self.assertEqual(new_timeTracker._study.ECTS, self.study.ECTS)
        self.assertEqual(new_timeTracker._study.hoursPerECTS, self.study.hoursPerECTS)

        # Custom file
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Export data to JSON
        timeTracker.export_to_json(temp_filename)
        
        # Create a new TimeTracker instance and import data
        new_timeTracker = controller.TimeTracker(model.Study(ECTS=0, hoursPerECTS=0, plannedEnd=datetime.datetime.now()))
        new_timeTracker.import_from_json(temp_filename)
        
        # Check if the data was imported correctly
        self.assertEqual(new_timeTracker._study.ECTS, self.study.ECTS)
        self.assertEqual(new_timeTracker._study.hoursPerECTS, self.study.hoursPerECTS)
        
        # Clean up
        os.remove(temp_filename)

        # Reset the last_filename
        timeTracker.settings.set("last_filename", prev_last_filename)

    def test_update_semester(self):
        '''test the update_semester method'''
        timeTracker = controller.TimeTracker(self.study)
        
        semester = model.Semester(name="sem", ECTS=30, plannedEnd=datetime.datetime(2023, 12, 31))
        self.study.semesters.append(semester)
        
        # Test updating ECTS
        updated_semester = timeTracker.update_semester(semester, "ECTS", "60")
        self.assertEqual(updated_semester.ECTS, 60)
        
        # Test updating plannedEnd with valid formats
        valid_dates = ["2024-12-31", "31.12.2024", "2024/12/31", "12/31/2024"]
        for date in valid_dates:
            updated_semester = timeTracker.update_semester(semester, "plannedEnd", date)
            self.assertEqual(updated_semester.plannedEnd, datetime.datetime(2024, 12, 31))
        
        # Test updating plannedEnd with invalid format
        with self.assertRaises(ValueError):
            timeTracker.update_semester(semester, "plannedEnd", "31-12-2024")
        
        # Test updating with invalid ECTS value
        with self.assertRaises(ValueError):
            timeTracker.update_semester(semester, "ECTS", "invalid")
        
        # Test updating non-existent semester
        with self.assertRaises(ValueError):
            timeTracker.update_semester(None, "ECTS", "60")

    def test_get_initial_entry(self):
        '''test the get_initial_entry method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Test with no entries
        initial_entry = timeTracker.get_initial_entry()
        self.assertEqual(initial_entry, (None, None, None))

        # Add an entry to the study
        timeTracker.start_tracking("sem", "mod", "cat", "com")
        semester = timeTracker.current_semester
        module = timeTracker.current_module
        entry = timeTracker.current_entry

        timeTracker.stop_tracking()
        
        # Get the initial entry
        initial_entry = timeTracker.get_initial_entry()
        self.assertEqual(initial_entry, (semester, module, entry))

    def test_get_semester(self):
        '''test the get_semester method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Add a semester to the study
        semester_name = "sem"
        semester = model.Semester(name=semester_name)
        self.study.semesters.append(semester)
        
        # Test getting the semester by name
        retrieved_semester = timeTracker.get_semester(semester_name)
        self.assertEqual(retrieved_semester, semester)
        
        # Test getting a non-existent semester
        non_existent_semester = timeTracker.get_semester("non_existent_sem")
        self.assertIsNone(non_existent_semester)

    def test_get_semesters(self):
        '''test the get_semesters method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Test with no semesters
        self.assertEqual(timeTracker.get_semesters(), [])
        
        # Add semesters to the study
        semester1 = model.Semester(name="sem1")
        semester2 = model.Semester(name="sem2")
        self.study.semesters.extend([semester1, semester2])
        
        # Test with semesters
        semesters = timeTracker.get_semesters()
        self.assertEqual(len(semesters), 2)
        self.assertIn(semester1, semesters)
        self.assertIn(semester2, semesters)

    def test_get_semester_names(self):
        '''test the get_semester_names method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Test with no semesters
        self.assertEqual(timeTracker.get_semester_names(), [])
        
        # Add semesters to the study
        semester1 = model.Semester(name="sem1")
        semester2 = model.Semester(name="sem2")
        self.study.semesters.extend([semester1, semester2])
        
        # Test with semesters
        semester_names = timeTracker.get_semester_names()
        self.assertEqual(len(semester_names), 2)
        self.assertIn("sem1", semester_names)
        self.assertIn("sem2", semester_names)

    def test_get_modules(self):
        '''test the get_modules method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Test with no semesters
        self.assertEqual(timeTracker.get_modules("sem"), [])
        
        # Add a semester with modules to the study
        semester_name = "sem"
        module1 = model.Module(name="mod1")
        module2 = model.Module(name="mod2")
        semester = model.Semester(name=semester_name)
        semester.modules.extend([module1, module2])
        self.study.semesters.append(semester)
        
        # Test with existing semester
        modules = timeTracker.get_modules(semester_name)
        self.assertEqual(len(modules), 2)
        self.assertIn(module1, modules)
        self.assertIn(module2, modules)
        
        # Test with non-existent semester
        non_existent_modules = timeTracker.get_modules("non_existent_sem")
        self.assertEqual(non_existent_modules, [])

    def test_get_module_names(self):
        '''test the get_module_names method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Test with no semesters
        self.assertEqual(timeTracker.get_module_names("sem"), [])
        
        # Add a semester with modules to the study
        semester_name = "sem"
        module1 = model.Module(name="mod1")
        module2 = model.Module(name="mod2")
        semester = model.Semester(name=semester_name)
        semester.modules.extend([module1, module2])
        self.study.semesters.append(semester)
        
        # Test with existing semester
        module_names = timeTracker.get_module_names(semester_name)
        self.assertEqual(len(module_names), 2)
        self.assertIn("mod1", module_names)
        self.assertIn("mod2", module_names)
        
        # Test with non-existent semester
        non_existent_module_names = timeTracker.get_module_names("non_existent_sem")
        self.assertEqual(non_existent_module_names, [])

    def test_get_category_names(self):
        '''test the get_category_names method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Test with no semesters or modules
        self.assertEqual(timeTracker.get_category_names("sem", "mod"), [])
        
        # Add a semester with a module and categories to the study
        semester_name = "sem"
        module_name = "mod"
        category1 = "cat1"
        category2 = "cat2"
        module = model.Module(name=module_name)
        module.entries.append(model.Entry(category=category1, comment=""))
        module.entries.append(model.Entry(category=category2, comment=""))
        semester = model.Semester(name=semester_name)
        semester.modules.append(module)
        self.study.semesters.append(semester)
        
        # Test with existing semester and module
        category_names = timeTracker.get_category_names(semester_name, module_name)
        self.assertEqual(len(category_names), 2)
        self.assertIn(category1, category_names)
        self.assertIn(category2, category_names)
        
        # Test with non-existent semester
        non_existent_categories = timeTracker.get_category_names("non_existent_sem", module_name)
        self.assertEqual(non_existent_categories, [])
        
        # Test with non-existent module
        non_existent_categories = timeTracker.get_category_names(semester_name, "non_existent_mod")
        self.assertEqual(non_existent_categories, [])

    def test_generate_chart_pie(self):
        '''test the generate_chart method for PIE chart'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Create mock data
        semester = model.Semester(name="sem", ECTS=10, plannedEnd=datetime.datetime(2023, 12, 31))
        module = model.Module(name="mod", ECTS=5)
        module.start = datetime.datetime(2023, 1, 1)
        module.plannedEnd = datetime.datetime(2023, 6, 30)
        module.stop = datetime.datetime(2023, 6, 30)
        entry = model.Entry(category="cat", comment="com")
        sleep(1)
        entry.stop()

        module.entries.append(entry)
        semester.modules.append(module)
        self.study.semesters.append(semester)
        
        # Generate PIE chart
        chart = timeTracker.generate_chart(self.study, ChartType.PIE)
        
        # Assertions
        self.assertIsNotNone(chart)
        self.assertIsInstance(chart, PieChart)
        self.assertEqual(chart.labels, ["sem"])
        self.assertEqual(chart.rel_sizes, [100.0])

    def test_generate_chart_burndown(self):
        '''test the generate_chart method for BURNDOWN chart'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Create mock data
        semester = model.Semester(name="sem", ECTS=10, plannedEnd=datetime.datetime(2023, 12, 31))
        module = model.Module(name="mod", ECTS=5)
        module.start = datetime.datetime(2023, 1, 1)
        module.plannedEnd = datetime.datetime(2023, 5, 30)
        module.stop = datetime.datetime(2023, 6, 30)
        entry = model.Entry(category="cat", comment="com")
        sleep(1)
        entry.stop()
        module.entries.append(entry)
        semester.modules.append(module)
        self.study.semesters.append(semester)
        
        # Generate BURNDOWN chart
        chart = timeTracker.generate_chart(self.study, ChartType.BURNDOWN)
        
        # Assertions
        self.assertIsNotNone(chart)
        self.assertIsInstance(chart, BurndownChart)
        self.assertEqual(chart.dates,[module.start, module.stop])
        self.assertEqual(chart.remaining_work, [180, 175])

    def test_update_study(self):
        '''test the update_study method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Define new study parameters
        new_ECTS = 120
        new_hoursPerECTS = 25
        new_plannedEnd = datetime.datetime(2025, 12, 31)
        
        # Mock the on_treeview_update method
        update_called = False
        def mock_on_treeview_update():
            nonlocal update_called
            update_called = True
        
        timeTracker.on_treeview_update = mock_on_treeview_update
        
        # Update the study
        timeTracker.update_study(new_ECTS, new_hoursPerECTS, new_plannedEnd)
        
        # Assertions
        self.assertEqual(timeTracker._study.ECTS, new_ECTS)
        self.assertEqual(timeTracker._study.hoursPerECTS, new_hoursPerECTS)
        self.assertEqual(timeTracker._study.plannedEnd, new_plannedEnd)
        self.assertTrue(update_called, "on_treeview_update was not called")

    def test_create_new_study(self):
        '''test the create_new_study method'''
        timeTracker = controller.TimeTracker(self.study)
        
        # Define new study parameters
        new_ECTS = 120
        new_hoursPerECTS = 25
        new_plannedEnd = datetime.datetime(2025, 12, 31)
        
        # Mock the on_treeview_update method
        update_called = False
        def mock_on_treeview_update():
            nonlocal update_called
            update_called = True
        
        timeTracker.on_treeview_update = mock_on_treeview_update
        
        # Create a new study
        new_study = timeTracker.create_new_study(new_ECTS, new_hoursPerECTS, new_plannedEnd)
        
        # Assertions
        self.assertIsNotNone(new_study, "New study was not created")
        self.assertEqual(new_study.ECTS, new_ECTS)
        self.assertEqual(new_study.hoursPerECTS, new_hoursPerECTS)
        self.assertEqual(new_study.plannedEnd, new_plannedEnd)
        self.assertTrue(update_called, "on_treeview_update was not called")





if __name__ == '__main__':
    unittest.main()
