from tkinter import *
from ui.constants import *
from enum import IntEnum


class FileIndexes(IntEnum):
    # Be sure that commands in menu bar are declared in the same order (separators are missed)
    FILE_OPTIONS_IDX = 0
    FILE_GEN_PDF_IDX = 2
    FILE_GEN_TXT_IDX = 3
    FILE_GEN_CSV_IDX = 4
    FILE_LOAD_CONFIG = 6
    FILE_EXIT_IDX = 8


class LoggerIndexes(IntEnum):
    LOGGER_READ = 0
    LOGGER_PROGRAM = 1
    LOGGER_SAVE_TEMPLATE = 3
    LOGGER_APPLY_TEMPLATE = 4


class UI_MenuBar(Menu):

    def __init__(self, root, **kw):
        super().__init__(root, **kw)
        self.file_menu = Menu(self, tearoff=0)
        self.file_menu.add_command(label='Options', command=None, font=GUI_FONT_MENU)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Generate PDF', command=None, font=GUI_FONT_MENU)
        self.file_menu.add_command(label='Generate TXT', command=None, font=GUI_FONT_MENU)
        self.file_menu.add_command(label='Generate CSV', command=None, font=GUI_FONT_MENU)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Load template', command=None, font=GUI_FONT_MENU)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=None, font=GUI_FONT_MENU)
        self.logger_menu = Menu(self, tearoff=0)
        self.logger_menu.add_command(label='Read', command=None, font=GUI_FONT_MENU)
        self.logger_menu.add_command(label='Program', command=None, font=GUI_FONT_MENU)
        self.logger_menu.add_separator()
        self.logger_menu.add_command(label='Save template', command=None, font=GUI_FONT_MENU)
        self.logger_menu.add_command(label='Apply template', command=None, font=GUI_FONT_MENU)
        self.help_menu = Menu(self, tearoff=0)
        self.help_menu.add_command(label='About', command=None, font=GUI_FONT_MENU)
        self.add_cascade(label='File', menu=self.file_menu, font=GUI_FONT_MENU)
        self.add_cascade(label='Device', menu=self.logger_menu, font=GUI_FONT_MENU)
        self.add_cascade(label='Help', menu=self.help_menu, font=GUI_FONT_MENU)

    def set_button_exit_callback(self, callback):
        self.file_menu.entryconfigure(FileIndexes.FILE_EXIT_IDX.value, command=callback)

    def set_button_read_callback(self, callback):
        self.logger_menu.entryconfigure(LoggerIndexes.LOGGER_READ.value, command=callback)

    def set_button_program_callback(self, callback):
        self.logger_menu.entryconfigure(LoggerIndexes.LOGGER_PROGRAM.value, command=callback)

    def set_button_options_callback(self, callback):
        self.file_menu.entryconfigure(FileIndexes.FILE_OPTIONS_IDX.value, command=callback)

    def set_button_save_template_callback(self, callback):
        self.logger_menu.entryconfigure(LoggerIndexes.LOGGER_SAVE_TEMPLATE.value, command=callback)

    def set_button_load_template_callback(self, callback):
        self.file_menu.entryconfigure(FileIndexes.FILE_LOAD_CONFIG.value, command=callback)

    def set_button_apply_template_callback(self, callback):
        self.logger_menu.entryconfigure(LoggerIndexes.LOGGER_APPLY_TEMPLATE.value, command=callback)

    def set_button_export_pdf_callback(self, callback):
        self.file_menu.entryconfigure(FileIndexes.FILE_GEN_PDF_IDX.value, command=callback)

    def set_button_export_txt_callback(self, callback):
        self.file_menu.entryconfigure(FileIndexes.FILE_GEN_TXT_IDX.value, command=callback)

    def set_button_export_csv_callback(self, callback):
        self.file_menu.entryconfigure(FileIndexes.FILE_GEN_CSV_IDX.value, command=callback)

    def set_button_about_callback(self, callback):
        self.help_menu.entryconfigure(0, command=callback)
