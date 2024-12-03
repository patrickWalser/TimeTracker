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
            


if __name__ == '__main__':
    unittest.main()
