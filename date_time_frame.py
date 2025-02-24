import tkinter as tk
from tkinter import Frame, ttk
from tkcalendar import DateEntry
import datetime
import time

class DateTimeFrame(ttk.Frame):
    ''' a user control to combine selection of date and time

    extends Frame
    '''

    def __init__(self, parent, label):
        ''' constructor of the user control

        parent: the parent frame in which the DateTimeFrame is added
        label: the label to be displayed next to the controls.
        '''
        start = time.time()
        super().__init__(parent)


        tk.Label(self, text=label).grid(row=0, column=0, sticky='w')
        tk.Label(self, text="Date:").grid(row=0, column=1, sticky='w')
        self.date = DateEntry(self)
        self.date.grid(row=0, column=2)

        tk.Label(self, text="Time:").grid(row=0, column=3, sticky='w')
        self.hour_entry = ttk.Combobox(
            self, values=[f"{i:02}" for i in range(24)], width=3)
        self.hour_entry.grid(row=0, column=4, sticky='w')

        self.minute_entry = ttk.Combobox(
            self, values=[f"{i:02}" for i in range(60)], width=3)
        self.minute_entry.grid(row=0, column=5, sticky='w')

    def set_datetime(self, datetime):
        ''' set the value of the user control

        datetime: the datetime object to set
        '''
        if (datetime is None):  # leave empty
            return

        self.date.set_date(datetime)
        self.hour_entry.set(datetime.hour)
        self.minute_entry.set(datetime.minute)

    def get_datetime(self):
        ''' get the value of the user control as datetime

        returns datetime
        '''
        date = self.date.get_date()
        h = int(self.hour_entry.get())
        m = int(self.minute_entry.get())
        return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=h, minute=m)
