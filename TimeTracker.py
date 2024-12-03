import tkinter as tk
import datetime
from model import Study
from controller import TimeTracker
from view import TimeTrackerGUI


if __name__ == "__main__":
    root = tk.Tk()

    # model
    study = Study(180,30, datetime.datetime.now())

    # controller
    tracker = TimeTracker(study)

    # view
    app = TimeTrackerGUI(root, tracker)
    root.mainloop()