from tkinter import *
from tkinter import ttk
from ui.constants import *
from ui.hint_no_devices import UI_HintNoDevices
from ui.device import UI_Device
from ui.device_menu import UI_DeviceMenu
from settings import Settings
from threading import Thread
from time import sleep
import gc


class UI_DeviceTree:
    connected_ports: list = []
    connected_devices: list = []

    def __init__(self, main_window):
        self.main_window = main_window
        self.active_device = None
        self.general_settings = Settings()
        # Creating device tree title
        frame_tree_title = Frame(self.main_window, width=GUI_DEVICE_TREE_WIDTH + GUI_DEVICE_TREE_SCROLLBAR_WIDTH + 4,
                                 height=GUI_DEVICE_TREE_TITLE_HEIGHT, bg=GUI_BG_COLOR)
        label_tree_title = Label(frame_tree_title, text="Connected devices", font=GUI_FONT_TITLES,
                                 foreground=GUI_FONT_COLOR, bg=GUI_BG_COLOR)
        label_tree_title.place(x=GUI_DEVICE_TREE_WIDTH / 2, y=GUI_DEVICE_TREE_TITLE_HEIGHT / 2, anchor=CENTER)
        frame_tree_title.pack(anchor=NW)
        # Creating scrollable device tree on the left side of window
        canvas_tree = Canvas(self.main_window, width=GUI_DEVICE_TREE_WIDTH, height=GUI_HEIGHT,
                             bg=GUI_BG_COLOR, cursor='arrow')
        scrollbar = Scrollbar(self.main_window, width=GUI_DEVICE_TREE_SCROLLBAR_WIDTH, orient='vertical',
                              command=canvas_tree.yview)
        canvas_tree.configure(yscrollcommand=scrollbar.set)
        self.frame_tree = Frame(canvas_tree, width=GUI_DEVICE_TREE_WIDTH,
                                height=GUI_HEIGHT - GUI_DEVICE_TREE_TITLE_HEIGHT, bg=GUI_BG_COLOR)
        self.frame_tree.bind('<Configure>',
                             lambda e: canvas_tree.configure(
                                 scrollregion=canvas_tree.bbox('all')
                             )
                             )
        canvas_tree.create_window(0, 0, anchor=NW, window=self.frame_tree)
        canvas_tree.pack(side='left')
        scrollbar.pack(side='left', fill='y')
        # Creating empty device menu on the right side of window
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=GUI_FONT_MENU, foreground=GUI_FONT_COLOR)
        style.configure('TFrame', background=GUI_BG_COLOR)
        self.frame_device_menu = Frame(self.main_window, width=GUI_DEVICE_SETTINGS_WIDTH,
                                       height=GUI_HEIGHT + GUI_DEVICE_TREE_TITLE_HEIGHT + 4, bg=GUI_BG_COLOR)
        empty_notebook = ttk.Notebook(self.frame_device_menu, width=GUI_DEVICE_SETTINGS_WIDTH)
        empty_notebook.add(ttk.Frame(empty_notebook), text='Home', state='disabled')
        empty_notebook.add(ttk.Frame(empty_notebook), text='Program', state='disabled')
        empty_notebook.add(ttk.Frame(empty_notebook), text='Graph', state='disabled')
        empty_notebook.add(ttk.Frame(empty_notebook), text='Histogram', state='disabled')
        empty_notebook.add(ttk.Frame(empty_notebook), text='Table', state='disabled')
        empty_notebook.add(ttk.Frame(empty_notebook), text='Summary', state='disabled')
        empty_notebook.place(x=0, y=0, anchor=NW)
        self.frame_device_menu.place(x=GUI_DEVICE_TREE_WIDTH + GUI_DEVICE_TREE_SCROLLBAR_WIDTH + 6,
                                     y=GUI_TOOLBAR_HEIGHT + 4)
        # Adding no-devices hint
        self.hint = UI_HintNoDevices(self.frame_tree)

    def add_device(self, device_port):
        self.clear_hint()
        # Create new device submenu in device tree
        ui_device = UI_Device(self, device_port)
        ui_device.device_menu = UI_DeviceMenu(self.frame_device_menu, ui_device)
        self.connected_devices.append(ui_device)
        self.connected_ports.append(device_port)
        # Connecting to device
        Thread(target=self.connect_device, args=(ui_device, )).start()

    def remove_device_by_port(self, device_port):
        self.connected_ports.remove(device_port)
        for device in self.connected_devices:
            if device.device_port.__eq__(device_port):
                self.connected_devices.remove(device)
                device.delete()
                del device
                break
        gc.collect(1)

    def get_active_device(self):
        active_device = None
        for device in self.connected_devices:
            if device.is_active:
                active_device = device
                break
        return active_device

    def get_connected_devices(self):
        return self.connected_devices

    def get_connected_ports(self):
        return self.connected_ports

    def add_hint(self):
        self.hint.start()

    def clear_hint(self):
        self.hint.stop()

    def connect_device(self, ui_device):
        is_connected = False
        sleep(2)
        ui_device.update_device_status('connecting')
        for attempt in range(5):
            print(f'Attempt to connect: {attempt}')
            is_connected = ui_device.connect()
            if is_connected:
                break
            sleep(0.5)
        if not is_connected:
            ui_device.update_device_status('no_connection')
            return
        ui_device.is_connected = True
        if len(self.connected_devices) == 1:
            # If there is only 1 device connected then we should automatically switch to its menu
            ui_device.make_active()
        # Calibrate RTC module of the device
        Thread(target=ui_device.synchronize_time).start()
        # Automatically collect data from device (if this option enabled)
        self.general_settings.update()
        if self.general_settings.auto_download:
            Thread(target=ui_device.read_data_from_device).start()
