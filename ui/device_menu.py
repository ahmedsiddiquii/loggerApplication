from tkinter import ttk
from tkinter import *
from ui.constants import *
from ui.tab_home import UI_TabHome
from ui.tab_graph import UI_TabGraph
from ui.tab_program import UI_TabProgram
from ui.tab_histogram import UI_TabHistogram
from ui.tab_table import UI_TabTable
from ui.tab_summary import UI_TabSummary
from threading import Thread
import gc


class UI_DeviceMenu(ttk.Notebook):

    def __init__(self, parent, device, **kw):
        super().__init__(parent, height=GUI_HEIGHT + 18, width=GUI_DEVICE_SETTINGS_WIDTH, **kw)
        self.device = device
        self.tab_home = UI_TabHome(self)
        self.tab_program = UI_TabProgram(self)
        self.tab_program.set_button_program_callback(self.program_device)
        self.tab_graph = UI_TabGraph(self)
        self.tab_histogram = UI_TabHistogram(self)
        self.tab_table = UI_TabTable(self)
        self.tab_summary = UI_TabSummary(self)
        self.add(self.tab_home, text='Home')
        #self.add(self.tab_program, text='Program')
        self.add(self.tab_graph, text='Graph')
        self.add(self.tab_histogram, text='Histogram')
        self.add(self.tab_table, text='Table')
        self.add(self.tab_summary, text='Summary')

    def program_device(self):
        Thread(target=self.device.program_data_to_device).start()

    def ui_start(self):
        self.pack(expand=True, fill='both')

    def ui_stop(self):
        self.pack_forget()

    def ui_delete(self):
        # Enable probably being disabled tabs back to normal state to avoid a strange exception
        self.tab(2, state='normal')
        self.tab(3, state='normal')
        self.tab(4, state='normal')
        self.ui_stop()
        self.tab_home.ui_delete()
        self.tab_program.ui_delete()
        self.tab_graph.ui_delete()
        self.tab_histogram.ui_delete()
        self.tab_table.ui_delete()
        self.tab_summary.ui_delete()
        del self.tab_home
        del self.tab_program
        del self.tab_graph
        del self.tab_histogram
        del self.tab_table
        del self.tab_summary
        self.destroy()
        gc.collect()
