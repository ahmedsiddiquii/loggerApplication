from tkinter import *
from tkinter import messagebox as mb
from ui.constants import *
from ui.popup import UI_PopUp
from communication.protocol import CODE_NACK
from communication.data_structure import Structure_SystemData, Structure_Metadata, Structure_Configuration, \
    Structure_Records, Container_Recordings, Timestamp2020
from communication.protocol import Protocol, ProtocolExchangeException
from communication.reports import Reports
from widgets.custom_imagebutton import CustomImageButton
import ctypes
import serial.tools.list_ports
from time import sleep
from idlelib.tooltip import Hovertip
from PIL import ImageTk, Image
from threading import Thread
import gc
import httpx

UI_Y_OFFSET = 20


class UI_Device:

    def __init__(self, device_tree, device_comport):
        self.device_tree = device_tree
        self.tkroot = device_tree.main_window
        self.parent = device_tree.frame_tree
        self.device_instances_list = device_tree.connected_devices
        self.device_port = device_comport
        self.device_menu = None
        self.interface = None
        self.system_data = None
        self.metadata = None
        self.configuration = Structure_Configuration()
        self.recordings = Container_Recordings()
        self.is_time_synchronised = False
        self.is_active = False
        self.is_connected = False
        self.is_programming_in_progress = False
        self.is_reading_in_progress = False
        self.is_spinner_stopped = True
        self.is_not_configured = False
        self.thread_spinner = None
        self.is_popup_activated = False
        self.popup_message: str = ''
        self.usb_label = None
        self.ht = None
        # Widgets
        self.canvas = None
        self.label_name = None
        self.label_serial_number = None
        self.button_make_active = None
        self.button_reconnect = None
        self.image_status = None
        self.image_status_ok = None
        self.image_status_error = None
        self.image_status_not_configured = None
        # Creating UI
        self.__ui_create()
        self.__ui_start()
        self.__create_popup()

    def make_active(self):
        for device in self.device_instances_list:
            device.is_active = False
            device.device_menu.ui_stop()
            if device.is_connected:
                device.button_make_active.set_state('ENABLED')
        self.device_menu.ui_start()
        self.is_active = True
        self.button_make_active.set_state('DISABLED')

    def delete(self):
        self.disconnect()
        self.device_menu.ui_delete()
        self.__ui_stop()
        self.canvas.destroy()
        self.button_make_active.destroy()
        self.button_reconnect.destroy()
        del self.system_data
        del self.metadata
        del self.configuration
        del self.recordings
        del self.interface
        del self.device_instances_list
        del self.image_status
        del self.image_status_ok
        del self.image_status_error
        del self.image_status_connecting
        del self.image_status_no_connection
        del self.image_status_loading
        del self.image_status_not_configured
        del self.button_make_active
        del self.button_reconnect
        del self.ht
        del self
        gc.collect(1)

    def connect(self) -> bool:
        # Firstly we try to open serial port.
        # If it is already opened it will also throw SerialException: PermissionError - just skip it
        try:
            self.interface = Protocol(self.device_port.name)
        except serial.serialutil.SerialException as e:
            if self.interface is not None:
                self.interface.serial_if.close()
            sleep(0.5)
            return False
        except:
            print('Device: exception, uncatched')
        # Then we try to send sync request to the device.
        # If port is not opened or some error occurred during communication we must release serial
        # mutex to unlock further communication
        is_connected = False
        print('Device: connecting to device')
        try:
            is_connected = self.interface.connect_to_device()
        except serial.serialutil.SerialException as e:
            print('Device: exception, releasing mutexes')
            if self.interface.mutex.locked():
                self.interface.mutex.release()
        except AttributeError:
            print('Device: exception, port wasn`t opened')
            # Port was not previously opened
            pass
        return is_connected

    def disconnect(self):
        self.__stop_spinner()
        try:
            self.interface.disconnect()
        except AttributeError:
            print(f'Cannot close {self.device_port} - port instance is None')

    def write_logs(self,msg):
        with open("logs.txt","a") as file:
            file.writelines(msg+"\n")
    def upload_pdf_report_exec(self,path, usb_label):
        response = httpx.post(
            'https://equartz.tech/pdf/upload_pdf.php',
            #'https://equartz.tech/pdf/upload_pdf.php',
            data={'serial_no': usb_label},
            files={'pdf_file': open(path, 'rb')},
            headers={'User-Agent': 'PostmanRuntime/7.29.10'},
        )


        if response.status_code == 200:
            print('Successfully uploaded the PDF file!')
            self.write_logs('Successfully uploaded the PDF file!')
        else:
            print(f"PDF file upload failed {response.text}")
            self.write_logs(f"PDF file upload failed {response.text}")

    def upload_data_to_server(self,usb_label):
        report = Reports(usb_label)
        pdf_path, usb_label = report.upload_pdf_report()
        upload_thread = Thread(target=self.upload_pdf_report_exec,
                                         args=(pdf_path, usb_label))
        upload_thread.start()

    def read_data_from_device(self):
        if self.is_reading_in_progress or self.is_programming_in_progress:
            return
        self.is_reading_in_progress = True
        self.update_device_status('updating')
        status: str = 'no_connection'
        try:
            self.__read_usb_label()
            self.__read_system_data_from_device()
            self.__read_configuration_from_device()
            self.__read_metadata_from_device()
            self.__read_recordings_from_device()
            self.__update_device_serial()

            if self.is_not_configured:
                status: str = 'initial'
                self.__set_initial_data()
            elif self.metadata.records_count.__eq__(0):
                status: str = 'not_started_yet'
            else:
                status: str = 'updated'
                try:
                    Thread(target=self.upload_data_to_server,args=(self.usb_label,)).start()
                except Exception as e:
                    self.write_logs(f"Error while uploading data {str(e)}")
                    print("Error while uploading data")
                    print(e)
        except serial.serialutil.SerialException:
            self.interface.mutex.release()
            self.__call_error_popup('Read process: can not access COM-port!')
        except ProtocolExchangeException as e:
            self.__call_error_popup(str(e))
        except Exception as e:
            self.__call_error_popup('Error occurred during data extraction!')
        self.update_device_status(status)
        self.is_reading_in_progress = False

    def program_data_to_device(self):
        if self.device_menu.tab_program.is_programming_blocked:
            mb.showerror(title='Error!', message='This is a single-use device! It cannot be reprogrammed!')
            return
        if self.is_reading_in_progress or self.is_programming_in_progress:
            return
        self.is_programming_in_progress = True
        # Check if time was synchronized successfully
        if not self.is_time_synchronised:
            answer = mb.askyesno(title='Warning!', message='Time cannot be synchronized over NTP server. '
                                                           'Local time will be used instead. Proceed?')
            if answer:
                self.synchronize_time(source='local')
                if not self.is_time_synchronised:
                    mb.showerror(title='Error!', message='Unable to synchronize time! Please try again')
                    self.is_programming_in_progress = False
                    return
            else:
                # User cancelled programming
                self.is_programming_in_progress = False
                return
        # Program new configuration into device
        status_code = False
        try:
            self.device_menu.tab_program.save_data_to_configuration(self.configuration)
            self.device_menu.tab_program.progressbar.start(50)
            status_code = self.interface.send_configuration(self.configuration)
        except serial.serialutil.SerialException:
            self.interface.mutex.release()
            self.__call_error_popup('Write process: can not access COM-port!')
        except Exception as e:
            self.__call_error_popup('Error occurred during device programming. Process interrupted')
        finally:
            self.device_menu.tab_program.progressbar.stop()
            self.device_menu.tab_program.progressbar['value'] = 100
        if status_code:
            mb.showinfo(title='Success!', message='New configuration was successfully programmed into device!')
        else:
            mb.showerror(title='Error!', message='Couldn\'t program new configuration!')
        self.is_programming_in_progress = False

    def update_device_status(self, status: str):
        try:
            if status.__eq__('updating'):
                self.thread_spinner = Thread(target=self.__start_spinner)
                self.thread_spinner.start()
            else:
                self.__stop_spinner()
                sleep(0.1)
                if status.__eq__('updated'):
                    if self.__are_log_data_good():
                        self.image_status.configure(image=self.image_status_ok)
                        self.image_status.image = self.image_status_ok
                        self.__set_hovertip(self.image_status, 'Collected recordings are good!')
                    else:
                        self.image_status.configure(image=self.image_status_error)
                        self.image_status.image = self.image_status_error
                        self.__set_hovertip(self.image_status, 'Collected recordings are not inside user thresholds!')
                    if not self.is_active:
                        self.button_make_active.set_state('ENABLED')
                elif status.__eq__('initial'):
                    self.image_status.configure(image=self.image_status_not_configured)
                    self.image_status.image = self.image_status_not_configured
                    self.__set_hovertip(self.image_status, 'Logger is not configured!')
                    if not self.is_active:
                        self.button_make_active.set_state('ENABLED')
                elif status.__eq__('connecting'):
                    self.image_status.configure(image=self.image_status_connecting)
                    self.image_status.image = self.image_status_connecting
                    self.__set_hovertip(self.image_status, 'Connecting...')
                    self.button_make_active.set_state('DISABLED')
                elif status.__eq__('no_connection'):
                    self.image_status.configure(image=self.image_status_no_connection)
                    self.image_status.image = self.image_status_no_connection
                    self.device_menu.ui_stop()
                    self.__set_hovertip(self.image_status, 'Unable to connect!')
                    self.canvas.itemconfigure(self.window_reconnect, state='normal')
                elif status.__eq__('not_started_yet'):
                    self.image_status.configure(image=self.image_status_not_started_yet)
                    self.image_status.image = self.image_status_not_started_yet
                    self.__set_hovertip(self.image_status, 'Logging was not started yet!')
                    if not self.is_active:
                        self.button_make_active.set_state('ENABLED')
                else:
                    raise ValueError('Unknown device status provided')
        except Exception as e:
            print(e)

    def synchronize_time(self, source='ntp'):
        for attempt in range(3):
            status = False
            if source == 'ntp':
                time = Timestamp2020.get_ntp_utc_time()
                if time is None:
                    continue
            else:
                time = Timestamp2020.get_local_utc_time()
            # Send current date-time to device
            try:
                status = self.interface.send_current_time(time)
            except serial.serialutil.SerialException:
                self.interface.mutex.release()
                self.__call_error_popup('Time sync process: can not access COM-port!')
            except Exception as e:
                self.__call_error_popup('Error occurred during time syncing!')
            if status:
                self.is_time_synchronised = True
                break

    def __reconnect(self):
        self.canvas.itemconfigure(self.window_reconnect, state='hidden')
        self.update_device_status('connecting')
        Thread(target=self.device_tree.connect_device, args=(self, )).start()

    def __ui_create(self):
        self.canvas = Canvas(self.parent, width=GUI_DEVICE_TREE_WIDTH - 2, height=56,
                             bg=MENU_BG_COLOR, cursor='arrow', highlightthickness=1, highlightbackground=GUI_FONT_COLOR)
        description_str = f'{self.device_port.description[:28]}...' if len(self.device_port.description) > 28 \
            else f'{self.device_port.description}'
        self.label_name = self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET, anchor=W, text=description_str,
                                                  font=f'{GUI_FONT_CONTENT} bold', justify=CENTER, fill=GUI_FONT_COLOR)
        self.canvas.create_text(AXIS_X_OFFSET, UI_Y_OFFSET + 20, anchor=W, text='S/N:',
                                font=f'{GUI_FONT_CONTENT} bold', justify=CENTER, fill=GUI_FONT_COLOR)
        self.label_serial_number = self.canvas.create_text(AXIS_X_OFFSET + 40, UI_Y_OFFSET + 20, anchor=W,
                                                           text=f'...',
                                                           font=f'{GUI_FONT_CONTENT} bold', justify=CENTER,
                                                           fill=GUI_FONT_COLOR)
        self.button_make_active = CustomImageButton(self.parent, width=30, height=30, bgcolor=MENU_BG_COLOR,
                                                    image_active=ICON_SWITCH_PROJECT_ACTIVE,
                                                    image_inactive=ICON_SWITCH_PROJECT_INACTIVE,
                                                    tip='Switch to this device',
                                                    command=self.make_active)
        self.button_make_active.set_state('DISABLED')
        window_make_active = self.canvas.create_window(GUI_DEVICE_TREE_WIDTH - 40, UI_Y_OFFSET + 10, anchor=W,
                                                       window=self.button_make_active)
        self.button_reconnect = CustomImageButton(self.parent, width=30, height=30, bgcolor=MENU_BG_COLOR,
                                                  image_active=ICON_RECONNECT,
                                                  image_inactive=ICON_RECONNECT,
                                                  tip='Reconnect device',
                                                  command=self.__reconnect)
        self.window_reconnect = self.canvas.create_window(GUI_DEVICE_TREE_WIDTH - 40, UI_Y_OFFSET + 10, anchor=W,
                                                          window=self.button_reconnect, state='hidden')
        self.image_status_ok = PhotoImage(file=ICON_STATUS_OK)
        self.image_status_error = PhotoImage(file=ICON_STATUS_ERROR)
        self.image_status_connecting = PhotoImage(file=ICON_STATUS_CONNECTING)
        self.image_status_no_connection = PhotoImage(file=ICON_STATUS_NO_CONNECTION)
        self.image_status_not_started_yet = PhotoImage(file=ICON_STATUS_NOT_STARTED_YET)
        self.image_status_not_configured = PhotoImage(file=ICON_NOT_CONFIGURED)
        self.image_status_loading = Image.open(ICON_STATUS_UPDATING)
        self.image_status = Label(self.canvas, image=self.image_status_connecting, background=MENU_BG_COLOR, width=30,
                                  height=30, bd=1, justify=CENTER, compound=CENTER)
        self.image_status.image = self.image_status_connecting
        window_image_status = self.canvas.create_window(GUI_DEVICE_TREE_WIDTH - 80, UI_Y_OFFSET + 10, anchor=W,
                                                        window=self.image_status)

    def __ui_start(self):
        self.canvas.pack(pady=2)

    def __ui_stop(self):
        self.canvas.pack_forget()

    def __read_usb_label(self):
        data = self.interface.get_usb_label()
        if data is None:
            raise ProtocolExchangeException('Error during USB volume label retrieving!')
        self.usb_label = data.decode('utf-8', 'ignore').strip('\x00')

    def __read_system_data_from_device(self):
        data = self.interface.get_system_data()
        if (data is None) or (len(data) < ctypes.sizeof(Structure_SystemData)):
            raise ProtocolExchangeException('Error during system data retrieving!')
        self.system_data = Structure_SystemData.from_buffer(bytearray(data))
        self.device_menu.tab_home.set_system_data(self.system_data)
        self.device_menu.tab_program.set_system_data(self.system_data)
        self.device_menu.tab_summary.set_system_data(self.system_data)

    def __read_metadata_from_device(self):
        if self.is_not_configured:
            return
        data = self.interface.get_metadata()
        if CODE_NACK == data:
            # Device is in IN_DELAY state, but it still may be reconfigured
            self.metadata = Structure_Metadata()
            self.metadata.records_count = 0
            self.device_menu.tab_home.set_default_metadata()
            self.device_menu.tab_summary.set_default_metadata()
        elif (data is None) or (len(data) < ctypes.sizeof(Structure_Metadata)):
            raise ProtocolExchangeException('Error during metadata retrieving!')
        else:
            self.metadata = Structure_Metadata.from_buffer(bytearray(data))
            # Adjusting timestamps relative to used time zone
            self.metadata.start_time += self.configuration.timezone
            self.metadata.stop_time += self.configuration.timezone
            # Filling UI with metadata
            self.device_menu.tab_home.set_metadata(self.metadata)
            self.device_menu.tab_program.set_metadata(self.metadata)
            self.device_menu.tab_summary.set_metadata(self.metadata)
        # If there are no collected recordings then 'Graph', 'Histogram' and 'Table' tabs
        # should be disabled
        if self.metadata.records_count.__eq__(0):
            self.device_menu.tab(2, state='disabled')
            self.device_menu.tab(3, state='disabled')
            self.device_menu.tab(4, state='disabled')

    def __read_configuration_from_device(self):
        data = self.interface.get_configuration()
        if CODE_NACK == data:
            # Device is in INITIAL state, so we have to abort further readings
            self.is_not_configured = True
            return
        if (data is None) or (len(data) < ctypes.sizeof(Structure_Configuration)):
            raise ProtocolExchangeException('Error during configuration retrieving!')
        self.configuration = Structure_Configuration.from_buffer(bytearray(data))
        # Adjusting timestamps relative to used time zone
        if self.configuration.auto_delay.__ne__(Structure_Configuration.TS_ILLEGAL_VALUE):
            self.configuration.auto_delay += self.configuration.timezone
        # Filling UI with configuration data
        self.device_menu.tab_home.set_configuration(self.configuration)
        self.device_menu.tab_program.set_configuration(self.configuration)
        self.device_menu.tab_graph.set_configuration(self.configuration)
        self.device_menu.tab_histogram.set_configuration(self.configuration)
        self.device_menu.tab_summary.set_configuration(self.configuration)
        self.device_menu.tab_table.set_configuration(self.configuration)

    def __read_recordings_from_device(self):
        if self.is_not_configured:
            return
        self.recordings.clear()
        records_number = self.metadata.records_count
        offset = 0
        max_chunk_size = 7
        while offset < records_number:
            chunk = None
            for attempt in range(5):
                chunk = self.interface.get_records_chunk(records_offset=offset)
                if chunk is not None:
                    break
                sleep(0.1)
            if chunk is None:
                raise ProtocolExchangeException(f'Error during records retrieving at {offset} offset!')
            records_list = [chunk[x:x + 8] for x in range(0, len(chunk), 8)]
            for rec in records_list:
                recording = Structure_Records.from_buffer(bytearray(rec))
                self.recordings.append(recording=recording,
                                       tz_offset=self.configuration.timezone,
                                       temp_unit=self.configuration.temp_unit)
            offset += max_chunk_size
        self.device_menu.tab_graph.set_recordings(self.recordings)
        self.device_menu.tab_histogram.set_recordings(self.recordings)
        self.device_menu.tab_table.set_recordings(self.recordings)

    def __set_initial_data(self):
        self.device_menu.tab_home.set_initial_data()
        self.device_menu.tab_program.set_initial_data()
        self.device_menu.tab_summary.set_initial_data()
        self.device_menu.tab(2, state='disabled')
        self.device_menu.tab(3, state='disabled')
        self.device_menu.tab(4, state='disabled')

    def __are_log_data_good(self) -> bool:
        is_success = True
        if self.metadata.records_count != 0:
            if self.configuration.hi_temp_thr.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
                if (self.configuration.hi_temp_thr / 10).__lt__(max(self.recordings.temperature)):
                    is_success = False
            if self.configuration.lo_temp_thr.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
                if (self.configuration.lo_temp_thr / 10).__gt__(min(self.recordings.temperature)):
                    is_success = False
            if self.configuration.hi_hum_thr.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
                if (self.configuration.hi_hum_thr / 10).__lt__(max(self.recordings.humidity)):
                    is_success = False
            if self.configuration.lo_hum_thr.__ne__(Structure_Configuration.THR_DISABLED_VALUE):
                if (self.configuration.lo_hum_thr / 10).__gt__(min(self.recordings.humidity)):
                    is_success = False
        return is_success

    def __update_device_serial(self):
        self.canvas.itemconfig(self.label_serial_number,
                               text=f'{Structure_Configuration.arr_to_string(self.system_data.serial)}')

    def __start_spinner(self):
        self.is_spinner_stopped = False
        angle = 0
        while not self.is_spinner_stopped:
            spinner = ImageTk.PhotoImage(self.image_status_loading.rotate(angle))
            self.image_status.configure(image=spinner)
            self.image_status.image = spinner
            angle -= 360 / 8
            angle %= 360
            sleep(0.1)

    def __stop_spinner(self):
        self.is_spinner_stopped = True

    def __create_popup(self):
        if self.is_popup_activated:
            popup = UI_PopUp(self.tkroot, self.popup_message)
            self.is_popup_activated = False
        self.parent.after(1000, self.__create_popup)

    def __call_error_popup(self, message):
        self.popup_message = message
        self.is_popup_activated = True

    def __set_hovertip(self, widget, tip):
        if self.ht is not None:
            self.ht.hidetip()
        self.ht = Hovertip(widget, tip)
