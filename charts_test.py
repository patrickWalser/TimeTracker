import unittest
import datetime
from charts import BurndownChart, PieChart
import tkinter as tk


class TestBurndownChart(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.dates = [datetime.date(2024, 6, i) for i in range(1, 11)]
        self.work_lst = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.total_work = 100
        self.planned_end = self.dates[-1]

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        chart = BurndownChart("title", self.dates,
                              self.work_lst, self.total_work, self.planned_end)

        expected_remaining_work = [90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
        expected_plan_x = [self.dates[0] +
                           datetime.timedelta(days=i) for i in range(10)]
        expected_plan_y = [self.total_work -
                           (self.total_work / 9) * i for i in range(10)]
        expected_interval = 1  # 10 days / 10 ticks

        self.assertEqual(chart.title, "title")
        self.assertEqual(chart.remaining_work, expected_remaining_work)
        self.assertEqual(chart.plan_x, expected_plan_x)
        self.assertEqual(chart.plan_y, expected_plan_y)
        self.assertEqual(chart.interval, expected_interval)

    def test_plot(self):
        chart = BurndownChart("title", self.dates,
                              self.work_lst, self.total_work, self.planned_end)
        frame = tk.Frame(self.root)
        chart.plot(frame)
        self.assertIsNotNone(chart.figure)
        self.assertEqual(chart.figure.axes[0].get_title(), 'title')
        self.assertEqual(chart.figure.axes[0].get_xlabel(), 'Date')
        self.assertEqual(chart.figure.axes[0].get_ylabel(), 'Remaining Work')

        chart.destroy()
        frame.destroy()


class TestPieChartPlot(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.labels = ['Apples', 'Bananas', 'Cherries', 'Dates']
        self.sizes = [15, 30, 45, 10]

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        # empty list
        labels = []
        sizes = []
        with self.assertRaises(ValueError) as context:
            PieChart("", labels, sizes)
        self.assertEqual(str(context.exception), "sum of sizes is zero")

        # sum of sizes is zero
        labels = ['Apples', 'Bananas', 'Cherries', 'Dates']
        sizes = [0, 0, 0, 0]
        with self.assertRaises(ValueError) as context:
            PieChart("", labels, sizes)
        self.assertEqual(str(context.exception), "sum of sizes is zero")

        # valid data
        labels = ['Apples', 'Bananas', 'Cherries', 'Dates']
        sizes = [15, 30, 45, 10]
        chart = PieChart("title", labels, sizes)

        expected_rel_sizes = [15.0, 30.0, 45.0, 10.0]
        self.assertEqual(chart.title, "title")
        self.assertEqual(chart.labels, labels)
        self.assertEqual(chart.rel_sizes, expected_rel_sizes)

    def test_plot(self):
        frame = tk.Frame(self.root)
        chart = PieChart("title", self.labels, self.sizes)
        chart.plot(frame)
        self.assertIsNotNone(chart.figure)
        self.assertEqual(chart.figure.axes[0].get_title(), 'title')

        expected_labels = []
        for i in range(0, len(self.labels)):
            expected_labels.append(
                self.labels[i] + ' - ' + '{:.1f}%'.format(self.sizes[i]))

        l = chart.figure.axes[0].legend_.texts
        labels = []
        for text in l:
            labels.append(text._text)

        self.assertEqual(labels, expected_labels)

        chart.destroy()
        frame.destroy()


class TestChart(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()

    def tearDown(self):
        self.root.destroy()

    def test_destroy(self):
        chart = BurndownChart("title", [datetime.date(2024, 6, 1), datetime.date(
            2024, 6, 2)], [10, 10], 20, datetime.date.today())
        frame = tk.Frame(self.root)
        chart.plot(frame)

        close_event = False

        def mock_on_close(event):
            nonlocal close_event
            close_event = True

        chart.figure.canvas.mpl_connect('close_event', mock_on_close)
        chart.destroy()

        # Assert that the close event was called
        self.assertTrue(close_event)
        frame.destroy()


if __name__ == '__main__':
    unittest.main()
