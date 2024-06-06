import tkinter as tk
import tkinter.ttk as ttk
from ui.constants import *
from datetime import datetime
from textwrap import wrap

POPUP_WIDTH = 200
POPUP_HEIGHT = 200
POPUP_BG_COLOR = '#ffcccc'


class UI_PopUp(tk.Toplevel):

    def __init__(self, root, message, **kw):
        super().__init__(root, **kw)
        self.root = root
        self.message = message
        self.withdraw()
        self.overrideredirect(True)
        self.resizable(False, False)
        self.attributes('-topmost', 'true')
        # Setting initial position of the window
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        x_offset = GUI_TOTAL_WIDTH - POPUP_WIDTH
        y_offset = 50
        self.geometry('+%d+%d' % (x + x_offset, y + y_offset))
        # Creating UI
        self.__ui_create()
        self.deiconify()
        # Editing the message by adding line breaks if needed
        self.root.update()
        char_width = self.label_message.winfo_width() / len(message)
        wrapped_message = '\n'.join(wrap(message, int(POPUP_WIDTH / char_width)))
        self.label_message['text'] = wrapped_message
        # Sticking this pop-up window to the root window
        self.bind_id = self.root.bind('<Configure>', self.__sync_windows, '+')

    def __ui_create(self):
        self.canvas = tk.Canvas(self, width=POPUP_WIDTH, height=POPUP_HEIGHT, background=POPUP_BG_COLOR)
        self.canvas.pack(expand=True, fill='both')
        error_time = datetime.now().strftime('%H:%M:%S')
        self.label_time = ttk.Label(self.canvas, text=error_time, justify=tk.CENTER, font=GUI_FONT_CONTENT,
                                    background=POPUP_BG_COLOR)
        self.canvas.create_window(POPUP_WIDTH / 2, 20, anchor=tk.CENTER, window=self.label_time)
        self.label_message = ttk.Label(self.canvas, text=self.message, justify=tk.CENTER, font=GUI_FONT_CONTENT,
                                       background=POPUP_BG_COLOR)
        self.canvas.create_window(POPUP_WIDTH / 2, POPUP_HEIGHT / 2, anchor=tk.CENTER, window=self.label_message)
        self.label_message.update_idletasks()
        self.button_ok = ttk.Button(self.canvas, text='OK', command=self.__delete)
        self.canvas.create_window(POPUP_WIDTH / 2, POPUP_HEIGHT - 20, anchor=tk.CENTER, window=self.button_ok)

    def __delete(self):
        self.__unbind('<Configure>', self.bind_id)
        self.destroy()

    def __sync_windows(self, event):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        x_offset = GUI_TOTAL_WIDTH - POPUP_WIDTH
        y_offset = 50
        self.geometry('+%d+%d' % (x + x_offset, y + y_offset))

    # This method overrides standard unbind method of class Tk because it doesn't work properly
    def __unbind(self, sequence, funcid=None):
        if not funcid:
            self.root.tk.call('bind', self.root._w, sequence, '')
            return
        func_callbacks = self.root.tk.call(
            'bind', self.root._w, sequence, None).split('\n')
        new_callbacks = [
            l for l in func_callbacks if l[6:6 + len(funcid)] != funcid]
        self.root.tk.call('bind', self.root._w, sequence, '\n'.join(new_callbacks))
        self.root.deletecommand(funcid)
