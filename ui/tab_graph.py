from tkinter import *
from tkinter import ttk
from tkinter.filedialog import asksaveasfile
from ui.constants import *
from ui.zoom_pan import ZoomPan
from communication.data_structure import Structure_Configuration, Container_Recordings, DataEnums
from widgets.custom_imagebutton import CustomImageButton
import matplotlib
import numpy as np
import gc

matplotlib.use('TkAgg')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class UI_TabGraph(ttk.Frame):

    def __init__(self, main_window, **kw):
        super().__init__(main_window, **kw)
        # Widgets
        self.main_window = main_window
        self.united_canvas = None
        self.united_figure = None
        self.temperature_plot = None
        self.humidity_plot = None
        self.notebook = None
        self.image_button_grid = None
        self.temp_thr_lo_line = None
        self.temp_thr_hi_line = None
        self.hum_thr_lo_line = None
        self.hum_thr_hi_line = None
        self.temp_lines = None
        self.hum_lines = None
        self.temp_book_lines = None
        self.temp_tamp_lines = None
        self.hum_book_lines = None
        self.hum_tamp_lines = None
        # Parameters
        self.recordings = None
        self.configuration = None
        self.temp_high: float = 0.0
        self.temp_low: float = 0.0
        self.hum_high: float = 0.0
        self.hum_low: float = 0.0
        # Settings
        self.grid_state: bool = True
        self.legend_state: bool = True
        self.is_update_enabled: bool = True
        self.zp = None
        # Rendering UI
        self.__ui_create()
        self.__ui_start()
        self.__touch_graph()

    def __ui_create(self):
        self.notebook = ttk.Notebook(self)
        self.united_figure = Figure()
        self.united_figure.patch.set_facecolor(GUI_BG_COLOR)
        # Creating temperature graph
        if self.temperature_plot is None:
            self.temperature_plot = self.united_figure.add_subplot(211)
        # Creating humidity graph
        if self.humidity_plot is None:
            self.humidity_plot = self.united_figure.add_subplot(212)
        # Adding grid if required
        if self.grid_state is True:
            self.temperature_plot.xaxis.grid(True, which='major')
            self.temperature_plot.yaxis.grid(True, which='major')
            self.humidity_plot.xaxis.grid(True, which='major')
            self.humidity_plot.yaxis.grid(True, which='major')

    def __ui_create_temperature_graph(self):
        self.temperature_plot.clear()
        # Setting x-axis format to date
        date_format_mask = DataEnums.date_format_mask.get(self.configuration.date_fmt,
                                                          DataEnums.date_format_mask.get(0))
        time_format_mask = DataEnums.time_format_mask.get(self.configuration.time_fmt,
                                                          DataEnums.time_format_mask.get(0))
        datetime_format = mdates.DateFormatter(f'{date_format_mask}\n{time_format_mask}')
        self.temperature_plot.xaxis.set_major_formatter(datetime_format)
        self.temperature_plot.xaxis.set_major_locator(plt.LinearLocator(7))
        self.temperature_plot.tick_params(axis='both', labelsize=9)
        # Plotting
        self.temp_lines = self.temperature_plot.plot_date(self.recordings.timestamp, self.recordings.temperature,
                                                          xdate=True,
                                                          fmt='-', color='black', label='Temperature', linewidth=1)
        __th = np.repeat(self.temp_high, len(self.recordings.temperature))
        __tl = np.repeat(self.temp_low, len(self.recordings.temperature))
        if self.temp_high.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            self.temperature_plot.fill_between(self.recordings.timestamp, self.recordings.temperature, self.temp_high,
                                               where=self.recordings.temperature >= __th,
                                               interpolate=True, color=GRAPH_HIGH_THR_COLOR, label='High alert')
            self.temp_thr_lo_line = self.temperature_plot.axhline(y=self.temp_high, color=GRAPH_HIGH_THR_COLOR,
                                                                  linestyle='--')
        if self.temp_low.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            self.temperature_plot.fill_between(self.recordings.timestamp, self.recordings.temperature, self.temp_low,
                                               where=self.recordings.temperature <= __tl,
                                               interpolate=True, color=GRAPH_LOW_THR_COLOR, label='Low alert')
            self.temp_thr_hi_line = self.temperature_plot.axhline(y=self.temp_low, color=GRAPH_LOW_THR_COLOR,
                                                                  linestyle='--')
        # Adding 'tampered' and 'bookmark' marks
        self.temp_book_lines = self.temperature_plot.plot_date(self.recordings.timestamp, self.recordings.temperature,
                                                               xdate=True, marker='o', markerfacecolor='g', fmt='',
                                                               markevery=list(map(bool, self.recordings.is_bookmark)),
                                                               label='Bookmark', color='black', alpha=0.7)
        self.temp_tamp_lines = self.temperature_plot.plot_date(self.recordings.timestamp, self.recordings.temperature,
                                                               xdate=True, marker='o', markerfacecolor='r', fmt='',
                                                               markevery=list(map(bool, self.recordings.is_tampered)),
                                                               label='Tampered', color='black', alpha=0.7)
        # Adding legend and axis labels
        self.temperature_plot.legend(loc=1)
        # self.temperature_plot.set_xlabel('Date & Time', fontsize=9)
        self.temperature_plot.set_ylabel(f'Temperature, '
                                         f'\u00b0{DataEnums.temperature_unit_t[self.configuration.temp_unit][:1]}',
                                         fontsize=9)
        # Adding grid if required
        if self.grid_state is True:
            self.temperature_plot.xaxis.grid(True, which='major')
            self.temperature_plot.yaxis.grid(True, which='major')
        # Clear memory
        del __th, __tl
        del datetime_format, date_format_mask, time_format_mask
        gc.collect(1)

    def __ui_create_humidity_graph(self):
        self.humidity_plot.clear()
        # Setting x-axis format to date
        date_format_mask = DataEnums.date_format_mask.get(self.configuration.date_fmt,
                                                          DataEnums.date_format_mask.get(0))
        time_format_mask = DataEnums.time_format_mask.get(self.configuration.time_fmt,
                                                          DataEnums.time_format_mask.get(0))
        datetime_format = mdates.DateFormatter(f'{date_format_mask}\n{time_format_mask}')
        self.humidity_plot.xaxis.set_major_formatter(datetime_format)
        self.humidity_plot.xaxis.set_major_locator(plt.LinearLocator(7))
        self.humidity_plot.tick_params(axis='both', labelsize=9)
        # Plotting
        self.hum_lines = self.humidity_plot.plot_date(self.recordings.timestamp, self.recordings.humidity, xdate=True,
                                                      fmt='-', color='black', label='Humidity', linewidth=1)
        __th = np.repeat(self.hum_high, len(self.recordings.humidity))
        __tl = np.repeat(self.hum_low, len(self.recordings.humidity))
        if self.hum_high.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            self.humidity_plot.fill_between(self.recordings.timestamp, self.recordings.humidity, self.hum_high,
                                            where=self.recordings.humidity >= __th,
                                            interpolate=True, color=GRAPH_HIGH_THR_COLOR, label='High alert')
            self.hum_thr_hi_line = self.humidity_plot.axhline(y=self.hum_high, color=GRAPH_HIGH_THR_COLOR,
                                                              linestyle='--')
        if self.hum_low.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            self.humidity_plot.fill_between(self.recordings.timestamp, self.recordings.humidity, self.hum_low,
                                            where=self.recordings.humidity <= __tl,
                                            interpolate=True, color=GRAPH_LOW_THR_COLOR, label='Low alert')
            self.hum_thr_lo_line = self.humidity_plot.axhline(y=self.hum_low, color=GRAPH_LOW_THR_COLOR,
                                                              linestyle='--')
        # Adding 'tampered' and 'bookmark' marks
        self.hum_book_lines = self.humidity_plot.plot_date(self.recordings.timestamp, self.recordings.humidity,
                                                           xdate=True, marker='o', markerfacecolor='g', fmt='',
                                                           markevery=list(map(bool, self.recordings.is_bookmark)),
                                                           label='Bookmark', color='black', alpha=0.7)
        self.hum_tamp_lines = self.humidity_plot.plot_date(self.recordings.timestamp, self.recordings.humidity,
                                                           xdate=True, marker='o', markerfacecolor='r', fmt='',
                                                           markevery=list(map(bool, self.recordings.is_tampered)),
                                                           label='Tampered', color='black', alpha=0.7)
        # Adding legend and axis labels
        self.humidity_plot.legend(loc=1)
        self.humidity_plot.set_xlabel('Date & Time', fontsize=9)
        self.humidity_plot.set_ylabel('Humidity, %', fontsize=9)
        # Adding grid if required
        if self.grid_state is True:
            self.humidity_plot.xaxis.grid(True, which='major')
            self.humidity_plot.yaxis.grid(True, which='major')
        # Clear memory
        del __th, __tl
        del datetime_format, date_format_mask, time_format_mask
        gc.collect(1)

    def __ui_start(self):
        self.united_canvas = FigureCanvasTkAgg(self.united_figure, master=self)
        self.notebook.add(self.united_canvas.get_tk_widget(), text='Graphs')
        self.__ui_create_control_panel()
        self.notebook.pack(expand=1, fill='both')
        # Adding zoom and pan feature
        self.zp = ZoomPan(self.temperature_plot, self.humidity_plot)
        self.zp.start_pan_factory()
        self.zp.start_zoom_factory(base_scale=1.2)

    def __ui_create_control_panel(self):
        control_panel = Canvas(self, height=GRAPH_CONTROL_HEIGHT, bg=GUI_BG_COLOR, cursor='arrow')
        self.image_button_export_png = CustomImageButton(control_panel, width=50, height=50, bgcolor=GUI_BG_COLOR,
                                                         image_active=ICON_EXPORT_PNG,
                                                         image_inactive=ICON_EXPORT_PNG,
                                                         tip='Save as PNG',
                                                         command=self.__save_graph)
        control_panel.create_window(10, 5, window=self.image_button_export_png, anchor=NW)
        self.image_button_grid = CustomImageButton(control_panel, width=50, height=50, bgcolor=GUI_BG_COLOR,
                                                   image_active=ICON_GRID_ACTIVE,
                                                   image_inactive=ICON_GRID_INACTIVE,
                                                   tip='Enable grid',
                                                   command=self.__change_grid_state)
        control_panel.create_window(70, 5, window=self.image_button_grid, anchor=NW)
        self.image_button_legend = CustomImageButton(control_panel, width=50, height=50, bgcolor=GUI_BG_COLOR,
                                                     image_active=ICON_LEGEND,
                                                     image_inactive=ICON_LEGEND_INACTIVE,
                                                     tip='Enable legend',
                                                     command=self.__change_legend_state)
        control_panel.create_window(130, 5, window=self.image_button_legend, anchor=NW)
        self.image_button_reset_graph = CustomImageButton(control_panel, width=50, height=50, bgcolor=GUI_BG_COLOR,
                                                          image_active=ICON_RESET_GRAPH,
                                                          image_inactive=ICON_RESET_GRAPH,
                                                          tip='Autoscale the graphs',
                                                          command=self.__reset_graph_limits)
        control_panel.create_window(190, 5, window=self.image_button_reset_graph, anchor=NW)
        control_panel.pack(fill='both', side=TOP)

    def __ui_stop(self):
        self.notebook.pack_forget()

    def __change_legend_state(self):
        self.legend_state = False if self.legend_state is True else True
        # Activate\deactivate icon of legend button
        self.image_button_legend.swap_icons()
        # Rebuild plots to apply changes
        try:
            self.temperature_plot.get_legend().set_visible(self.legend_state)
            self.humidity_plot.get_legend().set_visible(self.legend_state)
        except AttributeError:
            pass
        self.united_figure.canvas.draw()

    def __change_grid_state(self):
        self.grid_state = False if self.grid_state is True else True
        # Activate\deactivate icon of grid button
        self.image_button_grid.swap_icons()
        # Rebuild plots to apply changes
        self.temperature_plot.grid(self.grid_state)
        self.humidity_plot.grid(self.grid_state)
        self.united_figure.canvas.draw()

    def __save_graph(self):
        file_png = asksaveasfile(initialfile='graph.png', defaultextension='.png',
                                 filetypes=[('PNG', '*.png'), ],
                                 mode='w')
        if file_png is not None:
            self.united_figure.savefig(file_png.name)
            file_png.close()
            del file_png
            gc.collect(1)

    def __reset_graph_limits(self):
        self.temperature_plot.autoscale()
        self.humidity_plot.autoscale()
        self.united_figure.canvas.draw()

    def __touch_graph(self):
        if self.is_update_enabled:
            self.united_figure.canvas.draw()
            self.is_update_enabled = False
        self.after(100, self.__touch_graph)

    def __plot_graphs(self):
        self.__ui_create_temperature_graph()
        self.__ui_create_humidity_graph()
        self.is_update_enabled = True
        gc.collect()

    def set_recordings(self, recordings: Container_Recordings):
        self.recordings = recordings
        if len(recordings.timestamp) != 0:
            self.__plot_graphs()

    def set_configuration(self, configuration):
        thr_dis_val = Structure_Configuration.THR_DISABLED_VALUE
        self.configuration = configuration
        self.temp_high = configuration.hi_temp_thr if configuration.hi_temp_thr.__eq__(thr_dis_val) \
            else DataEnums.convert_celsius_to_required(configuration.hi_temp_thr / 10, self.configuration.temp_unit)
        self.temp_low = configuration.lo_temp_thr if configuration.lo_temp_thr.__eq__(thr_dis_val) \
            else DataEnums.convert_celsius_to_required(configuration.lo_temp_thr / 10, self.configuration.temp_unit)
        self.hum_high = configuration.hi_hum_thr if configuration.hi_hum_thr.__eq__(thr_dis_val) \
            else configuration.hi_hum_thr / 10
        self.hum_low = configuration.lo_hum_thr if configuration.lo_hum_thr.__eq__(thr_dis_val) \
            else configuration.lo_hum_thr / 10

    def ui_delete(self):
        # Freeing figure
        self.united_figure.canvas.close_event()
        self.united_figure.clear()
        del self.united_figure
        # Freeing plots
        self.temperature_plot.clear()
        self.humidity_plot.clear()
        del self.temperature_plot
        del self.humidity_plot
        # Freeing lines
        self.temp_lines.pop(0).remove() if self.temp_lines else None
        self.temp_book_lines.pop(0).remove() if self.temp_book_lines else None
        self.temp_tamp_lines.pop(0).remove() if self.temp_tamp_lines else None
        self.hum_lines.pop(0).remove() if self.hum_lines else None
        self.hum_book_lines.pop(0).remove() if self.hum_book_lines else None
        self.hum_tamp_lines.pop(0).remove() if self.hum_tamp_lines else None
        self.temp_thr_hi_line.remove() if self.temp_thr_hi_line else None
        self.temp_thr_lo_line.remove() if self.temp_thr_lo_line else None
        self.hum_thr_hi_line.remove() if self.hum_thr_hi_line else None
        self.hum_thr_lo_line.remove() if self.hum_thr_lo_line else None
        # Freeing zoom-pan factory
        self.zp.destroy()
        del self.zp
        # Freeing backend
        for item in self.united_canvas.get_tk_widget().find_all():
            self.united_canvas.get_tk_widget().delete(item)
        self.united_canvas.get_tk_widget().destroy()
        self.united_canvas.figure.clear()
        plt.close(self.united_canvas.figure)
        del self.united_canvas._tkphoto
        del self.united_canvas.renderer._renderer
        del self.united_canvas.renderer.bbox
        del self.united_canvas.renderer._filter_renderers
        del self.united_canvas.renderer.mathtext_parser
        del self.united_canvas.toolbar
        del self.united_canvas
        # Freeing images
        self.image_button_grid.destroy()
        self.image_button_export_png.destroy()
        del self.image_button_grid
        del self.image_button_export_png
        # Freeing parameters
        del self.recordings
        del self.configuration
        gc.collect(1)
