import tkinter as tk
from ui.constants import *
import webbrowser
import gc

WIN_ABOUT_WIDTH = 375
WIN_ABOUT_HEIGHT = 180


class UI_AboutWindow(tk.Toplevel):

    def __init__(self, root, **kw):
        super().__init__(root, background=GUI_BG_COLOR, **kw)
        # Widgets
        self.root = root
        # Create UI
        self.withdraw()
        self.__ui_create()
        self.deiconify()

    def __ui_create(self):
        self.resizable(False, False)
        self.title('About')
        self.iconbitmap(ICON_APP)
        self.protocol("WM_DELETE_WINDOW", self.__ui_quit)
        # Create UI
        self.canvas = tk.Canvas(self, width=WIN_ABOUT_WIDTH, height=WIN_ABOUT_HEIGHT,
                                bg=GUI_BG_COLOR, cursor='arrow', highlightthickness=0,
                                highlightbackground=GUI_FONT_COLOR)
        self.image_file_logo = tk.PhotoImage(file=ICON_KAPTAR_LOGO)
        self.label_logo = tk.Label(self.canvas, image=self.image_file_logo, background=GUI_BG_COLOR, width=150,
                                   height=150, bd=1, justify=tk.CENTER)
        self.canvas.create_window(25, 15, anchor=tk.NW, window=self.label_logo)
        self.canvas.create_text(200, 15, anchor=tk.NW, text=f'{GUI_TITLE}', font=GUI_FONT_CONTENT)
        self.canvas.create_text(200, 35, anchor=tk.NW, text=f'Version: {GUI_VERSION}', font=GUI_FONT_CONTENT)
        self.canvas.create_text(200, 55, anchor=tk.NW, text=f'Kaptar \xA9 2023', font=GUI_FONT_CONTENT)
        self.label_link = tk.Label(self.canvas, background=GUI_BG_COLOR, cursor='hand2',
                                   font=GUI_FONT_CONTENT, text='https://www.kaptar.io/')
        self.press_cid = self.label_link.bind('<Button-1>', lambda e: webbrowser.open_new('https://www.kaptar.io/'))
        self.canvas.create_window(197, 137, anchor=tk.NW, window=self.label_link)
        self.canvas.pack()
        # Positioning toplevel
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.update_idletasks()
        x_offset = (GUI_TOTAL_WIDTH - self.winfo_width()) // 2
        y_offset = (GUI_HEIGHT - self.winfo_height()) // 2
        self.geometry('+%d+%d' % (x + x_offset, y + y_offset))

    def __ui_quit(self):
        self.label_link.unbind('<Button-1>', self.press_cid)
        self.label_link.destroy()
        self.label_logo.destroy()
        del self.image_file_logo
        del self.press_cid
        del self.label_link
        del self.label_logo
        gc.collect(1)
        self.destroy()
