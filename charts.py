import datetime
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from abc import ABC, abstractmethod
from enum import Enum


class ChartType(Enum):
    BURNDOWN = 'burndown'
    PIE = 'pie'


class Chart(ABC):
    '''superclass to draw a chart'''

    def __init__(self):
        self.figure = None

    @abstractmethod
    def plot(self):
        ''' abstract method to plot '''
        pass

    def create_canvas(self, fig, frame):
        ''' draw the Matplot figure to a frame 

        fig: the matplotlib figure
        frame: the tkinter frame
        '''

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.NONE, expand=True)
        self.figure = fig
        self.frame = frame

    def destroy(self):
        ''' destroy the widget and close the figure

        figure must be closed to prevent a memory leak
        '''
        for widget in self.frame.winfo_children():
            widget.destroy()

        plt.close(self.figure)


class BurndownChart(Chart):
    ''' Burndown chart

    extends chart
    implements plot function for burndown charts
    '''

    def __init__(self, date_lst, work_lst, total_work, planned_end):
        ''' init a burndown chart

        calculates the remaining_work and the target line (planned)

        date_lst: list of dates
        work_lst: corresponding lst of done work
        total_work: the total amount of work
        planned_end: the planned end
        '''
        super().__init__()
        self.dates = date_lst
        self.remaining_work = []
        remaining = total_work
        for ects in work_lst:
            remaining -= ects
            self.remaining_work.append(remaining)

        self.plan_x = [date_lst[0], planned_end]
        self.plan_y = [total_work, 0]

    def plot(self, frame):
        ''' plots a burndown chart

        frame: the frame where the figure should be shown
        '''
        fig, ax = plt.subplots(figsize=(5, 5))
        # plot burndown rate
        ax.plot(self.dates, self.remaining_work,
                marker='o', linestyle='-', color='b')
        # plot target line
        ax.plot(self.plan_x, self.plan_y, linestyle='--', color='g')
        ax.set_title('Burndown Chart')
        ax.set_xlabel('Date')
        ax.set_ylabel('Remaining Work')
        ax.grid(True)


        self.create_canvas(fig, frame)


class PieChart(Chart):
    ''' Pie chart

    extends chart
    implements plot function for pie charts
    '''

    def __init__(self, labels, sizes):
        ''' init a pie chart

        calculates the relative sizes

        labels: different categories
        sizes: the absolute sizes of the categories
        '''
        super().__init__()
        self.labels = labels
        sum = np.sum(sizes)
        if sum == 0.0:
            raise ValueError("sum of sizes is zero")

        self.rel_sizes = [100 * size / sum for size in sizes]

    def plot(self, frame):
        ''' plots a pie chart

        frame: the frame where the figure should be shown
        '''
        fig, ax = plt.subplots(figsize=(5, 5))
        wedges, _, _ = ax.pie(self.rel_sizes,
                              autopct='%1.1f%%', startangle=0)
        ax.set_title('Pie Chart')
        # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.axis('equal')

        # Create legend with percentage
        labels_with_pct = [f'{label} - {size:.1f}%' for label,
                           size in zip(self.labels, self.rel_sizes)]

        ax.legend(wedges, labels_with_pct, loc="lower left",
                  bbox_to_anchor=(-0.15, -0.15, 0, 0))

        self.create_canvas(fig, frame)


class ChartFactory:
    '''Chart factory

    instantiates different charts
    '''
    @staticmethod
    def create_chart(chart_type, *args, **kwargs):
        if chart_type == ChartType.BURNDOWN:
            return BurndownChart(*args, **kwargs)
        elif chart_type == ChartType.PIE:
            return PieChart(*args, **kwargs)
        else:
            raise ValueError(f"Chart type {chart_type} is not supported.")


if __name__ == "__main__":
    # Main frame
    root = tk.Tk()
    root.title("Chart Application")

    # Burndown-Chart frame
    frame1 = tk.Frame(root)
    frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Burndown-Chart data
    dates = [datetime.date(2024, 6, i) for i in range(1, 11)]
    remaining_work = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]

    # create and plot Burndown-Chart
    burndown_chart = ChartFactory.create_chart(
        ChartType.BURNDOWN, dates, remaining_work)
    burndown_chart.plot(frame1)

    # Pie-Chart frame
    frame2 = tk.Frame(root)
    frame2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Pie-Chart data
    labels = ['Apples', 'Bananas', 'Cherries', 'Dates']
    sizes = [15, 30, 45, 10]

    # create and plot Pie-Chart
    pie_chart = ChartFactory.create_chart(ChartType.PIE, labels, sizes)
    pie_chart.plot(frame2)

    root.mainloop()
