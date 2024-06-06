import threading

import httpx

from ui.device_tree import UI_DeviceTree
from ui.menu_bar import UI_MenuBar
from ui.tool_bar import UI_ToolBar
from ui.options_window import UI_OptionsWindow
from ui.about_window import UI_AboutWindow
from ui.constants import *
from tkinter.filedialog import asksaveasfile, askopenfile
from tkinter import messagebox as mb, Toplevel, Label, TOP
from communication.data_structure import Structure_Configuration
from communication.reports import Reports
from threading import Thread
from time import sleep
import serial.tools.list_ports
from typing import Optional
import gc

STLINK_VID = 1155
SILICON_LABS_CP210X_VID = 4292

STLINK_PID = 14155

DEVICES_SCANNING_PERIOD = 2000


class UI_MainWindow:
    legal_vids = [STLINK_VID, SILICON_LABS_CP210X_VID]
    blocked_pids = [STLINK_PID]

    def __init__(self, root):
        self.root = root
        self.is_template_loaded: bool = False
        self.config_template: Optional[Structure_Configuration] = None
        self.root.protocol("WM_DELETE_WINDOW", self.__ui_quit)
        self.root.iconbitmap(ICON_APP)
        self.tool_bar = UI_ToolBar(root)
        self.tool_bar.set_button_options_callback(self.__ui_open_options)
        self.tool_bar.set_button_read_callback(self.__read_device_data)
        self.tool_bar.set_button_program_callback(self.__program_device_data)
        self.tool_bar.set_button_save_config_callback(self.__save_config_template)
        self.tool_bar.set_button_load_config_callback(self.__load_config_template)
        self.tool_bar.set_button_apply_config_callback(self.__apply_config_template)
        self.tool_bar.set_button_txt_callback(self.__save_txt_report)
        self.tool_bar.set_button_pdf_callback(self.__save_pdf_report)
        self.tool_bar.set_button_csv_callback(self.__save_csv_report)

        self.tool_bar.set_button_pdf_upload_callback(self.__upload_pdf_report)

        self.menu_bar = UI_MenuBar(root)
        self.menu_bar.set_button_options_callback(self.__ui_open_options)
        self.menu_bar.set_button_exit_callback(self.__ui_quit)
        self.menu_bar.set_button_read_callback(self.__read_device_data)
        self.menu_bar.set_button_program_callback(self.__program_device_data)
        self.menu_bar.set_button_save_template_callback(self.__save_config_template)
        self.menu_bar.set_button_load_template_callback(self.__load_config_template)
        self.menu_bar.set_button_apply_template_callback(self.__apply_config_template)
        self.menu_bar.set_button_export_pdf_callback(self.__save_pdf_report)
        self.menu_bar.set_button_export_txt_callback(self.__save_txt_report)
        self.menu_bar.set_button_export_csv_callback(self.__save_csv_report)
        self.menu_bar.set_button_about_callback(self.__ui_open_about)
        self.device_tree = UI_DeviceTree(root)

    def ui_start_mainloop(self):
        self.root.title(f'{GUI_TITLE} {GUI_VERSION}')
        self.root.resizable(False, False)
        self.root.deiconify()
        self.root.config(menu=self.menu_bar)
        # Start scanning COM-ports
        self.__scan_comports()
        # Start mainloop
        self.root.mainloop()

    def __ui_open_about(self):
        about = UI_AboutWindow(self.root)
        about.grab_set()

    def __ui_open_options(self):
        options = UI_OptionsWindow(self.root, self.__options_submit_callback)
        options.grab_set()

    def __options_submit_callback(self):
        for device in self.device_tree.connected_devices:
            device.device_menu.tab_program.update_datetime_format()

    def __ui_quit(self):
        connected_devices = self.device_tree.get_connected_devices()
        # Correctly disconnect all devices
        for device in connected_devices:
            if device.is_reading_in_progress:
                return
            device.disconnect()
        self.root.quit()
        # self.root.destroy()

    def __scan_comports(self):
        comports_list = serial.tools.list_ports.comports()
        # Check if we need to remove disconnected devices
        connected_ports = self.device_tree.get_connected_ports()
        for device_port in connected_ports:
            if device_port not in comports_list:
                self.device_tree.remove_device_by_port(device_port)
        if not self.device_tree.get_connected_devices():
            # If there are no more devices left then we have to return the hint
            self.device_tree.add_hint()
        # Check if we need to add new device
        for device_port in comports_list:
            if (device_port.vid in self.legal_vids) and (device_port not in connected_ports) and \
                    (device_port.pid not in self.blocked_pids):
                self.device_tree.add_device(device_port)
        self.root.after(DEVICES_SCANNING_PERIOD, self.__scan_comports)

    def __read_device_data(self):
        active_device = self.device_tree.get_active_device()
        print(f'Active device is {active_device}')
        if active_device is not None:
            Thread(target=active_device.read_data_from_device).start()
        else:
            mb.showerror(title='Error!', message='Device should be selected first!')

    def __program_device_data(self):
        active_device = self.device_tree.get_active_device()
        print(f'Active device is {active_device}')
        if active_device is not None:
            active_device.device_menu.program_device()
        else:
            mb.showerror(title='Error!', message='Device should be selected first!')

    def __save_config_template(self):
        active_device = self.device_tree.get_active_device()
        print(f'Active device is {active_device}')
        if active_device is not None:
            try:
                template_file = asksaveasfile(initialfile='config_template.lct', defaultextension='.lct',
                                              filetypes=[('Logger configuration templates', '*.lct'), ],
                                              mode='wb')
                if template_file is not None:
                    active_device.device_menu.tab_program.save_data_to_configuration(active_device.configuration)
                    template_file.write(bytearray(active_device.configuration))
                    template_file.close()
                    del template_file
            except Exception as e:
                print(f'Unexpected error occurred. Saving process interrupted: {e}')
        else:
            mb.showerror(title='Error!', message='Device should be selected first!')
        del active_device
        gc.collect(1)

    def __load_config_template(self):
        try:
            template_file = askopenfile(initialfile='config_template.lct', defaultextension='.lct',
                                        filetypes=[('Logger configuration templates', '*.lct'), ],
                                        mode='rb')
            if template_file is not None:
                self.config_template = Structure_Configuration.from_buffer(bytearray(template_file.read()))
                # Adjusting timestamps relative to used time zone
                if self.config_template.auto_delay.__ne__(Structure_Configuration.TS_ILLEGAL_VALUE):
                    self.config_template.auto_delay += self.config_template.timezone
                template_file.close()
                del template_file
                if not self.is_template_loaded:
                    self.is_template_loaded = True
                    self.tool_bar.unlock_apply_button()
        except Exception as e:
            print(f'Unexpected error occurred. Loading process interrupted: {e}')
        gc.collect(1)

    def __apply_config_template(self):
        if not self.is_template_loaded:
            return
        active_device = self.device_tree.get_active_device()
        print(f'Active device is {active_device}')
        if active_device is not None:
            active_device.device_menu.tab_program.set_configuration(self.config_template)
        else:
            mb.showerror(title='Error!', message='Device should be selected first!')
        del active_device
        gc.collect(1)

    def __save_pdf_report(self):
        active_device = self.device_tree.get_active_device()
        print(f'Active device is {active_device}')
        if active_device is not None:
            report = Reports(active_device.usb_label)
            try:
                report.save_pdf_report()
            except OSError:
                mb.showerror(title='Error!', message='Cannot access PDF report!')
            report.clean()
            del report
        else:
            mb.showerror(title='Error!', message='Device should be selected first!')
        del active_device
        gc.collect(1)

    def __save_txt_report(self):
        active_device = self.device_tree.get_active_device()
        print(f'Active device is {active_device}')
        if active_device is not None:
            report = Reports(active_device.usb_label)
            try:
                report.save_txt_report()
            except OSError:
                mb.showerror(title='Error!', message='Cannot access TXT report!')
            report.clean()
            del report
        else:
            mb.showerror(title='Error!', message='Device should be selected first!')
        del active_device
        gc.collect(1)

    def __save_csv_report(self):
        active_device = self.device_tree.get_active_device()
        print(f'Active device is {active_device}')
        if active_device is not None:
            report = Reports(active_device.usb_label)
            try:
                report.save_csv_report()
            except OSError:
                mb.showerror(title='Error!', message='Cannot access CSV report!')
            report.clean()
            del report
        else:
            mb.showerror(title='Error!', message='Device should be selected first!')
        del active_device
        gc.collect(1)
    
    @staticmethod
    def __upload_pdf_report_exec(path, usb_label, dialog):
        response = httpx.post(
            'https://equartz.tech/pdf/upload_pdf.php',
            data={'serial_no': usb_label},
            files={'pdf_file': open(path, 'rb')},
            headers={'User-Agent': 'PostmanRuntime/7.29.10'},
        )

        dialog.grab_release()
        dialog.destroy()

        if response.status_code == 200:
            mb.showinfo(title='Success!', message='Successfully uploaded the PDF file!')
        else:
            mb.showerror(title='Error', message=f"PDF file upload failed {response.text}")
    
    def __upload_pdf_report(self):
        active_device = self.device_tree.get_active_device()
        print(f'Active device is {active_device}')
        if active_device is not None:
            report = Reports(active_device.usb_label)
            try:
                progress_dialog = Toplevel()
                progress_dialog.title('Uploading PDF Report')

                dialog_width = 400
                dialog_height = 50
                x = (self.root.winfo_screenwidth() - dialog_width) // 2
                y = (self.root.winfo_screenheight() - dialog_height) // 2
                progress_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
                progress_dialog.protocol("WM_DELETE_WINDOW", lambda _: print(''))

                progress_label = Label(progress_dialog, text="Please wait while report is being uploaded ...")

                progress_label.pack(side=TOP, pady=10)
                progress_dialog.grab_set()

                pdf_path, usb_label = report.upload_pdf_report()

                upload_thread = threading.Thread(target=UI_MainWindow.__upload_pdf_report_exec,
                                                 args=(pdf_path, usb_label, progress_dialog))
                upload_thread.start()
            except OSError as e:
                progress_dialog.grab_release()
                progress_dialog.destroy()

                mb.showerror(title='Error!', message=f'Cannot access PDF report! {e}')
            report.clean()
            del report
        else:
            mb.showerror(title='Error!', message='Device should be selected first!')
        del active_device
        gc.collect(1)

