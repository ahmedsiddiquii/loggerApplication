import tkinter.ttk as ttk
from ui.constants import *
from communication.data_structure import Timestamp2020, Structure_Configuration, DataEnums
import tksheet
import gc


class UI_TabSummary(ttk.Frame):
    cell_rows = {
        'Serial #': 0,
        'Description': 1,
        'Memory size': 2,
        'Temperature range': 3,
        'Trip #': 4,
        'System type': 5,
        'State of charge': 6,
        'Firmware version': 7,
        'Temperature unit': 8,
        'Timezone': 9,
        'Timezone code': 10,
        'Start mode: auto at': 11,
        'Start mode: manual delay': 12,
        'Stop cond: duration': 13,
        'Stop cond: max. records': 14,
        'Measure period': 15,
        'Humidity sensor': 16,
        'Light sensor': 17,
        'Stop button': 18,
        'Date format': 19,
        'Time format': 20,
        'Started time': 21,
        'Stopped time': 22,
        'Stop reason': 23,
        'Recordings number': 24,
        # 'Temperature high thr. enabled': 25,
        # 'Temperature low thr. enabled': 26,
        # 'Humidity high thr. enabled': 27,
        # 'Humidity low thr. enabled': 28,
        'Temperature high thr.': 25,
        'Temperature low thr.': 26,
        'Humidity high thr.': 27,
        'Humidity low thr.': 28
    }

    options_states = ['Disabled', 'Enabled']

    def __init__(self, main_window, **kw):
        super().__init__(main_window, width=100, height=100, style='TFrame', **kw)
        self.date_fmt = '%Y-%m-%d'
        self.time_fmt = '%H:%M:%S'
        self.table = tksheet.Sheet(self, font=GUI_FONT_CONTENT, header_font=GUI_FONT_CONTENT,
                                   popup_menu_font=GUI_FONT_CONTENT, table_bg=GUI_BG_COLOR)
        self.table.headers(['Parameter', 'Value'])
        self.table.column_width(column=0, width=220)
        self.table.column_width(column=1, width=200)
        self.table.pack(expand=True, fill='both')
        self.table.enable_bindings('all')
        self.table.disable_bindings(['rc_insert_column', 'rc_delete_column', 'edit_cell', 'delete', 'paste',
                                     'cut', 'rc_delete_row', 'rc_insert_row'])
        self.table.insert_row(values=('Serial #', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Description', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Memory size', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Temperature range', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Trip #', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('System type', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('State of charge', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Firmware version', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Temperature unit', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Timezone', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Timezone code', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Start mode: auto at', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Start mode: manual delay', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Stop cond: duration', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Stop cond: max. records', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Measure period', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Humidity sensor', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Light sensor', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Stop button', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Date format', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Time format', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Started time', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Stopped time', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Stop reason', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Recordings number', ''), idx='end', add_columns=False)
        # self.table.insert_row(values=('Temperature high thr. enabled', ''), idx='end', add_columns=False)
        # self.table.insert_row(values=('Temperature low thr. enabled', ''), idx='end', add_columns=False)
        # self.table.insert_row(values=('Humidity high thr. enabled', ''), idx='end', add_columns=False)
        # self.table.insert_row(values=('Humidity low thr. enabled', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Temperature high thr.', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Temperature low thr.', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Humidity high thr.', ''), idx='end', add_columns=False)
        self.table.insert_row(values=('Humidity low thr.', ''), idx='end', add_columns=False)

    def set_metadata(self, metadata):
        self.table.set_cell_data(c=1, r=self.cell_rows['Started time'],
                                 value=Timestamp2020.convert_to_datetime_str(metadata.start_time,
                                                                             date_fmt=self.date_fmt,
                                                                             time_fmt=self.time_fmt))
        self.table.set_cell_data(c=1, r=self.cell_rows['Stopped time'],
                                 value=Timestamp2020.convert_to_datetime_str(metadata.stop_time,
                                                                             date_fmt=self.date_fmt,
                                                                             time_fmt=self.time_fmt))
        self.table.set_cell_data(c=1, r=self.cell_rows['Recordings number'], value=metadata.records_count)
        self.table.set_cell_data(c=1, r=self.cell_rows['Stop reason'],
                                 value=DataEnums.stop_reason_t.get(metadata.stop_reason, 'Unknown (error)'))
        self.table.redraw()

    def set_default_metadata(self):
        self.table.set_cell_data(c=1, r=self.cell_rows['Started time'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Stopped time'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Recordings number'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Stop reason'], value=DataEnums.stop_reason_t.get(5, '–'))

    def set_system_data(self, system_data):
        self.table.set_cell_data(c=1, r=self.cell_rows['Trip #'], value=system_data.cycle)
        self.table.set_cell_data(c=1, r=self.cell_rows['Serial #'], value=bytes(system_data.serial).decode('ascii', 'ignore'))
        self.table.set_cell_data(c=1, r=self.cell_rows['System type'],
                                 value=DataEnums.system_type_t.get(system_data.system_type, 'Unknown (error)'))
        self.table.set_cell_data(c=1, r=self.cell_rows['Temperature range'],
                                 value=DataEnums.temperature_range_t.get(system_data.temp_range, 'Unknown (error)'))
        self.table.set_cell_data(c=1, r=self.cell_rows['Memory size'], value=system_data.memory_size)
        self.table.set_cell_data(c=1, r=self.cell_rows['State of charge'],
                                 value='High' if system_data.battery_soc else 'Low')
        self.table.set_cell_data(c=1, r=self.cell_rows['Firmware version'], value=f'{system_data.fw_version[0]}.'
                                                                                  f'{system_data.fw_version[1]}.'
                                                                                  f'{system_data.fw_version[2]}')

    def set_configuration(self, configuration):
        thr_dis_val = Structure_Configuration.THR_DISABLED_VALUE
        ts_illegal_val = Structure_Configuration.TS_ILLEGAL_VALUE
        self.date_fmt = DataEnums.date_format_mask.get(configuration.date_fmt,
                                                       DataEnums.date_format_mask.get(0))
        self.time_fmt = DataEnums.time_format_mask.get(configuration.time_fmt,
                                                       DataEnums.time_format_mask.get(0))
        measure_period = Timestamp2020.convert_to_duration_str(configuration.meas_period)
        self.table.set_cell_data(c=1, r=self.cell_rows['Measure period'], value=measure_period)
        manual_delay = 'Disabled' if configuration.manual_delay.__eq__(ts_illegal_val) \
            else Timestamp2020.convert_to_duration_str(configuration.manual_delay)
        self.table.set_cell_data(c=1, r=self.cell_rows['Start mode: manual delay'],
                                 value=manual_delay)
        auto_delay = 'Disabled' if configuration.auto_delay.__eq__(ts_illegal_val) \
            else Timestamp2020.convert_to_datetime_str(configuration.auto_delay,
                                                       date_fmt=self.date_fmt,
                                                       time_fmt=self.time_fmt)
        self.table.set_cell_data(c=1, r=self.cell_rows['Start mode: auto at'],
                                 value=auto_delay)
        duration = 'Disabled' if configuration.duration_time.__eq__(0) \
            else Timestamp2020.convert_to_duration_str(configuration.duration_time)
        self.table.set_cell_data(c=1, r=self.cell_rows['Stop cond: duration'], value=duration)
        max_records = 'Disabled' if configuration.max_records.__eq__(0) else configuration.max_records
        self.table.set_cell_data(c=1, r=self.cell_rows['Stop cond: max. records'], value=max_records)
        self.table.set_cell_data(c=1, r=self.cell_rows['Description'],
                                 value=bytes(configuration.description).decode('ascii'))
        self.table.set_cell_data(c=1, r=self.cell_rows['Timezone'], value=configuration.timezone // 3600)
        self.table.set_cell_data(c=1, r=self.cell_rows['Timezone code'],
                                 value=bytes(configuration.timezone_code).decode('ascii'))
        self.table.set_cell_data(c=1, r=self.cell_rows['Temperature unit'],
                                 value=DataEnums.temperature_unit_t.get(configuration.temp_unit, 'Unknown (error)'))
        self.table.set_cell_data(c=1, r=self.cell_rows['Humidity sensor'],
                                 value=self.options_states[configuration.hum_enabled])
        self.table.set_cell_data(c=1, r=self.cell_rows['Light sensor'],
                                 value=self.options_states[configuration.als_enabled])
        self.table.set_cell_data(c=1, r=self.cell_rows['Stop button'],
                                 value=self.options_states[configuration.stop_btn_enabled])
        self.table.set_cell_data(c=1, r=self.cell_rows['Date format'],
                                 value=DataEnums.date_format_t.get(configuration.date_fmt, 'Unknown (error)'))
        self.table.set_cell_data(c=1, r=self.cell_rows['Time format'],
                                 value=DataEnums.time_format_t.get(configuration.time_fmt, 'Unknown (error)'))
        hi_temp_thr = 'Disabled' if configuration.hi_temp_thr.__eq__(thr_dis_val) \
            else DataEnums.convert_celsius_to_required(configuration.hi_temp_thr / 10, configuration.temp_unit)
        lo_temp_thr = 'Disabled' if configuration.lo_temp_thr.__eq__(thr_dis_val) \
            else DataEnums.convert_celsius_to_required(configuration.lo_temp_thr / 10, configuration.temp_unit)
        hi_hum_thr = 'Disabled' if configuration.hi_hum_thr.__eq__(thr_dis_val) else configuration.hi_hum_thr / 10
        lo_hum_thr = 'Disabled' if configuration.lo_hum_thr.__eq__(thr_dis_val) else configuration.lo_hum_thr / 10
        self.table.set_cell_data(c=1, r=self.cell_rows['Temperature high thr.'], value=hi_temp_thr)
        self.table.set_cell_data(c=1, r=self.cell_rows['Temperature low thr.'], value=lo_temp_thr)
        self.table.set_cell_data(c=1, r=self.cell_rows['Humidity high thr.'], value=hi_hum_thr)
        self.table.set_cell_data(c=1, r=self.cell_rows['Humidity low thr.'], value=lo_hum_thr)

    def set_initial_data(self):
        self.set_default_metadata()
        self.table.set_cell_data(c=1, r=self.cell_rows['Description'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Measure period'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Start mode: manual delay'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Start mode: auto at'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Stop cond: duration'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Stop cond: max. records'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Description'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Timezone'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Timezone code'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Temperature unit'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Humidity sensor'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Light sensor'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Stop button'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Date format'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Time format'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Temperature high thr.'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Temperature low thr.'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Humidity high thr.'], value='–')
        self.table.set_cell_data(c=1, r=self.cell_rows['Humidity low thr.'], value='–')
        #self.table.redraw()

    def ui_delete(self):
        self.table.destroy()
        self.table.RI.destroy()
        self.table.CH.destroy()
        self.table.MT.destroy()
        self.table.TL.destroy()
        del self.table
        self.destroy()
        gc.collect(1)
