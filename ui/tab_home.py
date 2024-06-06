from tkinter import *
from tkinter import ttk
from ui.constants import *
from communication.data_structure import Timestamp2020, DataEnums, Structure_Configuration
import gc

UI_Y_OFFSET = 20
LABEL_X_OFFSET = AXIS_X_OFFSET + 150


class UI_TabHome(ttk.Frame):

    def __init__(self, main_window, style='TFrame', **kw):
        super().__init__(main_window, **kw)
        self.main_window = main_window
        self.date_format_mask = '%Y-%m-%d'
        self.time_format_mask = '%H:%M:%S'
        # Widgets
        self.canvas = None
        self.label_product_id = None
        self.label_description = None
        self.label_serial = None
        self.label_memory_size = None
        self.label_temp_range = None
        self.label_trip_number = None
        self.label_system_type = None
        self.label_soc = None
        self.label_fw_version = None
        self.label_timezone = None
        self.label_start_time = None
        self.label_stop_time = None
        self.label_records_count = None
        self.label_stop_reason = None
        # Render
        self.__ui_create()
        self.__ui_start()

    def __ui_create(self):
        self.canvas = Canvas(self, width=GUI_DEVICE_SETTINGS_WIDTH,
                             bg=GUI_BG_COLOR, cursor='arrow')
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET, anchor=W,
                                text='Product ID:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_product_id = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET, anchor=W, text='',
                                                        font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 20, anchor=W,
                                text='Serial #:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_serial = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 20, anchor=W, text='',
                                                    font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 40, anchor=W,
                                text='System type:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_system_type = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 40, anchor=W, text='',
                                                         font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 60, anchor=W,
                                text='Temp. range, \xB0C:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_temp_range = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 60, anchor=W, text='',
                                                        font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 80, anchor=W,
                                text='Trip #:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_trip_number = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 80, anchor=W, text='',
                                                         font=GUI_FONT_CONTENT,
                                                         justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 100, anchor=W,
                                text='Memory size:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_memory_size = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 100, anchor=W, text='',
                                                         font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 120, anchor=W,
                                text='State of charge:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_soc = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 120, anchor=W, text='',
                                                 font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 140, anchor=W,
                                text='Firmware version:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_fw_version = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 140, anchor=W, text='',
                                                        font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 160, anchor=W,
                                text='Time zone:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_timezone = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 160, anchor=W, text='',
                                                      font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 180, anchor=W,
                                text='Start time:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_start_time = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 180, anchor=W, text='',
                                                        font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 200, anchor=W,
                                text='Stop time:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_stop_time = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 200, anchor=W, text='',
                                                       font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 220, anchor=W,
                                text='Stop reason:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_stop_reason = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 220, anchor=W, text='',
                                                         font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 240, anchor=W,
                                text='Records number:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_records_count = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 240, anchor=W, text='',
                                                           font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 260, anchor=W,
                                text='Description:', font=GUI_FONT_CONTENT, justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_description = self.canvas.create_text(LABEL_X_OFFSET, UI_Y_OFFSET + 252, anchor=NW, text='',
                                                         font=GUI_FONT_CONTENT, justify=LEFT, fill=GUI_FONT_COLOR)

    def set_configuration(self, configuration):
        sign = ' ' if configuration.timezone.__eq__(0) else '-' if configuration.timezone.__lt__(0) else '+'
        code = Structure_Configuration.arr_to_string(configuration.timezone_code).rstrip('\x00')
        self.canvas.itemconfig(self.label_timezone, text=f'{code}{sign}{configuration.timezone // 3600}')
        self.canvas.itemconfig(self.label_description,
                               text=Structure_Configuration.arr_to_string(configuration.description))
        self.date_format_mask = DataEnums.date_format_mask.get(configuration.date_fmt,
                                                               DataEnums.date_format_mask.get(0))
        self.time_format_mask = DataEnums.time_format_mask.get(configuration.time_fmt,
                                                               DataEnums.time_format_mask.get(0))

    def set_metadata(self, metadata):
        self.canvas.itemconfig(self.label_start_time,
                               text=Timestamp2020.convert_to_datetime_str(metadata.start_time,
                                                                          date_fmt=self.date_format_mask,
                                                                          time_fmt=self.time_format_mask))
        self.canvas.itemconfig(self.label_stop_time,
                               text=Timestamp2020.convert_to_datetime_str(metadata.stop_time,
                                                                          date_fmt=self.date_format_mask,
                                                                          time_fmt=self.time_format_mask))
        self.canvas.itemconfig(self.label_records_count, text=metadata.records_count)
        self.canvas.itemconfig(self.label_stop_reason,
                               text=DataEnums.stop_reason_t.get(metadata.stop_reason, 'Unknown (error)'))

    def set_default_metadata(self):
        self.canvas.itemconfig(self.label_start_time, text='–')
        self.canvas.itemconfig(self.label_stop_time, text='–')
        self.canvas.itemconfig(self.label_records_count, text='–')
        self.canvas.itemconfig(self.label_stop_reason, text=DataEnums.stop_reason_t.get(5, '–'))

    def set_system_data(self, system_data):
        self.canvas.itemconfig(self.label_trip_number, text=system_data.cycle)
        self.canvas.itemconfig(self.label_serial, text=Structure_Configuration.arr_to_string(system_data.serial))
        self.canvas.itemconfig(self.label_product_id,
                               text=DataEnums.product_codes_t.get(system_data.system_type, 'Unknown (error)'))
        self.canvas.itemconfig(self.label_system_type,
                               text=DataEnums.system_type_t.get(system_data.system_type, 'Unknown (error)'))
        self.canvas.itemconfig(self.label_temp_range,
                               text=DataEnums.temperature_range_t.get(system_data.temp_range, 'Unknown (error)'))
        self.canvas.itemconfig(self.label_memory_size, text=system_data.memory_size)
        self.canvas.itemconfig(self.label_soc, text='High' if system_data.battery_soc else 'Low')
        self.canvas.itemconfig(self.label_fw_version, text=f'{system_data.fw_version[0]}.'
                                                           f'{system_data.fw_version[1]}.'
                                                           f'{system_data.fw_version[2]}')

    def set_initial_data(self):
        self.set_default_metadata()
        self.canvas.itemconfig(self.label_timezone, text='–')
        self.canvas.itemconfig(self.label_description, text='–')

    def __ui_start(self):
        self.canvas.pack(expand=1, fill='both')

    def ui_delete(self):
        self.canvas.pack_forget()
        self.destroy()
        gc.collect(1)
