import tkinter as tk
from tkinter import ttk

class Accordion_Element(ttk.Frame):
    '''Is an Element in an Accordion

    Extends ttk.Frame
    Has two Buttons and a Frame for potential sub_elements.
    Clicking the first button calls a specific command
    Clicking the second button shows the Frame with subelememts
    and reorders the accordion.
    Holds a list of sub_elements
    '''

    def __init__(self, accordion, parent, name, command, sub_elements=None, level=0, row=0):
        '''constructor of accordion element

        accordion: the accordion
        parent: the parent frame
        name: name of the element (= text of the button)
        command: command to execute at button click event
        sub_elements: list of sub_elements
        level: the level of the element inside the accordion
        row: row inside the grid (is set at reordereing)
        '''
        super().__init__(parent)
        self.grid(sticky='ew')

        self.sub_elements = []
        if sub_elements is not None:
            self.sub_elements.extend(sub_elements)

        self.name = name
        self.level = level
        self.row = row
        self.visible = False
        self.parent = parent
        self.accordion = accordion

        # Create buttons for the element
        style_name = f'Custom{level}.TButton'
        self.accordion.create_style(style_name, level)

        self.element_btn = ttk.Button(self, text=name, style=style_name)
        self.element_btn.grid(row=self.row, column=0,
                              sticky='ew', padx=level * 10, pady=(0, 2))

        self.collapse_btn = ttk.Button(
            self, text="+", style=style_name, width=2)
        self.collapse_btn.grid(row=self.row, column=1,
                               sticky="e", padx=0, pady=(0, 0))

        # Create frame for sub-elements
        self.sub_element_frame = ttk.Frame(self)
        self.sub_element_frame.grid(row=self.row + 1, column=0, sticky='ew')
        self.sub_element_frame.grid_remove()

        self.element_btn.config(command=lambda: command())
        self.collapse_btn.config(command=lambda: self.toggle_element())

    def __eq__(self, other):
        '''can be used to compare Accordion_Element objects

        check is done based on the equality of the properties

        other: instance to be checked for equality

        returns: True if equal False if not
                  NotImplemented if other is no AccordionElement
        '''
        if not isinstance(other, Accordion_Element):
            return NotImplemented

        return self.name == other.name and self.level == other.level \
            and self.row == other.row and self.visible == other.visible \
            and self.parent == other.parent and self.accordion == other.accordion

    def toggle_element(self):
        '''click event of the button

        visible state of the element is toggled
        accordion is reordered
        text of the collapse button is toggled
        '''
        self.visible = not self.visible
        if (self.visible):
            self.collapse_btn.config(text="-")
        else:
            self.collapse_btn.config(text="+")

        self.accordion.reorder()

    def reorder(self, row=0):
        '''reoerder the element

        uses recursion to order all underlaying elements

        row: row to start

        returns next row
        '''
        # order the button
        self.row = row
        self.element_btn.grid(row=row, column=0, sticky='ew',
                              padx=self.level * 10, pady=(0, 2))

        if len(self.sub_elements) > 0:
            self.collapse_btn.grid(
                row=self.row, column=1, sticky="e", padx=0, pady=(0, 2))
        else:
            self.collapse_btn.grid_remove()

        row += 1
        if self.visible:
            # show and order the sub_elements_frame
            self.sub_element_frame.grid(row=row, column=0, sticky='ew')
            row += 1

            # reorder the sub_elements
            sub_row = 0
            for elem in self.sub_elements:
                sub_row = elem.reorder(sub_row)
        else:
            self.sub_element_frame.grid_remove()

        return row

    def add_element(self, name, command, sub_elements=None):
        ''' add a sub_element

        updates the accordion width

        name: the name
        command: the command tobe executet at the click ecent
        sub_elements: list of sub_elements

        returns: the generated element
        '''
        e = Accordion_Element(self.accordion, self.sub_element_frame, name,
                              command=command, sub_elements=sub_elements, level=self.level + 1)
        self.sub_elements.append(e)
        self.accordion.update_canvas_width()
        return e
    def remove_element(self, element):
        ''' remove a sub_element
        
        updates the accordion width

        element: the Accordion_Element to remove
        '''

        self.sub_elements.remove(element)
        element.destroy()
        self.accordion.update_canvas_width()

    def destroy(self):
        ''' destroys the element and its sub_elements'''
        for e in self.sub_elements:
            e.destroy()

        self.sub_element_frame.destroy()
        self.element_btn.destroy()
        super().destroy()
        del self


class Accordion(ttk.Frame):
    ''' Accordion holding elements

    Extends ttk.Frame
    provides a Frame containing the elements and a scrollbar
    Holds a list of the sections
    '''

    def __init__(self, parent):
        ''' constructor of the accordion

        parent: the parent frame
        '''
        super().__init__(parent)

        self.canvas = tk.Canvas(self, width=150)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # bind scroll event
        self.bind_mouse_scroll(self.canvas)
        self.bind_mouse_scroll(self.scrollable_frame)

        self.sections = []

    def bind_mouse_scroll(self, widget):
        ''' bind the scroll event to the widget'''
        widget.bind_all("<MouseWheel>", self._on_mouse_wheel)  # Windows
        widget.bind_all("<Button-4>", self._on_mouse_wheel)    # Unix
        widget.bind_all("<Button-5>", self._on_mouse_wheel)    # Unix

    def _on_mouse_wheel(self, event):
        ''' the scroll event

        handles unix and windows scrolling
        only scrolls if canvas is too big for the available space
        '''
        if self.canvas.bbox("all")[3] > self.winfo_height():
            if event.num == 4:  # Unix scroll up
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Unix scroll down
                self.canvas.yview_scroll(1, "units")
            else:  # Windows
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def add_section(self, name, command, sub_elements=None):
        ''' add a section to the accordion

        a section is also an Accordion_Element but at the highest level
        adds the section to the section_list
        reorders the accordion
        updates the width

        name: the name of the section
        command: the command to be executed at the click event
        sub_elements: list of sub elements

        returns: the created section
        '''
        s = Accordion_Element(self, self.scrollable_frame,
                              name, command=command, sub_elements=sub_elements)
        s.grid(row=len(self.sections), column=0, sticky='ew')
        self.sections.append(s)
        self.reorder()
        self.update_canvas_width()
        return s

    def remove_section(self, section):
        ''' remove an element
        
        updates the accordion width

        section: the Accordion_Element to remove
        '''

        self.sections.remove(section)
        section.destroy()
        self.reorder()
        self.update_canvas_width()

    def reorder(self):
        ''' reorder the accordion

        reorder each section
        '''
        row = 0
        for s in self.sections:
            row = s.reorder(row)

    def create_style(self, style_name, level):
        ''' creates a style for the defined level of the accordion element 

        style_name: the name of the style (must end with T.Button for buttons)
        level: the level of the element
        '''
        style = ttk.Style()
        font_size = 10 - level
        style.configure(style_name, font=("Helvetica", font_size), padding=(
            0, 0), relief="flat", background='#e0e0e0')
        style.map(style_name, background=[
                  ('active', '#d0d0d0')], foreground=[('active', '#000000')])

    def update_canvas_width(self):
        ''' update the canvas width based on the width of the widest element.'''
        self.canvas.update_idletasks()
        # find the maximum width
        max_width = 0
        for section in self.sections:
            width = section.element_btn.winfo_reqwidth() + \
                section.collapse_btn.winfo_reqwidth() + \
                section.level * 10 + 20  # Including padding
            max_width = max(max_width, width)
            for elem in section.sub_elements:
                width = elem.element_btn.winfo_reqwidth() + \
                    elem.collapse_btn.winfo_reqwidth() + \
                    elem.level * 10 + 20  # Including padding
                max_width = max(max_width, width)
                for sub_elem in elem.sub_elements:
                    width = sub_elem.element_btn.winfo_reqwidth() + \
                        sub_elem.collapse_btn.winfo_reqwidth() + \
                        sub_elem.level * 10 + 20  # Including padding
                    max_width = max(max_width, width)

        # configure canvas
        self.canvas.config(width=max_width)
        self.canvas.itemconfig(self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor='nw'), width=max_width)

    def destroy(self):
        ''' destroy all sections and the accordion '''
        for s in self.sections:
            s.destroy()

        super().destroy()
        del self


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Accordion Navigation Bar")

    frame = ttk.Frame(root)
    frame.grid(row=0, sticky='news')
    accordion = Accordion(frame)
    accordion.grid(row=0, column=0, sticky='ns')
    # accordion.pack(fill='both', expand=True)

    # Example elements with multiple levels
    s = accordion.add_section("Section 1", lambda: print("Section 1 clicked"))
    e = s.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
    e = s.add_element("Item 1.2", lambda: print("Item 1.2 clicked"))
    e1 = e.add_element("Item 1.2.1", lambda: print("Item 1.2.1 clicked"))

    s = accordion.add_section("Section 2", lambda: print("Section 2 clicked"))
    e = s.add_element("Item 2.1", lambda: print("Item 2.1 clicked"))
    e = s.add_element("Item 2.2", lambda: print("Item 2.2 clicked"))
    e1 = e.add_element("Item 2.2.1", lambda: print("Item 2.2.1 clicked"))

    accordion.reorder()

    root.mainloop()
