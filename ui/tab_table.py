import tkinter.ttk as ttk
from communication.data_structure import DataEnums
from ui.constants import *
import tksheet
import gc


class UI_TabTable(ttk.Frame):

    def __init__(self, main_window, **kw):
        super().__init__(main_window, width=100, height=100, style='TFrame', **kw)
        self.configuration = None
        self.table = tksheet.Sheet(self, font=GUI_FONT_CONTENT, header_font=GUI_FONT_CONTENT,
                                   popup_menu_font=GUI_FONT_CONTENT, table_bg=GUI_BG_COLOR)
        self.table.headers(['Timestamp', 'Temperature, °C', 'Humidity, %', 'Annotation'])
        self.table.column_width(column=0, width=180, only_set_if_too_small=False)
        self.table.column_width(column=2, width=100, only_set_if_too_small=False)
        self.table.column_width(column=3, width=180, only_set_if_too_small=False)
        self.table.pack(expand=True, fill='both')
        self.table.enable_bindings('all')
        self.table.disable_bindings(['rc_insert_column', 'rc_delete_column', 'edit_cell', 'delete', 'paste',
                                     'cut', 'rc_delete_row', 'rc_insert_row'])

    def add(self, timestamp, temperature, humidity, is_tampered, is_bookmark):
        self.table.insert_row(values=(timestamp, temperature, humidity, is_tampered, is_bookmark),
                              idx='end', add_columns=False)

    def clear(self):
        self.table.select_all(redraw=False, run_binding_func=True)
        rows_number = len(self.table.get_selected_rows(get_cells_as_rows=True))
        self.table.MT.del_row_positions(idx=0, numrows=rows_number, deselect_all=True)

    def set_configuration(self, configuration):
        self.configuration = configuration

    def set_recordings(self, recordings):
        # self.clear()
        temperature_symbol = DataEnums.temperature_unit_t.get(self.configuration.temp_unit,
                                                              DataEnums.temperature_unit_t.get(0))[:1]
        self.table.headers(['Timestamp', f'Temperature, °{temperature_symbol}', 'Humidity, %', 'Annotation'])
        date_fmt = DataEnums.date_format_mask.get(self.configuration.date_fmt,
                                                  DataEnums.date_format_mask.get(0))
        time_fmt = DataEnums.time_format_mask.get(self.configuration.time_fmt,
                                                  DataEnums.time_format_mask.get(0))
        self.table.set_column_data(values=[ts.strftime(f'{date_fmt} {time_fmt}') for ts in recordings.timestamp], c=0,
                                   redraw=True)
        self.table.set_column_data(values=recordings.temperature, c=1, redraw=True)
        self.table.set_column_data(values=recordings.humidity, c=2, redraw=True)
        annotation_list = [self.__get_annotation(x, y) for x, y in zip(recordings.is_tampered, recordings.is_bookmark)]
        self.table.set_column_data(values=annotation_list, c=3, redraw=True)

    @staticmethod
    def __get_annotation(is_tampered: bool, is_bookmark: bool) -> str:
        annotation = ''
        if is_tampered:
            annotation += 'Tampered, '
        if is_bookmark:
            annotation += 'Bookmark'
        return annotation.strip(', ')

    def ui_delete(self):
        self.table.destroy()
        self.table.RI.destroy()
        self.table.CH.destroy()
        self.table.MT.destroy()
        self.table.TL.destroy()
        del self.table
        self.destroy()
        gc.collect(1)
