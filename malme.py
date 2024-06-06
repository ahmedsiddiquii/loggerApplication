from ui.main_window import *
from ttkthemes import ThemedTk
from tkinter import messagebox as mb
from tendo import singleton
import gc
import os
import sys
import ctypes

if 'nt'.__eq__(os.name):
    theme = 'vista'
else:
    theme = 'radiance'


def is_admin() -> bool:
    try:
        ret = (os.getuid() == 0)
    except AttributeError:
        ret = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return ret


def run_as_admin():
    try:
        if 'win32' in sys.platform:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        else:
            subprocess.Popen(['sudo', sys.executable] + sys.argv)
        sys.exit()
    except Exception as e:
        ThemedTk().withdraw()
        mb.showerror(title='Error', message='Run application with admin privileges!')
        sys.exit()


if __name__.__eq__('__main__'):
    try:
        si = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        ThemedTk().withdraw()
        mb.showerror(title='Error', message='Another application instance is already running!')
        sys.exit()

    if not is_admin():
        ThemedTk().withdraw()
        run_as_admin()
        
    root = ThemedTk(theme=theme)
    root.tk.call('tk', 'scaling', 1.33)
    root.withdraw()
    ui_main_window = UI_MainWindow(root)
    gc.disable()
    # Mainloop
    ui_main_window.ui_start_mainloop()
