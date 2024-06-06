from tkinter import *
from ui.constants import *

HINT_WIDTH = 360
HINT_HEIGHT = 56


class UI_HintNoDevices:

    def __init__(self, parent):
        self.canvas_hint = Canvas(parent, width=GUI_DEVICE_TREE_WIDTH - 2, height=DEVICE_MENU_HEIGHT, bg=MENU_BG_COLOR,
                                  cursor='arrow', highlightthickness=1, highlightbackground=GUI_FONT_COLOR)
        self.canvas_hint.create_text(GUI_DEVICE_TREE_WIDTH / 2, DEVICE_MENU_HEIGHT / 2, anchor=CENTER,
                                     text='No devices connected yet', font=GUI_FONT_CONTENT,
                                     justify=CENTER, fill=GUI_FONT_COLOR)

    def start(self):
        self.canvas_hint.pack(side='top', pady=2)

    def stop(self):
        self.canvas_hint.pack_forget()
