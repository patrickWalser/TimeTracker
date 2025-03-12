import unittest
import tkinter as tk
from date_time_frame import DateTimeFrame
import datetime


class TestDateTimeFrame(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.frame = DateTimeFrame(self.root, "Test Label")

    def tearDown(self):
        self.root.destroy()

    def test_initialization(self):
        ''' test the initialization of the DateTimeFrame '''
        self.assertEqual(self.frame.get_datetime(), None)
        self.assertEqual(self.frame.winfo_children()[
                         0].cget("text"), "Test Label")
        self.assertEqual(self.frame.winfo_children()[1].cget("text"), "Date:")
        self.assertEqual(self.frame.winfo_children()[3].cget("text"), "Time:")
        self.assertEqual(self.frame.hour_entry['values'], tuple(
            f"{i:02}" for i in range(24)))
        self.assertEqual(self.frame.minute_entry['values'], tuple(
            f"{i:02}" for i in range(60)))

    def test_initialize_date_entry(self):
        ''' test the initialize_date_entry method '''
        self.frame.initialize_date_entry()
        self.assertEqual(self.frame.date_initialized, True)
        self.assertIsNotNone(self.frame.date)

    def test_set_datetime(self):
        ''' test the set_datetime method '''
        self.frame.initialize_date_entry()
        self.assertEqual(self.frame.get_datetime().date(),
                         datetime.datetime.now().date())
        self.assertEqual(self.frame.hour_entry.get(), "")
        self.assertEqual(self.frame.minute_entry.get(), "")

        test_datetime = datetime.datetime(2024, 6, 15, 14, 30)
        self.frame.set_datetime(test_datetime)
        self.assertEqual(self.frame.get_datetime(), test_datetime)
        self.assertEqual(self.frame.hour_entry.get(), "14")
        self.assertEqual(self.frame.minute_entry.get(), "30")

        self.frame.initialize_date_entry()
        self.assertEqual(self.frame.get_datetime(), test_datetime)
        self.assertEqual(self.frame.hour_entry.get(), "14")
        self.assertEqual(self.frame.minute_entry.get(), "30")

    def test_get_datetime(self):
        ''' test the get_datetime method '''
        test_datetime = datetime.datetime(2024, 6, 15, 14, 30)
        self.frame.set_datetime(test_datetime)
        result = self.frame.get_datetime()
        self.assertEqual(result, test_datetime)


if __name__ == '__main__':
    unittest.main()
