import tkinter as tk
import datetime
from model import Study
from controller import TimeTracker
from view import TimeTrackerGUI


if __name__ == "__main__":
    root = tk.Tk()

    # model
    model = Study(180, 30, datetime.datetime.now())

    # controller
    controller = TimeTracker(model)

    # view
    view = TimeTrackerGUI(root, controller)
    root.mainloop()
