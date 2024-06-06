from tkinter import *
from widgets.custom_imagebutton import CustomImageButton
from ui.constants import *

EXPORT_OFFSET = 5
UPDATE_OFFSET = 130
CONFIG_OFFSET = 220
OPTIONS_OFFSET = 340


class UI_ToolBar:

    def __init__(self, main_window):
        self.main_window = main_window
        self.canvas_toolbar = Canvas(self.main_window, width=GUI_TOTAL_WIDTH, height=GUI_TOOLBAR_HEIGHT,
                                     bg=GUI_BG_COLOR, cursor='arrow')
        self.button_options_callback = lambda: print('Opened options')
        self.button_read_callback = lambda: print('Read device data')
        self.button_program_callback = lambda: print('Program device')
        self.button_save_config_callback = lambda: print('Saved config as template')
        self.button_load_config_callback = lambda: print('Loaded config as template')
        self.button_apply_config_callback = lambda: print('Applied template as config')
        self.button_pdf_callback = lambda: print('Exported PDF')
        self.button_txt_callback = lambda: print('Exported TXT')
        self.button_csv_callback = lambda: print('Exported CSV')
        self.button_upload_pdf_callback = lambda: print('Upload PDF')
        self.__ui_create()
        self.__ui_start()

    def set_button_read_callback(self, callback):
        self.button_read_callback = callback

    def set_button_program_callback(self, callback):
        self.button_program_callback = callback

    def set_button_save_config_callback(self, callback):
        self.button_save_config_callback = callback

    def set_button_load_config_callback(self, callback):
        self.button_load_config_callback = callback

    def set_button_apply_config_callback(self, callback):
        self.button_apply_config_callback = callback

    def set_button_options_callback(self, callback):
        self.button_options_callback = callback

    def set_button_pdf_callback(self, callback):
        self.button_pdf_callback = callback

    def set_button_txt_callback(self, callback):
        self.button_txt_callback = callback

    def set_button_csv_callback(self, callback):
        self.button_csv_callback = callback

    def set_button_pdf_upload_callback(self, callback):
        self.button_upload_pdf_callback = callback

    def __ui_create(self):
        image_button_export_pdf = CustomImageButton(self.canvas_toolbar, width=32, height=32, bgcolor=GUI_BG_COLOR,
                                                    image_active=ICON_EXPORT_PDF,
                                                    image_inactive=ICON_EXPORT_PDF,
                                                    tip='Export PDF file',
                                                    command=lambda: self.button_pdf_callback())
        self.canvas_toolbar.create_window(EXPORT_OFFSET, 4, window=image_button_export_pdf, anchor=NW)
        image_button_export_txt = CustomImageButton(self.canvas_toolbar, width=32, height=32, bgcolor=GUI_BG_COLOR,
                                                    image_active=ICON_EXPORT_TXT,
                                                    image_inactive=ICON_EXPORT_TXT,
                                                    tip='Export TXT file',
                                                    command=lambda: self.button_txt_callback())
        self.canvas_toolbar.create_window(EXPORT_OFFSET + 35, 4, window=image_button_export_txt, anchor=NW)
        image_button_export_csv = CustomImageButton(self.canvas_toolbar, width=32, height=32, bgcolor=GUI_BG_COLOR,
                                                    image_active=ICON_EXPORT_CSV,
                                                    image_inactive=ICON_EXPORT_CSV,
                                                    tip='Export CSV file',
                                                    command=lambda: self.button_csv_callback())
        self.canvas_toolbar.create_window(EXPORT_OFFSET + 70, 4, window=image_button_export_csv, anchor=NW)

        self.image_button_upload_pdf = CustomImageButton(self.canvas_toolbar, width=32, height=32,
                                                           bgcolor=GUI_BG_COLOR,
                                                           image_active=ICON_UPLOAD_PDF,
                                                           image_inactive=ICON_UPLOAD_PDF,
                                                           tip='Upload PDF report',
                                                           command=lambda: self.button_upload_pdf_callback())
        self.canvas_toolbar.create_window(EXPORT_OFFSET + 120, 4, window=self.image_button_upload_pdf, anchor=NW)
        """
        image_button_options = CustomImageButton(self.canvas_toolbar, width=32, height=32, bgcolor=GUI_BG_COLOR,
                                                 image_active=ICON_OPTIONS,
                                                 image_inactive=ICON_OPTIONS,
                                                 tip='Options',
                                                 command=lambda: self.button_options_callback())
        self.canvas_toolbar.create_window(OPTIONS_OFFSET, 4, window=image_button_options, anchor=NW)
        image_button_program = CustomImageButton(self.canvas_toolbar, width=32, height=32, bgcolor=GUI_BG_COLOR,
                                                 image_active=ICON_PROGRAM,
                                                 image_inactive=ICON_PROGRAM,
                                                 tip='Program device',
                                                 command=lambda: self.button_program_callback())
        self.canvas_toolbar.create_window(UPDATE_OFFSET + 35, 4, window=image_button_program, anchor=NW)
        image_button_read = CustomImageButton(self.canvas_toolbar, width=32, height=32, bgcolor=GUI_BG_COLOR,
                                              image_active=ICON_READ,
                                              image_inactive=ICON_READ,
                                              tip='Read from device',
                                              command=lambda: self.button_read_callback())
        self.canvas_toolbar.create_window(UPDATE_OFFSET, 4, window=image_button_read, anchor=NW)
        image_button_save_config = CustomImageButton(self.canvas_toolbar, width=32, height=32, bgcolor=GUI_BG_COLOR,
                                                     image_active=ICON_SAVE_CONFIG,
                                                     image_inactive=ICON_SAVE_CONFIG,
                                                     tip='Save configuration as template',
                                                     command=lambda: self.button_save_config_callback())
        self.canvas_toolbar.create_window(CONFIG_OFFSET, 4, window=image_button_save_config, anchor=NW)
        image_button_load_config = CustomImageButton(self.canvas_toolbar, width=32, height=32, bgcolor=GUI_BG_COLOR,
                                                     image_active=ICON_LOAD_CONFIG,
                                                     image_inactive=ICON_LOAD_CONFIG,
                                                     tip='Load configuration template',
                                                     command=lambda: self.button_load_config_callback())
        self.canvas_toolbar.create_window(CONFIG_OFFSET + 35, 4, window=image_button_load_config, anchor=NW)
        self.image_button_apply_config = CustomImageButton(self.canvas_toolbar, width=32, height=32,
                                                           bgcolor=GUI_BG_COLOR,
                                                           image_active=ICON_APPLY_CONFIG_ACTIVE,
                                                           image_inactive=ICON_APPLY_CONFIG_INACTIVE,
                                                           tip='Apply configuration without programming',
                                                           command=lambda: self.button_apply_config_callback())
        self.image_button_apply_config.set_state('DISABLED')
        self.canvas_toolbar.create_window(CONFIG_OFFSET + 70, 4, window=self.image_button_apply_config, anchor=NW)
        """

    def unlock_apply_button(self):
        self.image_button_apply_config.set_state('ENABLED')

    def __ui_start(self):
        self.canvas_toolbar.pack()
