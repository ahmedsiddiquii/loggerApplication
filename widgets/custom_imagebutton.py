import tkinter as tk
from tkinter import CENTER
from idlelib.tooltip import Hovertip
import gc


class CustomImageButton(tk.Label):
    shape = None

    def __init__(self, parent, width, height, bgcolor, image_active, image_inactive=None,
                 tip=None, command=None, args=(), **kw):
        self.state = 'ENABLED'
        self.command = command
        self.args = args
        if image_inactive is None:
            image_inactive = image_active
        self.image_file_active = tk.PhotoImage(file=image_active)
        self.image_file_inactive = tk.PhotoImage(file=image_inactive)
        self.image = self.image_file_active
        super().__init__(parent, image=self.image_file_active, background=bgcolor, width=width,
                         height=height, bd=1, justify=CENTER, cursor='hand2', **kw)
        self.ht = None
        if tip is not None:
            self.ht = Hovertip(self, tip)
        self.press_cid = self.bind('<ButtonPress>', self.__on_press, '+')
        self.release_cid = self.bind('<ButtonRelease>', self.__on_release, '+')

    def __on_press(self, event):
        if self.state.__eq__('ENABLED'):
            self.configure(relief='groove')
        elif self.state.__eq__('DISABLED'):
            pass

    def __on_release(self, event):
        if self.state.__eq__('ENABLED'):
            self.configure(relief='flat')
            if self.command is not None:
                self.command(*self.args)
        elif self.state.__eq__('DISABLED'):
            pass

    def set_state(self, new_state):
        if new_state.__eq__('DISABLED'):
            self.state = 'DISABLED'
            self.configure(image=self.image_file_inactive, cursor='arrow')
            self.image = self.image_file_inactive
        elif new_state.__eq__('ENABLED'):
            self.state = 'ENABLED'
            self.configure(image=self.image_file_active, cursor='hand2')
            self.image = self.image_file_active

    def swap_icons(self):
        if self.image == self.image_file_active:
            self.configure(image=self.image_file_inactive)
            self.image = self.image_file_inactive
        else:
            self.configure(image=self.image_file_active)
            self.image = self.image_file_active

    def bind_command(self, command, args=()):
        self.command = command
        self.args = args

    def destroy(self):
        self.unbind('<ButtonPress>', self.press_cid)
        self.unbind('<ButtonRelease>', self.release_cid)
        del self.press_cid
        del self.release_cid
        del self.command
        del self.args
        del self.image
        del self.image_file_active
        del self.image_file_inactive
        if self.ht is not None:
            del self.ht
        super().destroy()
        del self
        gc.collect(1)