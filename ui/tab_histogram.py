from tkinter import *
from tkinter import ttk
from tkinter.filedialog import asksaveasfile
from ui.constants import *
from ui.zoom_pan import ZoomPan
from widgets.custom_imagebutton import CustomImageButton
from communication.data_structure import Structure_Configuration, Container_Recordings, DataEnums
import matplotlib
import gc

matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.container import BarContainer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BINS_NUMBER = 10
BINS_WIDTH = 0.8


class UI_TabHistogram(ttk.Frame):

    def __init__(self, main_window, **kw):
        super().__init__(main_window, **kw)
        # Widgets
        self.main_window = main_window
        self.united_canvas = None
        self.united_figure = None
        self.temperature_hist = None
        self.humidity_hist = None
        self.notebook = None
        self.image_button_grid = None
        self.temp_thr_lo_line = None
        self.temp_thr_hi_line = None
        self.hum_thr_lo_line = None
        self.hum_thr_hi_line = None
        self.temp_patches = None
        self.hum_patches = None
        # Parameters
        self.recordings = None
        self.configuration = None
        self.temp_high: float = 0.0
        self.temp_low: float = 0.0
        self.hum_high: float = 0.0
        self.hum_low: float = 0.0
        # Settings
        self.grid_state: bool = True
        self.is_update_enabled: bool = True
        self.zp = None
        # Rendering UI
        self.__ui_create()
        self.__ui_start()
        self.__touch_hist()

    def __ui_create(self):
        self.notebook = ttk.Notebook(self, height=GRAPH_TAB_HEIGHT)
        self.united_figure = Figure()
        self.united_figure.patch.set_facecolor(GUI_BG_COLOR)
        # Creating temperature hist
        if self.temperature_hist is None:
            self.temperature_hist = self.united_figure.add_subplot(211)
        # Creating humidity hist
        if self.humidity_hist is None:
            self.humidity_hist = self.united_figure.add_subplot(212)
        # Adding grid if required
        if self.grid_state is True:
            self.temperature_hist.xaxis.grid(True, which='major')
            self.temperature_hist.yaxis.grid(True, which='major')
            self.humidity_hist.xaxis.grid(True, which='major')
            self.humidity_hist.yaxis.grid(True, which='major')

    def __ui_create_temperature_hist(self):
        self.temperature_hist.clear()
        self.temperature_hist.tick_params(axis='both', labelsize=9)
        # Calculating max and min thresholds for histogram coloring
        temp_high = max(self.recordings.temperature)
        temp_low = min(self.recordings.temperature)
        if self.temp_high.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            temp_high = self.temp_high
        if self.temp_low.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            temp_low = self.temp_low
        # Draw histogram
        N, bins, self.temp_patches = self.temperature_hist.hist(self.recordings.temperature,
                                                                bins=BINS_NUMBER,
                                                                histtype='bar', rwidth=BINS_WIDTH, color='black',
                                                                orientation='horizontal')
        # Color the patches accordingly to thresholds
        for i, patch in enumerate(self.temp_patches):
            if bins[i] <= temp_low and self.temp_low.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
                patch.set_facecolor(GRAPH_LOW_THR_COLOR)
            elif bins[i + 1] >= temp_high and self.temp_high.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
                patch.set_facecolor(GRAPH_HIGH_THR_COLOR)

        # Draw histogram that lies to the left from low threshold
        if self.temp_low.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            self.temp_thr_lo_line = self.temperature_hist.axhline(y=self.temp_low, color=GRAPH_LOW_THR_COLOR,
                                                                  linestyle='--')
        # Draw histogram that lies to the right from high threshold
        if self.temp_high.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            self.temp_thr_hi_line = self.temperature_hist.axhline(y=self.temp_high, color=GRAPH_HIGH_THR_COLOR,
                                                                  linestyle='--')
        # Adding axis labels
        self.temperature_hist.set_ylabel(f'Temperature, '
                                         f'\u00b0{DataEnums.temperature_unit_t[self.configuration.temp_unit][:1]}',
                                         fontsize=9)
        # Adding grid if required
        if self.grid_state is True:
            self.temperature_hist.xaxis.grid(True, which='major')
            self.temperature_hist.yaxis.grid(True, which='major')
        # Clear memory
        del temp_high, temp_low
        del N, bins
        gc.collect(1)

    def __ui_create_humidity_hist(self):
        self.humidity_hist.clear()
        self.humidity_hist.tick_params(axis='both', labelsize=9)
        # Calculating max and min thresholds for histogram coloring
        hum_high = max(self.recordings.humidity)
        hum_low = min(self.recordings.humidity)
        if self.hum_high.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            hum_high = self.hum_high
        if self.hum_low.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            hum_low = self.hum_low
        # Draw histogram
        N, bins, self.hum_patches = self.humidity_hist.hist(self.recordings.humidity,
                                                            bins=BINS_NUMBER,
                                                            histtype='bar', rwidth=BINS_WIDTH, color='black',
                                                            orientation='horizontal')
        # Color the patches accordingly to thresholds
        for i, patch in enumerate(self.hum_patches):
            if bins[i] <= hum_low and self.hum_low.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
                patch.set_facecolor(GRAPH_LOW_THR_COLOR)
            elif bins[i + 1] >= hum_high and self.hum_high.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
                patch.set_facecolor(GRAPH_HIGH_THR_COLOR)
        # Draw thresholds
        if self.hum_low.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            self.hum_thr_lo_line = self.humidity_hist.axhline(y=self.hum_low, color=GRAPH_LOW_THR_COLOR,
                                                              linestyle='--')
        # Draw histogram that lies to the right from high threshold
        if self.hum_high.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
            self.hum_thr_hi_line = self.humidity_hist.axhline(y=self.hum_high, color=GRAPH_HIGH_THR_COLOR,
                                                              linestyle='--')
        # Adding axis labels
        self.humidity_hist.set_xlabel('Number of records', fontsize=9)
        self.humidity_hist.set_ylabel('Humidity, %', fontsize=9)
        # Adding grid if required
        if self.grid_state is True:
            self.humidity_hist.xaxis.grid(True, which='major')
            self.humidity_hist.yaxis.grid(True, which='major')
        # Clear memory
        del hum_high, hum_low
        del N, bins
        gc.collect(1)

    def __ui_start(self):
        self.united_canvas = FigureCanvasTkAgg(self.united_figure, master=self)
        self.notebook.add(self.united_canvas.get_tk_widget(), text='Histograms')
        self.__ui_create_control_panel()
        self.notebook.pack(expand=True, fill='both')
        # Adding zoom and pan feature
        self.zp = ZoomPan(self.temperature_hist, self.humidity_hist)
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
        self.image_button_reset_graph = CustomImageButton(control_panel, width=50, height=50, bgcolor=GUI_BG_COLOR,
                                                          image_active=ICON_RESET_GRAPH,
                                                          image_inactive=ICON_RESET_GRAPH,
                                                          tip='Autoscale the histograms',
                                                          command=self.__reset_graph_limits)
        control_panel.create_window(130, 5, window=self.image_button_reset_graph, anchor=NW)
        control_panel.pack(fill='both', side=TOP)

    def __ui_stop(self):
        self.notebook.pack_forget()

    def __change_grid_state(self):
        self.grid_state = False if self.grid_state is True else True
        # Activate\deactivate icon of grid button
        self.image_button_grid.swap_icons()
        # Rebuild histograms to apply changes
        self.temperature_hist.grid(self.grid_state)
        self.humidity_hist.grid(self.grid_state)
        self.united_figure.canvas.draw()

    def __save_graph(self):
        file_png = asksaveasfile(initialfile='histogram.png', defaultextension='.png',
                                 filetypes=[('PNG', '*.png'), ],
                                 mode='w')
        if file_png is not None:
            self.united_figure.savefig(file_png.name)
            file_png.close()
            del file_png
            gc.collect(1)

    def __reset_graph_limits(self):
        self.temperature_hist.autoscale()
        self.humidity_hist.autoscale()
        self.united_figure.canvas.draw()

    def __touch_hist(self):
        if self.is_update_enabled:
            self.united_figure.canvas.draw()
            self.is_update_enabled = False
        self.after(100, self.__touch_hist)

    def __plot_histograms(self):
        self.__ui_create_temperature_hist()
        self.__ui_create_humidity_hist()
        self.is_update_enabled = True
        gc.collect()

    def set_recordings(self, recordings: Container_Recordings):
        self.recordings = recordings
        if len(recordings.timestamp) != 0:
            self.__plot_histograms()

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
        self.temperature_hist.clear()
        self.humidity_hist.clear()
        del self.temperature_hist
        del self.humidity_hist
        # Freeing lines
        for _ in range(BINS_NUMBER):
            if isinstance(self.temp_patches, BarContainer):
                try:
                    self.temp_patches.remove()
                except:
                    pass
            elif isinstance(self.temp_patches, list):
                self.temp_patches.pop(0).remove()
        del self.temp_patches
        for _ in range(BINS_NUMBER):
            if isinstance(self.hum_patches, BarContainer):
                try:
                    self.hum_patches.remove()
                except:
                    pass
            elif isinstance(self.hum_patches, list):
                self.hum_patches.pop(0).remove()
        del self.hum_patches
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
