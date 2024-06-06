import tkinter as tk
from math import ceil
from ui.constants import *

class RadioGroup():
    def __init__(self):
        self.groupsList = []
        self.numberOfGroups = 0

    def add_group(self, lastSelectedRadiobox=None):
        self.groupsList.append(lastSelectedRadiobox)
        self.numberOfGroups += 1


class CustomRadiobox(tk.Canvas):

    def __init__(self,
                 parent,
                 width,
                 boxsize=10,
                 borderwidth=3,
                 cornerradius=10,
                 maincolor='red',
                 bgcolor='green',
                 padding=5,
                 text='Some text',
                 group=None,
                 groupClass=None,
                 textcolor=None,
                 oncheck=None,
                 args=()):
        self.parent = parent
        self.width = width
        self.boxSize = boxsize
        self.borderWidth = borderwidth
        self.cornerRadius = cornerradius
        self.mainColor = maincolor
        self.bgColor = bgcolor
        self.focusedColor = '#3a75c4'
        self.checked = False
        self.padding = padding
        self.text = text
        self.groupNumber = group
        self.groupClass = groupClass
        self.commandOnCheck = oncheck
        self.commandArgs = args
        if textcolor is None:
            self.textColor = self.mainColor
        else:
            self.textColor = textcolor
        tk.Canvas.__init__(self, parent,
                           borderwidth=0,
                           relief='flat',
                           highlightthickness=0,
                           bg=self.bgColor,
                           height=self.boxSize + self.borderWidth / 2,
                           width=self.width)
        self.config(cursor='hand2')
        self.checkbox = self.create_oval((self.borderWidth / 2, self.borderWidth / 2),
                                         (self.boxSize, self.boxSize),
                                         fill=self.bgColor,
                                         outline=self.mainColor,
                                         width=self.borderWidth)
        self.check = None

        def _on_mouse_over(event):
            self.itemconfig(self.checkbox, fill=self.focusedColor)
            if self.check is not None:
                self.itemconfig(self.check, fill=self.bgColor)

        def _on_mouse_away(event):
            self.itemconfig(self.checkbox, fill=self.bgColor)
            if self.check is not None:
                self.itemconfig(self.check, fill=self.mainColor)

        def _on_mouse_click(event):
            if self.checked.__eq__(False):
                if self.groupNumber.__ne__(None) and self.groupClass.__ne__(None):
                    if (self.groupClass.groupsList[self.groupNumber]).__ne__(None):
                        self.groupClass.groupsList[self.groupNumber].uncheck()
                    self.groupClass.groupsList[self.groupNumber] = self
                self._draw_check()
                self.checked = True
            else:
                #self.delete(self.check)
                #self.checked = False
                pass
            if self.commandOnCheck is not None:
                self.commandOnCheck(*self.commandArgs)

        self.bind('<Enter>', _on_mouse_over)
        self.bind('<Leave>', _on_mouse_away)
        self.bind('<ButtonPress-1>', _on_mouse_click)

        self.create_text(self.boxSize + self.padding, self.boxSize / 2,
                         anchor=tk.W,
                         text=self.text,
                         font=GUI_FONT_CONTENT,
                         fill=self.textColor)

    def _draw_check(self):
        '''self.check = self.create_line((self.boxSize * 0.2 + self.borderWidth / 2, self.boxSize * 0.5),
                                      (self.boxSize * 0.4 + self.borderWidth / 2, self.boxSize * (1 - 0.2)),
                                      (self.boxSize * (1 - 0.2), self.boxSize * 0.2 + self.borderWidth / 2),
                                      fill=self.mainColor,
                                      width=ceil(self.borderWidth * 1.5))'''
        self.check = self.create_oval((self.boxSize * 0.3 + self.borderWidth / 2, self.boxSize * 0.3 + self.borderWidth / 2),
                                      (self.boxSize * 0.7, self.boxSize * 0.7),
                                      fill=self.bgColor)

    def get(self):
        return self.checked

    def uncheck(self):
        self.delete(self.check)
        self.checked = False

    def set(self):
        if self.groupNumber.__ne__(None) and self.groupClass.__ne__(None):
            if (self.groupClass.groupsList[self.groupNumber]).__ne__(None):
                self.groupClass.groupsList[self.groupNumber].uncheck()
            self.groupClass.groupsList[self.groupNumber] = self
        self._draw_check()
        self.itemconfig(self.check, fill=self.mainColor)
        if self.commandOnCheck is not None:
            self.commandOnCheck(*self.commandArgs)
        self.checked = True

    def bind_command(self, command, args=()):
        self.commandOnCheck = command
        self.commandArgs = args