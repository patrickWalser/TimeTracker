import unittest
import tkinter as tk
from tkinter import ttk
from my_accordion import Accordion, Accordion_Element
from unittest import mock

class TestAccordionElement(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.accordion = Accordion(self.root)
        self.section = self.accordion.add_section("Section 1", lambda: print("Section 1 clicked"))

    def tearDown(self):
        self.root.destroy()

    def test_add_element(self):
        # add one element
        element = self.section.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
        self.assertEqual(len(self.section.sub_elements), 1)
        self.assertEqual(self.section.sub_elements[0], element)
        self.assertEqual(element.name, "Item 1.1")

        frame = tk.Frame(self.root)

        # add element with one subelement
        element21 = Accordion_Element(self.accordion, frame, "Item 1.2.1", lambda: print("Item 1.2.1 clicked"))
        element2 = self.section.add_element("Item 1.2", lambda: print("Item 1.2 clicked"), [element21])
        self.assertEqual(len(element2.sub_elements), 1)
        self.assertEqual(element2.sub_elements[0], element21)

        # add element with multiple subelements
        element31 = Accordion_Element(self.accordion, frame, "Item 1.3.1", lambda: print("Item 1.3.1 clicked"))
        element32 = Accordion_Element(self.accordion, frame, "Item 1.3.2", lambda: print("Item 1.3.2 clicked"))
        element3 = Accordion_Element(self.accordion, frame, "Item 1.3", lambda: print("Item 1.3 clicked"), [element31, element32])
        self.assertEqual(len(element3.sub_elements), 2)
        self.assertEqual(element3.sub_elements[0], element31)
        self.assertEqual(element3.sub_elements[1], element32)

        frame.destroy()

    def test_remove_element(self):
        element = self.section.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
        self.section.remove_element(element)
        self.assertEqual(len(self.section.sub_elements), 0)

    def test_toggle_element(self):
        element = self.section.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
        self.assertFalse(element.visible)
        element.toggle_element()
        self.assertTrue(element.visible)
        element.toggle_element()
        self.assertFalse(element.visible)

    def test_reorder(self):
        element1 = self.section.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
        element2 = self.section.add_element("Item 1.2", lambda: print("Item 1.2 clicked"))

        # collapsed
        self.section.reorder()
        self.assertEqual(element1.row, 0)
        self.assertEqual(element2.row, 0)

        # expanded
        self.section.toggle_element()
        element1.toggle_element()
        element2.toggle_element()
        self.section.reorder()
        self.assertEqual(element1.row, 0)
        self.assertEqual(element2.row, 2)

    def test_destroy(self):
        accordion = Accordion(self.root)
        section = accordion.add_section("Section 1", lambda: print("Section 1 clicked"))
        element1 = section.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
        element2 = section.add_element("Item 1.2", lambda: print("Item 1.2 clicked"))
        sub_element = element2.add_element("Item 1.2.1", lambda: print("Item 1.2.1 clicked"))

        self.assertEqual(len(section.sub_elements), 2)
        self.assertEqual(len(element2.sub_elements), 1)

        element2.destroy()

        self.assertFalse(element2.winfo_exists())
        self.assertFalse(sub_element.winfo_exists())

        section.destroy()

        self.assertFalse(section.winfo_exists())
        self.assertFalse(element1.winfo_exists())
        accordion.destroy()


class TestAccordion(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.accordion = Accordion(self.root)

    def tearDown(self):
        self.accordion.destroy()
        self.root.destroy()

    def test_add_section(self):
        # add a section
        section1 = self.accordion.add_section("Section 1", lambda: print("Section 1 clicked"))
        self.assertEqual(len(self.accordion.sections), 1)
        self.assertEqual(self.accordion.sections[0], section1)
        self.assertEqual(section1.name, "Section 1")
        
        frame = tk.Frame(self.root)

        # add a section with one subelement
        element1 = Accordion_Element(self.accordion, frame, "Item 2.1", lambda: print("Item 2.1 clicked"))
        section2 = self.accordion.add_section("Section 2", lambda: print("Section 2 clicked"), [element1])
        self.assertEqual(len(section2.sub_elements), 1)
        self.assertEqual(section2.sub_elements[0], element1)
        self.assertEqual(len(self.accordion.sections), 2)
        self.assertEqual(self.accordion.sections[1], section2)

        # add a section with multiple subelements
        element2 = Accordion_Element(self.accordion, frame, "Item 2.2", lambda: print("Item 2.2 clicked"))
        section3 = self.accordion.add_section("Section 3", lambda: print("Section 3 clicked"), [element1, element2])
        self.assertEqual(len(section3.sub_elements), 2)
        self.assertEqual(section3.sub_elements[0], element1)
        self.assertEqual(section3.sub_elements[1], element2)
        self.assertEqual(len(self.accordion.sections), 3)
        self.assertEqual(self.accordion.sections[2], section3)

        frame.destroy()

    def test_remove_section(self):
        section = self.accordion.add_section("Section 1", lambda: print("Section 1 clicked"))
        self.accordion.remove_section(section)
        self.assertEqual(len(self.accordion.sections), 0)

    def test_update_canvas_width(self):
        section = self.accordion.add_section("Section 1", lambda: print("Section 1 clicked"))
        element = section.add_element("Item 1.1 long text", lambda: print("Item 1.1 clicked"))
        # collapsed
        self.accordion.update_canvas_width()
        collapsed_width = self.accordion.scrollable_frame.winfo_reqwidth()

        # expanded
        section.toggle_element()
        element.toggle_element()
        self.accordion.update_canvas_width()
        self.assertGreater(self.accordion.scrollable_frame.winfo_width(), section.collapse_btn.winfo_reqwidth())
        self.assertGreater(self.accordion.scrollable_frame.winfo_reqwidth(), collapsed_width)

    def test_reorder(self):
        section1 = self.accordion.add_section("Section 1", lambda: print("Section 1 clicked"))
        section2 = self.accordion.add_section("Section 2", lambda: print("Section 2 clicked"))
        element1 = section1.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
        element2 = section1.add_element("Item 1.2", lambda: print("Item 1.2 clicked"))
        element3 = section2.add_element("Item 2.1", lambda: print("Item 2.1 clicked"))

        # collapsed
        self.accordion.reorder()

        self.assertEqual(section1.row, 0)
        self.assertEqual(element1.row, 0)
        self.assertEqual(element2.row, 0)
        self.assertEqual(section2.row, 1)
        self.assertEqual(element3.row, 0)

        # expanded
        section1.toggle_element()
        section2.toggle_element()
        element1.toggle_element()
        element2.toggle_element()
        element3.toggle_element()
        self.accordion.reorder()

        self.assertEqual(section1.row, 0)
        self.assertEqual(element1.row, 0)
        self.assertEqual(element2.row, 2)
        self.assertEqual(section2.row, 2)
        self.assertEqual(element3.row, 0)

    def test_create_style(self):
        style_name = "Custom1.TButton"
        level = 1
        self.accordion.create_style(style_name, level)
        style = ttk.Style()
        self.assertEqual(style.lookup(style_name, 'font'), "Helvetica 9")
        self.assertEqual(style.lookup(style_name, 'padding'), "0 0")
        self.assertEqual(style.lookup(style_name, 'relief'), "flat")
        self.assertEqual(style.lookup(style_name, 'background'), '#e0e0e0')
        self.assertEqual(style.map(style_name, 'background'), [('active', '#d0d0d0')])
        self.assertEqual(style.map(style_name, 'foreground'), [('active', '#000000')])

    def test_destroy(self):
        accordion = Accordion(self.root)
        section1 = accordion.add_section("Section 1", lambda: print("Section 1 clicked"))
        section2 = accordion.add_section("Section 2", lambda: print("Section 2 clicked"))
        element1 = section1.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
        element2 = section1.add_element("Item 1.2", lambda: print("Item 1.2 clicked"))
        element3 = section2.add_element("Item 2.1", lambda: print("Item 2.1 clicked"))

        self.assertEqual(len(accordion.sections), 2)
        self.assertEqual(len(section1.sub_elements), 2)
        self.assertEqual(len(section2.sub_elements), 1)

        accordion.destroy()

        self.assertFalse(accordion.winfo_exists())
        self.assertFalse(section1.winfo_exists())
        self.assertFalse(section2.winfo_exists())
        self.assertFalse(element1.winfo_exists())
        self.assertFalse(element2.winfo_exists())
        self.assertFalse(element3.winfo_exists())

if __name__ == "__main__":
    unittest.main()