from tkinter import *
import tkinter.ttk as ttk
from ui.constants import *
from widgets.custom_checkbox import CustomCheckboxBool
from communication.timezones import Timezones
from communication.data_structure import DataEnums
from datetime import datetime, timedelta
from settings import Settings
import time

PADY = 5


class UI_OptionsWindow(Toplevel):

    def __init__(self, root, ext_submit_handler, **kw):
        super().__init__(root, background=GUI_BG_COLOR, **kw)
        # Widgets
        self.root = root
        self.withdraw()
        self.combobox_timezone = None
        self.checkbox_dst = None
        self.combobox_units = None
        # Parameters
        self.temperature_unit: int = 0
        self.current_time = StringVar()
        self.timezone_str = StringVar()
        self.timezone: int = 0
        self.date_format: int = 0
        self.time_format: int = 0
        self.is_dst_enabled: bool = False
        self.auto_download: bool = True
        self.is_submitted: bool = False
        self.time_standard: int = 0
        self.external_submit_handler = ext_submit_handler
        # Read settings
        self.__read_settings()
        # Create UI
        self.__ui_create()
        # Apply the read settings to UI
        self.__set_settings()
        # Start clocks
        self.__update_timezone()
        self.__update_current_time()
        self.deiconify()

    def __ui_create(self):
        self.resizable(False, False)
        self.title('Options')
        self.iconbitmap(ICON_APP)
        self.protocol("WM_DELETE_WINDOW", self.__ui_quit)
        # Create notebook
        self.notebook = ttk.Notebook(self, height=550)
        general_tab = self.__ui_create_general_tab()
        self.notebook.add(general_tab, text='General')
        self.notebook.pack(expand=True, fill='both')
        # Positioning toplevel
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.update_idletasks()
        x_offset = (GUI_TOTAL_WIDTH - self.winfo_width()) // 2
        y_offset = (GUI_HEIGHT - self.winfo_height()) // 2
        self.geometry('+%d+%d' % (x + x_offset, y + y_offset))
        # Create buttons
        ttk.Button(self, text='OK', command=self.__button_submit_callback) \
            .pack(side=LEFT, anchor=W, pady=5, padx=5)
        ttk.Button(self, text='Cancel', command=self.__button_cancel_callback) \
            .pack(side=RIGHT, anchor=SE, pady=5, padx=5)

    def __ui_create_general_tab(self):
        frame_general = ttk.Frame(self.notebook, height=600)
        style = ttk.Style()
        style.configure('TCheckbutton', background=GUI_BG_COLOR, font=GUI_FONT_CONTENT)
        # Create checkboxes
        self.checkbox_autoread = CustomCheckboxBool(frame_general,
                                                    tip='Download data from device automatically on connect',
                                                    text='Automatically download data')
        self.checkbox_autoread.set(True)
        self.checkbox_autoread.configure(state='disabled')
        self.checkbox_dst = CustomCheckboxBool(frame_general, tip='Advance data by 1 hour',
                                               text='Use daylight saving time', state='disabled',
                                               command=self.__update_dst_usage)
        self.checkbox_autoread.grid(row=0, column=0, columnspan=2, sticky=W, pady=PADY)
        self.checkbox_dst.grid(row=5, column=0, columnspan=2, sticky=W, pady=PADY)
        # Create labels
        ttk.Label(frame_general, text='Temp. units:', font=GUI_FONT_CONTENT, background=GUI_BG_COLOR) \
            .grid(row=1, column=0, sticky=W, pady=PADY)
        ttk.Label(frame_general, text='Date format:', font=GUI_FONT_CONTENT, background=GUI_BG_COLOR) \
            .grid(row=2, column=0, sticky=W, pady=PADY)
        ttk.Label(frame_general, text='Time format:', font=GUI_FONT_CONTENT, background=GUI_BG_COLOR) \
            .grid(row=3, column=0, sticky=W, pady=PADY)
        ttk.Label(frame_general, text='Time standard:', font=GUI_FONT_CONTENT, background=GUI_BG_COLOR) \
            .grid(row=4, column=0, sticky=W, pady=PADY)
        ttk.Label(frame_general, text='Timezone:', font=GUI_FONT_CONTENT, background=GUI_BG_COLOR) \
            .grid(row=6, column=0, sticky=W, pady=PADY)
        ttk.Label(frame_general, text='Current time at\nselected zone:', font=GUI_FONT_CONTENT, background=GUI_BG_COLOR) \
            .grid(row=7, column=0, sticky=W, pady=PADY)
        # Set font for dropdown list
        self.root.option_add('*TCombobox*Listbox.font', GUI_FONT_CONTENT)
        # Creating comboboxes
        self.combobox_units = ttk.Combobox(frame_general, values=list(DataEnums.temperature_unit_t.values()),
                                           font=GUI_FONT_CONTENT,
                                           width=20, style='W.TCombobox', takefocus=False)
        self.combobox_date_format = ttk.Combobox(frame_general, values=list(DataEnums.date_format_t.values()),
                                                 font=GUI_FONT_CONTENT,
                                                 width=20, style='W.TCombobox', takefocus=False)
        self.combobox_time_format = ttk.Combobox(frame_general, values=list(DataEnums.time_format_t.values()),
                                                 font=GUI_FONT_CONTENT,
                                                 width=20, style='W.TCombobox', takefocus=False)
        self.combobox_time_standard = ttk.Combobox(frame_general, values=Timezones.timezone_codes, font=GUI_FONT_CONTENT,
                                                   width=20, style='W.TCombobox', takefocus=False)
        self.combobox_timezone = ttk.Combobox(frame_general, values=Timezones.timezones_GMT, font=GUI_FONT_CONTENT,
                                              width=20, style='W.TCombobox', takefocus=False,
                                              textvariable=self.timezone_str)
        # Configuring initial values for comboboxes
        # self.combobox_units.current(0)
        # self.combobox_date_format.current(0)
        # self.combobox_time_format.current(0)
        self.combobox_time_standard.current(0)
        # self.combobox_timezone.current(0)
        # Packing comboboxes into grid
        self.combobox_units.grid(row=1, column=1, pady=PADY, padx=10, sticky=W + E)
        self.combobox_date_format.grid(row=2, column=1, pady=PADY, padx=10, sticky=W + E)
        self.combobox_time_format.grid(row=3, column=1, pady=PADY, padx=10, sticky=W + E)
        self.combobox_time_standard.grid(row=4, column=1, pady=PADY, padx=10, sticky=W + E)
        self.combobox_timezone.grid(row=6, column=1, pady=PADY, padx=10, sticky=W + E)
        # Binding event handlers to comboboxes
        self.combobox_units.bind('<<ComboboxSelected>>', lambda e: [frame_general.focus(),
                                                                    self.__update_temperature_unit()], '+')
        self.combobox_date_format.bind('<<ComboboxSelected>>', lambda e: [frame_general.focus(),
                                                                          self.__update_date_format()], '+')
        self.combobox_time_format.bind('<<ComboboxSelected>>', lambda e: [frame_general.focus(),
                                                                          self.__update_time_format()], '+')
        self.combobox_time_standard.bind('<<ComboboxSelected>>', lambda e: [frame_general.focus(),
                                                                            self.__update_time_standard()], '+')
        self.combobox_timezone.bind('<<ComboboxSelected>>', lambda e: [frame_general.focus(),
                                                                       self.__update_timezone()], '+')
        # Create current time read-only entry
        entry_current_time = ttk.Entry(frame_general, state='disabled', textvariable=self.current_time,
                                       width=20, font=GUI_FONT_CONTENT, justify=RIGHT)
        entry_current_time.grid(row=7, column=1, pady=PADY, padx=10, sticky=W + E)
        return frame_general

    def __update_temperature_unit(self):
        self.temperature_unit = self.combobox_units.current()

    def __update_dst_usage(self):
        self.is_dst_enabled = self.checkbox_dst.get()
        self.__update_timezone()

    def __update_time_standard(self):
        old_idx = self.combobox_timezone.current()
        self.time_standard = self.combobox_time_standard.current()
        if self.time_standard.__eq__(0):
            self.combobox_timezone.configure(values=Timezones.timezones_GMT)
        else:
            self.combobox_timezone.configure(values=Timezones.timezones_UTC)
        self.combobox_timezone.current(old_idx)

    def __update_timezone(self):
        tz_str = self.timezone_str.get()
        if tz_str.__eq__(Timezones.timezones_UTC[0]):
            self.timezone = -time.timezone
        else:
            hour_offset = int(tz_str[3:6])
            mins_offset = int(tz_str[7:9])
            self.timezone = hour_offset * 3600 + mins_offset * 60

    def __update_current_time(self):
        offset = 3600 if self.is_dst_enabled else 0
        self.current_time.set(
            (datetime.utcnow() + timedelta(seconds=(self.timezone + offset)))
                .strftime(f'{DataEnums.date_format_mask.get(self.date_format)} '
                          f'{DataEnums.time_format_mask.get(self.time_format)}'))
        self.after(1000, self.__update_current_time)

    def __update_date_format(self):
        self.date_format = self.combobox_date_format.current()

    def __update_time_format(self):
        self.time_format = self.combobox_time_format.current()

    def __set_submission(self, is_submitted):
        self.is_submitted = is_submitted

    def __read_settings(self):
        settings = Settings()
        self.temperature_unit = settings.temperature_unit
        self.date_format = settings.date_format
        self.time_format = settings.time_format
        self.timezone = settings.timezone
        # self.is_dst_enabled = settings.dst
        # self.autoread = settings.auto_download
        self.is_dst_enabled = False
        self.autoread = True
        self.time_standard = settings.time_standard

    def __set_settings(self):
        self.combobox_units.current(self.temperature_unit)
        self.combobox_date_format.current(self.date_format)
        self.combobox_time_format.current(self.time_format)
        self.combobox_timezone.current(Timezones.get_zone_idx_by_offset(self.timezone))
        self.checkbox_dst.set(self.is_dst_enabled)
        self.checkbox_autoread.set(self.autoread)
        self.combobox_time_standard.current(self.time_standard)
        self.__update_time_standard()

    def __button_submit_callback(self):
        settings = Settings()
        settings.temperature_unit = self.temperature_unit
        settings.date_format = self.date_format
        settings.time_format = self.time_format
        settings.timezone = self.timezone
        settings.dst = self.is_dst_enabled
        settings.auto_download = self.checkbox_autoread.get()
        settings.time_standard = self.time_standard
        settings.save()
        self.external_submit_handler()
        self.__ui_quit()

    def __button_cancel_callback(self):
        self.__ui_quit()

    def __ui_quit(self):
        self.destroy()
