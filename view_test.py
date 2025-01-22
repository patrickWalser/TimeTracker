import unittest
import tkinter as tk
from model import Study
from controller import TimeTracker
from view import TimeTrackerGUI
import datetime
import os
from unittest.mock import patch
class TimeTrackerGUITest(unittest.TestCase):

    def setUp(self):
        # Setup for GUI-Tests
        self.study = Study(ECTS=180, hoursPerECTS=30, plannedEnd=datetime.datetime.now())
        self.tracker = TimeTracker(self.study)
        self.root = tk.Tk()
        self.root.withdraw()
        self.gui = TimeTrackerGUI(self.root, self.tracker)

    def tearDown(self):
        self.root.destroy()

    def test_start_stop_button(self):
        # Simulate starting the tracking
        self.gui.semester_var.set("Semester1")
        self.gui.module_var.set("Module1")
        self.gui.category_var.set("Programming")
        self.gui.comment_var.set("Test comment")

        self.gui.btn_start_stop_click()  # Start Tracking
        self.assertEqual(self.gui.start_stop_btn.cget("text"), "Stop")
        self.assertTrue(self.tracker.current_entry is not None)
        print(self.gui.current_duration_label["text"])
        #self.assertTrue(self.gui.current_duration_label.cget("text").startswith("Tracking for"))

        # Simulate stopping the tracking
        self.gui.btn_start_stop_click()  # Stop Tracking
        self.assertEqual(self.gui.start_stop_btn.cget("text"), "Start")
        self.assertTrue(self.tracker.current_entry is None)
        self.assertFalse(self.gui.current_duration_label.winfo_ismapped())  # Label invisible

    def test_new_study(self):
        self.gui.new_study(edit=False)
        self.assertIsNotNone(self.gui.tracker._study)
        self.assertEqual(self.gui.tracker._study.ECTS, 180)
        self.assertEqual(self.gui.tracker._study.hoursPerECTS, 30)

    def test_save_new_study(self):
        self.gui.new_study(edit=True)
        self.assertEqual(self.gui.tracker._study.ECTS, 180)
        self.assertEqual(self.gui.tracker._study.hoursPerECTS, 30)

    def test_open_study(self):
        with patch('tkinter.filedialog.askopenfilename', return_value='test_tracker.json'):
            self.gui.open_study()
            self.assertIsNotNone(self.gui.tracker._study)

    def test_save_as(self):
        with patch('tkinter.filedialog.asksaveasfilename', return_value='test_tracker.json'):
            self.gui.save_as()
            self.assertTrue(os.path.exists('test_tracker.json'))

    def test_edit_semesters(self):
        self.gui.edit_semesters()
        self.assertIsNotNone(self.gui.edit_semester_tree)


if __name__ == '__main__':
    unittest.main()