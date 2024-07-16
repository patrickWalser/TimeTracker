import tkinter as tk
from tkinter import ttk


class Accordion_Element(ttk.Frame):
    '''Is an Element in an Accordion

    Extends ttk.Frame
    Has a Button and a Frame for potential sub_elements.
    Clicking the button shows the Frame with subelememts, calls
    a specific command and reorders the accordion.
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

        # Create button for the element
        style_name = f'Custom{level}.TButton'
        self.accordion.create_style(style_name, level)

        self.element_btn = ttk.Button(self, text=name, style=style_name)
        self.element_btn.grid(row=self.row, column=0,
                              sticky='ew', padx=level * 10, pady=(0, 2))

        # Create frame for sub-elements
        self.sub_element_frame = ttk.Frame(self)
        self.sub_element_frame.grid(row=self.row + 1, column=0, sticky='ew')
        self.sub_element_frame.grid_remove()

        self.element_btn.config(command=lambda: self.toggle_element(command))

    def toggle_element(self, command):
        '''click event of the button

        visible state of the element is toggled
        accordion is reordered
        specific command is called
        '''
        self.visible = not self.visible
        self.accordion.reorder()
        command()

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

        name: the name
        command: the command tobe executet at the click ecent
        sub_elements: list of sub_elements

        returns: the generated element
        '''
        e = Accordion_Element(self.accordion, self.sub_element_frame, name,
                              command=command, sub_elements=sub_elements, level=self.level + 1)
        self.sub_elements.append(e)
        return e

    def destroy(self):
        ''' destroys the element and its sub_elements'''
        for e in self.sub_elements:
            e.destroy()
        self.sub_element_frame.destroy()
        self.element_btn.destroy()
        super().destroy()


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
        return s

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

    def destroy(self):
        ''' destroy all sections and the accordion '''
        for s in self.sections:
            s.destroy()
        super().destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Modern Accordion Navigation Bar")

    accordion = Accordion(root)
    accordion.pack(fill='both', expand=True)

    # Example elements with multiple levels
    s = accordion.add_section("Section 1", lambda: print("Section 1 clicked"))
    e = s.add_element("Item 1.1", lambda: print("Item 1.1 clicked"))
    e = s.add_element("Item 1.2", lambda: print("Item 1.2 clicked"))
    e1 = e.add_element("Item 1.2.1", lambda: print("Item 1.2.1 clicked"))

    s = accordion.add_section("Section 2", lambda: print("Section 2 clicked"))
    e = s.add_element("Item 2.1", lambda: print("Item 2.1 clicked"))
    e = s.add_element("Item 2.2", lambda: print("Item 2.2 clicked"))
    e1 = e.add_element("Item 2.2.1", lambda: print("Item 2.2.1 clicked"))

    root.mainloop()
