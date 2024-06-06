from tkinter import *
from tkinter import ttk
from ui.constants import *
from widgets.custom_input import CustomInput
from widgets.custom_checkbox import CustomCheckboxBool
from widgets.custom_dateentry import CustomCalendar
from widgets.custom_timeentry import CustomTimeEntry
from communication.data_structure import Timestamp2020, Structure_Configuration, DataEnums
from communication.timezones import Timezones
from settings import Settings
from datetime import datetime
import ctypes
import math
import os
import gc

UI_Y_OFFSET = 20
UI_CHECKBOX_OFFSET = 220
UI_INPUT_OFFSET = 140
BUTTON_MAX_OFFSET = 152 if 'nt'.__eq__(os.name) else 115


class UI_TabProgram(ttk.Frame):

    def __init__(self, main_window, **kw):
        super().__init__(**kw)
        self.main_window = main_window
        self.start_mode = StringVar()
        self.stop_mode = StringVar()
        self.system_type = 0
        self.firmware_version = {"MAJOR": 0, "MINOR": 0, "FIX": 0}
        self.is_programming_blocked = False
        # Widgets
        self.canvas = None
        self.input_temp_high = None
        self.input_temp_low = None
        self.input_hum_high = None
        self.input_hum_low = None
        self.checkbox_enable_temp_high = None
        self.checkbox_enable_temp_low = None
        self.checkbox_enable_hum_high = None
        self.checkbox_enable_hum_low = None
        self.checkbox_enable_humidity_sensor = None
        self.checkbox_enable_stop_button = None
        self.checkbox_enable_restart = None
        self.input_consecutive_delay = None
        self.input_total_delay = None
        self.date_entry_start_auto = None
        self.input_start_after = None
        self.input_stop_when = None
        self.button_maximum_points = None
        self.button_program = None
        self.button_program_callback = lambda: print('Program device')
        self.progressbar = None
        # Render
        self.__ui_create()
        self.__ui_start()
        self.update_datetime_format()

    def set_system_data(self, system_data):
        # Save firmware version
        self.firmware_version["MAJOR"] = system_data.fw_version[0]
        self.firmware_version["MINOR"] = system_data.fw_version[1]
        self.firmware_version["FIX"] = system_data.fw_version[2]
        # Set max value for max recordings number
        self.input_max_records.set_max(system_data.memory_size)
        # Set min & max values for temperature thresholds
        temp_range = DataEnums.temperature_range_t.get(system_data.temp_range, DataEnums.temperature_range_t.get(1))
        temp_min, temp_max = temp_range.split('..')
        self.input_temp_low.set_min(int(temp_min))
        self.input_temp_low.set_max(int(temp_max))
        self.input_temp_high.set_max(int(temp_min))
        self.input_temp_high.set_max(int(temp_max))
        self.system_type = system_data.system_type
        if self.system_type == 1:
            # If device type is V1 then it doesnt support humidity and light sensor
            self.checkbox_enable_humidity_sensor.set(False)
            self.checkbox_enable_humidity_sensor.configure(state='disabled')
            self.checkbox_enable_light_sensor.set(False)
            self.checkbox_enable_light_sensor.configure(state='disabled')
        elif self.system_type == 3:
            # If device type is V3 then it supports restart
            self.checkbox_enable_restart.configure(state='normal')
            self.checkbox_enable_restart.set(True)

    def set_metadata(self, metadata):
        if self.system_type != 3 and metadata.records_count != 0:
            self.button_program.configure(state='disabled')
            self.is_programming_blocked = True
        else:
            self.button_program.configure(state='normal')

    def set_configuration(self, config):
        thr_dis_val = Structure_Configuration.THR_DISABLED_VALUE
        # Filling alarm thresholds submenu
        self.checkbox_enable_temp_high.set(config.hi_temp_thr != thr_dis_val)
        self.checkbox_enable_temp_low.set(config.lo_temp_thr != thr_dis_val)
        self.checkbox_enable_hum_high.set(config.hi_hum_thr != thr_dis_val)
        self.checkbox_enable_hum_low.set(config.lo_hum_thr != thr_dis_val)
        self.__enable_temp_hi_threshold()
        self.__enable_temp_lo_threshold()
        self.__enable_hum_hi_threshold()
        self.__enable_hum_lo_threshold()
        self.input_temp_high.set('0.0' if config.hi_temp_thr.__eq__(thr_dis_val)
                                 else DataEnums.convert_celsius_to_required(config.hi_temp_thr / 10, config.temp_unit))
        self.input_temp_low.set('0.0' if config.lo_temp_thr.__eq__(thr_dis_val)
                                else DataEnums.convert_celsius_to_required(config.lo_temp_thr / 10, config.temp_unit))
        self.input_hum_high.set('0.0' if config.hi_hum_thr.__eq__(thr_dis_val) else config.hi_hum_thr / 10)
        self.input_hum_low.set('0.0' if config.lo_hum_thr.__eq__(thr_dis_val) else config.lo_hum_thr / 10)
        # Filling delays submenu
        if self.__is_config_version_1_used():
            self.input_consecutive_delay.set('1')
            self.input_total_delay.set('1')
        else:
            self.input_consecutive_delay.set(str(config.alrt_cons))
            self.input_total_delay.set(str(config.alrt_count))
            self.input_consecutive_delay.set_state(True)
            self.input_total_delay.set_state(True)
        # Filling options submenu
        self.checkbox_enable_humidity_sensor.set(config.hum_enabled)
        self.checkbox_enable_light_sensor.set(config.als_enabled)
        self.checkbox_enable_stop_button.set(config.stop_btn_enabled)
        if self.system_type == 1:
            # If device type is V1 then it doesnt support humidity and light sensor
            self.checkbox_enable_humidity_sensor.set(False)
            self.checkbox_enable_humidity_sensor.configure(state='disabled')
            self.checkbox_enable_light_sensor.set(False)
            self.checkbox_enable_light_sensor.configure(state='disabled')
        elif self.system_type == 3:
            # If device type is V3 then it supports restart
            self.checkbox_enable_restart.configure(state='normal')
            self.checkbox_enable_restart.set(True)
        self.__enable_humidity_sensor()
        # Filling logging start submenu
        settings = Settings()
        date_fmt_mask = DataEnums.date_format_mask.get(settings.date_format, DataEnums.date_format_mask.get(0))
        if config.auto_delay.__ne__(Structure_Configuration.TS_ILLEGAL_VALUE):
            auto_start_date, auto_start_time = \
                Timestamp2020.convert_to_datetime_str(config.auto_delay,
                                                      date_fmt=date_fmt_mask).split(' ')
            auto_start_hour, auto_start_min, _ = auto_start_time.split(':')
            self.date_entry_start_auto.set_date(auto_start_date)

            self.time_entry_start_auto.set_time(hours=auto_start_hour, minutes=auto_start_min)
            self.time_entry_start_man.set_time(hours=0, minutes=0)
            self.start_mode.set('auto')
        if config.manual_delay.__ne__(Structure_Configuration.TS_ILLEGAL_VALUE):
            current_time = datetime.now()
            self.date_entry_start_auto.set_date(current_time)
            self.time_entry_start_auto.set_time(hours=current_time.hour, minutes=current_time.minute)
            self.time_entry_start_man.set(config.manual_delay)
            self.start_mode.set('manual')
        # Filling logging stop submenu
        if config.duration_time.__ne__(0):
            self.stop_mode.set('duration')
        if config.max_records.__ne__(0):
            self.stop_mode.set('records')
        self.time_entry_measure_period.set(config.meas_period)
        self.time_entry_stop_duration.set(config.duration_time)
        self.input_max_records.set(config.max_records)
        self.__stop_condition_changed()
        # Filling description
        self.text_description.delete(1.0, END)
        self.text_description.insert(1.0, Structure_Configuration.arr_to_string(config.description))

    def set_initial_data(self):
        # Filling alarm thresholds submenu
        self.checkbox_enable_temp_high.set(True)
        self.checkbox_enable_temp_low.set(True)
        self.checkbox_enable_hum_high.set(True)
        self.checkbox_enable_hum_low.set(True)
        self.__enable_temp_hi_threshold()
        self.__enable_temp_lo_threshold()
        self.__enable_hum_hi_threshold()
        self.__enable_hum_lo_threshold()
        temp_low, temp_high = DataEnums.temperature_range_t.get(self.system_type, '-5.0..20.0').split('..')
        self.input_temp_high.set(temp_high)
        self.input_temp_low.set(temp_low)
        self.input_hum_high.set('100.0')
        self.input_hum_low.set('0.0')
        # Filling delays submenu
        if not self.__is_config_version_1_used():
            self.input_consecutive_delay.set_state(True)
            self.input_total_delay.set_state(True)
        self.input_consecutive_delay.set('1')
        self.input_total_delay.set('1')
        # Filling options submenu
        self.checkbox_enable_humidity_sensor.set(False)
        self.checkbox_enable_light_sensor.set(False)
        self.checkbox_enable_stop_button.set(True)
        if self.system_type == 1:
            # If device type is V1 then it doesnt support humidity and light sensor
            self.checkbox_enable_humidity_sensor.set(False)
            self.checkbox_enable_humidity_sensor.configure(state='disabled')
            self.checkbox_enable_light_sensor.set(False)
            self.checkbox_enable_light_sensor.configure(state='disabled')
        elif self.system_type == 3:
            # If device type is V3 then it supports restart
            self.checkbox_enable_restart.configure(state='normal')
            self.checkbox_enable_restart.set(True)
        self.__enable_humidity_sensor()
        # Filling logging start submenu
        settings = Settings()
        date_fmt_mask = DataEnums.date_format_mask.get(settings.date_format, DataEnums.date_format_mask.get(0))
        current_time = datetime.now()
        self.date_entry_start_auto.set_date(current_time)
        self.time_entry_start_auto.set_time(hours=current_time.hour, minutes=current_time.minute)
        self.time_entry_start_man.set(0)
        self.start_mode.set('manual')
        # Filling logging stop submenu
        self.stop_mode.set('records')
        self.time_entry_measure_period.set(10)
        self.time_entry_stop_duration.set(0)
        self.input_max_records.set('1000')
        self.__stop_condition_changed()
        # Filling description
        self.text_description.delete(1.0, END)

    def save_data_to_configuration(self, config):
        if self.is_programming_blocked:
            return
        thr_dis_val = Structure_Configuration.THR_DISABLED_VALUE
        # Preparing configuration
        config.magic = Structure_Configuration.CONFIGURATION_MAGIC
        config.size = Structure_Configuration.CONFIGURATION_SIZE
        config.version = Structure_Configuration.CONFIGURATION_VERSION if self.__is_config_version_1_used() \
            else Structure_Configuration.CONFIGURATION_VERSION_2
        config.reserved1 = 0xFFFFFFFF
        config.reserved2 = (ctypes.c_uint8 * 68)(*[0xFF] * 68)
        # Collecting data from settings file
        settings = Settings()
        config.timezone = settings.timezone
        config.timezone_code = Structure_Configuration.string_to_arr(
            Timezones.timezone_codes[settings.time_standard], 4)
        config.temp_unit = settings.temperature_unit
        config.date_fmt = settings.date_format
        config.time_fmt = settings.time_format
        # Collecting alarm thresholds data
        self.__temp_thresholds_validator(None)
        self.__hum_thresholds_validator(None)
        config.hi_temp_thr = thr_dis_val if not self.checkbox_enable_temp_high.get() else \
            int(DataEnums.convert_current_to_celsius(float(self.input_temp_high.get()), config.temp_unit) * 10)
        config.lo_temp_thr = thr_dis_val if not self.checkbox_enable_temp_low.get() else \
            int(DataEnums.convert_current_to_celsius(float(self.input_temp_low.get()), config.temp_unit) * 10)
        config.hi_hum_thr = thr_dis_val if not self.checkbox_enable_hum_high.get() else \
            int(float(self.input_hum_high.get()) * 10)
        config.lo_hum_thr = thr_dis_val if not self.checkbox_enable_hum_low.get() else \
            int(float(self.input_hum_low.get()) * 10)
        # Collecting delays data
        if self.__is_config_version_1_used():
            # In configuration version 1 (in FW <= 0.100.N) these two fields belong to reserved2 field.
            config.alrt_cons = 0xFF
            config.alrt_count = 0xFF
        else:
            config.alrt_cons = int(self.input_consecutive_delay.get())
            config.alrt_count = int(self.input_total_delay.get())
        # Collecting options data
        config.hum_enabled = int(self.checkbox_enable_humidity_sensor.get())
        config.als_enabled = int(self.checkbox_enable_light_sensor.get())
        config.stop_btn_enabled = int(self.checkbox_enable_stop_button.get())
        # Collecting logging start data
        if self.start_mode.get().__eq__('auto'):
            date_fmt_mask = DataEnums.date_format_mask.get(config.date_fmt, DataEnums.date_format_mask.get(0))
            timestamp_auto = Timestamp2020.convert_to_timestamp(self.date_entry_start_auto.get(),
                                                                date_fmt=date_fmt_mask) + \
                             self.time_entry_start_auto.get() - config.timezone
            # FIXME
            #  If user chooses date earlier than 2020.01.01 00:00 UTC then timestamp value
            #  becomes negative. Variable config.delay_auto is unsigned, so in this cases
            #  timestamp is set to 0 to prevent unsigned overflow.
            timestamp_auto = 0 if timestamp_auto.__lt__(0) else timestamp_auto
            timestamp_manual = Structure_Configuration.TS_ILLEGAL_VALUE
        else:
            timestamp_auto = Structure_Configuration.TS_ILLEGAL_VALUE
            timestamp_manual = self.time_entry_start_man.get()
        config.auto_delay = timestamp_auto
        config.manual_delay = timestamp_manual
        # FIXME
        #  Currently we do nothing with 'enable restart' checkbox.
        # Collecting logging stop data
        self.__measure_period_validator()
        config.meas_period = self.time_entry_measure_period.get()
        if self.stop_mode.get().__eq__('duration'):
            max_duration = self.time_entry_stop_duration.get()
            max_records = 0
        else:
            max_duration = 0
            max_records = int(self.input_max_records.get())
        config.duration_time = max_duration
        config.max_records = max_records
        # Collecting device description data
        config.description = Structure_Configuration.string_to_arr(self.text_description.get(1.0, END).strip('\n'), 256)

    def set_button_program_callback(self, callback):
        self.button_program_callback = callback

    def update_datetime_format(self):
        settings = Settings()
        date_fmt_msk = DataEnums.date_format_mask.get(settings.date_format, DataEnums.date_format_mask.get(0))
        self.date_entry_start_auto.set_pattern(date_fmt_msk)

    def ui_delete(self):
        self.canvas.pack_forget()
        self.destroy()
        gc.collect(1)

    def __ui_create(self):
        self.canvas = Canvas(self, width=GUI_DEVICE_SETTINGS_WIDTH,
                             bg=GUI_BG_COLOR, cursor='arrow')
        style = ttk.Style()
        style.configure('TCheckbutton', background=GUI_BG_COLOR, font=GUI_FONT_CONTENT)
        style.configure('TRadiobutton', background=GUI_BG_COLOR, font=GUI_FONT_CONTENT)
        style.configure('TButton', background=GUI_BG_COLOR, font=GUI_FONT_CONTENT)
        self.__ui_create_thresholds_submenu()
        self.__ui_create_options_submenu()
        self.__ui_create_delays_submenu()
        self.__ui_create_logging_start_submenu()
        self.__ui_create_logging_stop_submenu()
        self.__ui_create_other_submenu()

    def __ui_create_thresholds_submenu(self):
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET, anchor=W,
                                text='Alarm thresholds', font=GUI_FONT_HEADERS, justify=CENTER,
                                fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 30, anchor=W,
                                text='Temperature high:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.input_temp_high = CustomInput(self, font=GUI_FONT_CONTENT, width=7, justify=RIGHT, validator='float',
                                           max=100, min=-100)
        self.input_temp_high.bind('<FocusOut>', self.__temp_thresholds_validator, '+')
        window_input_temp_high = self.canvas.create_window(UI_INPUT_OFFSET, UI_Y_OFFSET + 30, anchor=W,
                                                           window=self.input_temp_high)
        self.checkbox_enable_temp_high = CustomCheckboxBool(self, tip='Enable temperature high threshold',
                                                            command=self.__enable_temp_hi_threshold)
        window_checkbox_enable_temp_high = self.canvas.create_window(UI_CHECKBOX_OFFSET, UI_Y_OFFSET + 31, anchor=W,
                                                                     window=self.checkbox_enable_temp_high)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 60, anchor=W,
                                text='Temperature low:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR, )
        self.input_temp_low = CustomInput(self, font=GUI_FONT_CONTENT, width=7, justify=RIGHT, validator='float',
                                          max=100, min=-100)
        self.input_temp_low.bind('<FocusOut>', self.__temp_thresholds_validator, '+')
        window_input_temp_low = self.canvas.create_window(UI_INPUT_OFFSET, UI_Y_OFFSET + 60, anchor=W,
                                                          window=self.input_temp_low)
        self.checkbox_enable_temp_low = CustomCheckboxBool(self, tip='Enable temperature low threshold',
                                                           command=self.__enable_temp_lo_threshold)
        window_checkbox_enable_temp_low = self.canvas.create_window(UI_CHECKBOX_OFFSET, UI_Y_OFFSET + 61, anchor=W,
                                                                    window=self.checkbox_enable_temp_low)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 90, anchor=W,
                                text='Humidity high:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.input_hum_high = CustomInput(self, font=GUI_FONT_CONTENT, width=7, justify=RIGHT, validator='float',
                                          max=100, min=0)
        self.input_hum_high.bind('<FocusOut>', self.__hum_thresholds_validator, '+')
        window_input_humidity_high = self.canvas.create_window(UI_INPUT_OFFSET, UI_Y_OFFSET + 90, anchor=W,
                                                               window=self.input_hum_high)
        self.checkbox_enable_hum_high = CustomCheckboxBool(self, tip='Enable humidity high threshold',
                                                           command=self.__enable_hum_hi_threshold)
        window_checkbox_enable_humidity_high = self.canvas.create_window(UI_CHECKBOX_OFFSET, UI_Y_OFFSET + 91, anchor=W,
                                                                         window=self.checkbox_enable_hum_high)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 120, anchor=W,
                                text='Humidity low:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.input_hum_low = CustomInput(self, font=GUI_FONT_CONTENT, width=7, justify=RIGHT, validator='float',
                                         max=100, min=0)
        self.input_hum_low.bind('<FocusOut>', self.__hum_thresholds_validator, '+')
        window_input_humidity_low = self.canvas.create_window(UI_INPUT_OFFSET, UI_Y_OFFSET + 120, anchor=W,
                                                              window=self.input_hum_low)
        self.checkbox_enable_hum_low = CustomCheckboxBool(self, tip='Enable humidity low threshold',
                                                          command=self.__enable_hum_lo_threshold)
        window_checkbox_enable_humidity_low = self.canvas.create_window(UI_CHECKBOX_OFFSET, UI_Y_OFFSET + 121, anchor=W,
                                                                        window=self.checkbox_enable_hum_low)

    def __ui_create_options_submenu(self):
        self.canvas.create_text(AXIS_X_OFFSET + 500, UI_Y_OFFSET, anchor=W,
                                text='Options', font=GUI_FONT_HEADERS, justify=CENTER,
                                fill=GUI_FONT_COLOR)
        self.checkbox_enable_humidity_sensor = CustomCheckboxBool(self, text='Enable humidity sensor',
                                                                  command=self.__enable_humidity_sensor)
        window_checkbox_enable_humidity_sensor = self.canvas.create_window(AXIS_X_OFFSET + 500, UI_Y_OFFSET + 31,
                                                                           anchor=W,
                                                                           window=self.checkbox_enable_humidity_sensor)
        self.checkbox_enable_light_sensor = CustomCheckboxBool(self, text='Enable light sensor')
        window_checkbox_enable_light_sensor = self.canvas.create_window(AXIS_X_OFFSET + 500, UI_Y_OFFSET + 61, anchor=W,
                                                                        window=self.checkbox_enable_light_sensor)
        self.checkbox_enable_stop_button = CustomCheckboxBool(self, text='Enable STOP button')
        window_checkbox_enable_stop_button = self.canvas.create_window(AXIS_X_OFFSET + 500, UI_Y_OFFSET + 91, anchor=W,
                                                                       window=self.checkbox_enable_stop_button)
        self.checkbox_enable_restart = CustomCheckboxBool(self, text='Enable restart', state='disabled')
        self.checkbox_enable_restart.set(False)
        window_checkbox_enable_restart = self.canvas.create_window(AXIS_X_OFFSET + 500, UI_Y_OFFSET + 121, anchor=W,
                                                                   window=self.checkbox_enable_restart)

    def __ui_create_delays_submenu(self):
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 150, anchor=W,
                                text='Delays before alarm', font=GUI_FONT_HEADERS, justify=CENTER,
                                fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 210, anchor=W,
                                text='Consecutive:', font=GUI_FONT_CONTENT, justify=LEFT,
                                fill=GUI_FONT_COLOR)
        self.input_consecutive_delay = CustomInput(self, font=GUI_FONT_CONTENT, width=7, justify=RIGHT,
                                                   validator='unsigned', state='disabled', min=1,
                                                   command=self.__consecutive_alerts_number_validator)
        window_input_consecutive_delay = self.canvas.create_window(UI_INPUT_OFFSET, UI_Y_OFFSET + 210, anchor=W,
                                                                   window=self.input_consecutive_delay)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 180, anchor=W,
                                text='Total:', font=GUI_FONT_CONTENT, justify=LEFT,
                                fill=GUI_FONT_COLOR)
        self.input_total_delay = CustomInput(self, font=GUI_FONT_CONTENT, width=7, justify=RIGHT,
                                             validator='unsigned', state='disabled', min=1,
                                             command=self.__total_alerts_number_validator)
        window_input_total_delay = self.canvas.create_window(UI_INPUT_OFFSET, UI_Y_OFFSET + 180, anchor=W,
                                                             window=self.input_total_delay)

    def __ui_create_logging_start_submenu(self):
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 240, anchor=W,
                                text='Logging start', font=GUI_FONT_HEADERS, justify=CENTER,
                                fill=GUI_FONT_COLOR)
        radiobox_start_auto = ttk.Radiobutton(self, text='Auto at', value='auto', variable=self.start_mode)
        window_radiobox_start_at = self.canvas.create_window(AXIS_X_OFFSET, UI_Y_OFFSET + 270, anchor=W,
                                                             window=radiobox_start_auto)
        self.date_entry_start_auto = CustomCalendar(self, font=GUI_FONT_CONTENT, width=11)
        window_date_entry_start_auto = self.canvas.create_window(AXIS_X_OFFSET + 80, UI_Y_OFFSET + 270, anchor=W,
                                                                 window=self.date_entry_start_auto)
        self.time_entry_start_auto = CustomTimeEntry(self, font=GUI_FONT_CONTENT, bgcolor=GUI_BG_COLOR)
        window_time_entry_start_auto = self.canvas.create_window(AXIS_X_OFFSET + 210, UI_Y_OFFSET + 270, anchor=W,
                                                                 window=self.time_entry_start_auto)
        radiobox_start_man = ttk.Radiobutton(self, text='Manual with delay', value='manual', variable=self.start_mode)
        window_radiobox_start_man = self.canvas.create_window(AXIS_X_OFFSET, UI_Y_OFFSET + 300, anchor=W,
                                                              window=radiobox_start_man)
        self.time_entry_start_man = CustomTimeEntry(self, font=GUI_FONT_CONTENT, hours_limit=999, bgcolor=GUI_BG_COLOR)
        window_time_entry_start_man = self.canvas.create_window(AXIS_X_OFFSET + 210, UI_Y_OFFSET + 300, anchor=W,
                                                                window=self.time_entry_start_man)

    def __ui_create_logging_stop_submenu(self):
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 330, anchor=W, text='Logging stop conditions',
                                font=GUI_FONT_HEADERS, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 360, anchor=W, text='Measure period',
                                font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.time_entry_measure_period = CustomTimeEntry(self, font=GUI_FONT_CONTENT, hours_limit=17, secs_enabled=True,
                                                         bgcolor=GUI_BG_COLOR)
        self.time_entry_measure_period.on_change(self.__measure_period_validator)
        window_time_entry_measure_period = self.canvas.create_window(AXIS_X_OFFSET + 210, UI_Y_OFFSET + 360, anchor=W,
                                                                     window=self.time_entry_measure_period)
        radiobox_stop_duration = ttk.Radiobutton(self, text='Maximum trip duration', value='duration',
                                                 variable=self.stop_mode, command=self.__stop_condition_changed)
        window_radiobox_stop_duration = self.canvas.create_window(AXIS_X_OFFSET, UI_Y_OFFSET + 390, anchor=W,
                                                                  window=radiobox_stop_duration)
        self.time_entry_stop_duration = CustomTimeEntry(self, font=GUI_FONT_CONTENT, days_enabled=True,
                                                        secs_enabled=True, bgcolor=GUI_BG_COLOR)
        self.time_entry_stop_duration.on_change(self.__stop_duration_validator)
        window_time_entry_stop_duration = self.canvas.create_window(AXIS_X_OFFSET + 210, UI_Y_OFFSET + 390, anchor=W,
                                                                    window=self.time_entry_stop_duration)
        radiobox_stop_records = ttk.Radiobutton(self, text='Maximum num. of records', value='records',
                                                variable=self.stop_mode, command=self.__stop_condition_changed)
        window_radiobox_stop_records = self.canvas.create_window(AXIS_X_OFFSET, UI_Y_OFFSET + 420, anchor=W,
                                                                 window=radiobox_stop_records)
        self.input_max_records = CustomInput(self, font=GUI_FONT_CONTENT, width=6, justify=RIGHT, validator='unsigned',
                                             min=1, max=8000, command=self.__recordings_number_validator)
        window_input_max_records = self.canvas.create_window(AXIS_X_OFFSET + 210, UI_Y_OFFSET + 420, anchor=W,
                                                             window=self.input_max_records)

    def __ui_create_other_submenu(self):
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 450, anchor=W, text='Device description',
                                font=GUI_FONT_HEADERS, justify=CENTER, fill=GUI_FONT_COLOR)
        self.text_description = Text(self, width=60, height=2, font=GUI_FONT_CONTENT, border=2)
        self.canvas.create_window(AXIS_X_OFFSET, UI_Y_OFFSET + 470, anchor=NW, window=self.text_description)
        self.button_program = ttk.Button(self, text='Program device', command=lambda: self.button_program_callback())
        self.canvas.create_window(AXIS_X_OFFSET, UI_Y_OFFSET + 520, anchor=NW, window=self.button_program)
        self.progressbar = ttk.Progressbar(self, orient=HORIZONTAL, length=110, mode='determinate')
        self.progressbar.step(1)
        self.canvas.create_window(AXIS_X_OFFSET, UI_Y_OFFSET + 550, anchor=NW, window=self.progressbar)

    def __enable_temp_hi_threshold(self):
        self.input_temp_high.set_state(self.checkbox_enable_temp_high.get())

    def __enable_temp_lo_threshold(self):
        self.input_temp_low.set_state(self.checkbox_enable_temp_low.get())

    def __enable_hum_hi_threshold(self):
        self.input_hum_high.set_state(self.checkbox_enable_hum_high.get())

    def __enable_hum_lo_threshold(self):
        self.input_hum_low.set_state(self.checkbox_enable_hum_low.get())

    def __enable_humidity_sensor(self):
        if self.checkbox_enable_humidity_sensor.get():
            self.checkbox_enable_hum_high.set(True)
            self.checkbox_enable_hum_low.set(True)
            self.checkbox_enable_hum_high.config(state=ACTIVE)
            self.checkbox_enable_hum_low.config(state=ACTIVE)
        else:
            self.checkbox_enable_hum_high.set(False)
            self.checkbox_enable_hum_low.set(False)
            self.checkbox_enable_hum_high.config(state=DISABLED)
            self.checkbox_enable_hum_low.config(state=DISABLED)
        self.__enable_hum_hi_threshold()
        self.__enable_hum_lo_threshold()

    def __ui_start(self):
        self.canvas.pack(expand=1, fill='both')

    def __is_config_version_1_used(self) -> bool:
        return True if self.firmware_version["MAJOR"].__eq__(0) \
                       and self.firmware_version["MINOR"].__le__(100) else False

    def __consecutive_alerts_number_validator(self):
        try:
            # Consecutive alerts number may never be greater than total alerts number
            if int(self.input_consecutive_delay.get()) > int(self.input_total_delay.get()):
                self.input_consecutive_delay.set(self.input_total_delay.get())
        except ValueError:
            # This exception may occur if user selects the whole content of CustomInput and replaces/deletes it.
            # That leads to the situation, when '' is passed as an argument, that is incorrect. Just ignore that.
            pass

    def __total_alerts_number_validator(self):
        try:
            # Total alerts number may never be less than consecutive alerts number and greater than total
            # recordings number
            if int(self.input_total_delay.get()) < int(self.input_consecutive_delay.get()):
                self.input_consecutive_delay.set(self.input_total_delay.get())
            if int(self.input_total_delay.get()) > int(self.input_max_records.get()):
                self.input_total_delay.set(self.input_max_records.get())
        except ValueError:
            # This exception may occur if user selects the whole content of CustomInput and replaces/deletes it.
            # That leads to the situation, when '' is passed as an argument, that is incorrect. Just ignore that.
            pass

    def __temp_thresholds_validator(self, event):
        if self.checkbox_enable_temp_low.get() and self.checkbox_enable_temp_high.get():
            if float(self.input_temp_low.get()) > float(self.input_temp_high.get()):
                temporary = self.input_temp_low.get()
                self.input_temp_low.set(self.input_temp_high.get())
                self.input_temp_high.set(temporary)

    def __hum_thresholds_validator(self, event):
        if self.checkbox_enable_hum_low.get() and self.checkbox_enable_hum_high.get():
            if float(self.input_hum_low.get()) > float(self.input_hum_high.get()):
                temporary = self.input_hum_low.get()
                self.input_hum_low.set(self.input_hum_high.get())
                self.input_hum_high.set(temporary)

    def __measure_period_validator(self):
        try:
            # Maximal allowed measure period is 17 hours (61200 seconds)
            if self.time_entry_measure_period.get() > 61200:
                self.time_entry_measure_period.set(61200)
            # Minimal allowed measure period is 1 seconds
            if self.time_entry_measure_period.get() < 1:
                self.time_entry_measure_period.set(1)
            # Recalculate trip duration in case if recordings number is chosen as stop condition. Just to show the user
            if self.stop_mode.get().__eq__('records'):
                self.__recalculate_trip_duration_based_on_measure_interval_and_records_number()
            elif self.stop_mode.get().__eq__('duration'):
                records_number = self.__recalculate_records_number_based_on_measure_interval_and_trip_duration()
                # If records number are exceeded device memory then block further increasing of trip interval
                self.input_max_records.set(str(records_number))
                if records_number > self.input_max_records.max:
                    self.time_entry_measure_period.set(math.ceil(self.time_entry_stop_duration.get() /
                                                                 self.input_max_records.max))
        except ValueError:
            # This exception may occur if user selects the whole content of CustomTimeEntry and replaces/deletes it.
            # That leads to the situation, when '' is passed as an argument, that is incorrect. Just ignore that.
            pass

    def __stop_duration_validator(self):
        try:
            # Minimal allowed trip duration is 1 seconds
            if self.time_entry_stop_duration.get() < 1:
                self.time_entry_stop_duration.set(1)
            # Recalculate records number
            if self.stop_mode.get().__eq__('duration'):
                records_number = self.__recalculate_records_number_based_on_measure_interval_and_trip_duration()
                # If records number are exceeded device memory then block further increasing of trip interval
                self.input_max_records.set(str(records_number))
                if records_number > self.input_max_records.max:
                    self.time_entry_stop_duration.set(self.input_max_records.max * self.time_entry_measure_period.get())
        except ValueError:
            # This exception may occur if user selects the whole content of CustomTimeEntry and replaces/deletes it.
            # That leads to the situation, when '' is passed as an argument, that is incorrect. Just ignore that.
            pass

    def __recordings_number_validator(self):
        try:
            # Maximal allowed measure period is 17 hours (61200 seconds)
            if int(self.input_max_records.get()) > self.input_max_records.max:
                self.input_max_records.set(self.input_max_records.max)
            # Minimal allowed measure period is 1 seconds
            if int(self.input_max_records.get()) < 1:
                self.input_max_records.set(str(1))
            # Recalculate trip duration in case if recordings number is chosen as stop condition. Just to show the user
            if self.stop_mode.get().__eq__('records'):
                self.__recalculate_trip_duration_based_on_measure_interval_and_records_number()
            # Total alerts number must be always not greater than total recordings number
            if int(self.input_max_records.get()) < int(self.input_total_delay.get()):
                self.input_total_delay.set(self.input_max_records.get())
        except ValueError:
            # This exception may occur if user selects the whole content of CustomInput and replaces/deletes it.
            # That leads to the situation, when '' is passed as an argument, that is incorrect. Just ignore that.
            pass

    def __recalculate_records_number_based_on_measure_interval_and_trip_duration(self) -> int:
        # Measure period should never be bigger than trip duration
        if self.time_entry_stop_duration.get() < self.time_entry_measure_period.get():
            self.time_entry_stop_duration.set(self.time_entry_measure_period.get())
        required_records_number = self.time_entry_stop_duration.get() // self.time_entry_measure_period.get()
        return required_records_number

    def __recalculate_trip_duration_based_on_measure_interval_and_records_number(self):
        trip_duration = self.time_entry_measure_period.get() * int(self.input_max_records.get())
        self.time_entry_stop_duration.set(trip_duration)

    def __stop_condition_changed(self):
        if self.stop_mode.get().__eq__('duration'):
            self.time_entry_stop_duration.state('active')
            self.input_max_records.set_state(False)
            # Recalculate measure interval immediately
            self.__recalculate_records_number_based_on_measure_interval_and_trip_duration()
        else:
            self.time_entry_stop_duration.state('disabled')
            self.input_max_records.set_state(True)
            # Recalculate trip duration immediately
            self.__recalculate_trip_duration_based_on_measure_interval_and_records_number()
