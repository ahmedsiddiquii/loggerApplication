import wmi
import os
import shutil
import gc
from tkinter.filedialog import asksaveasfile
from typing import Optional


class Reports:

    def __init__(self, usb_label: str):
        self.wmic = wmi.WMI()
        self.pdf_file = None
        self.txt_file = None
        self.csv_file = None
        self.usb_label = usb_label

    def __get_usb_path(self) -> Optional[str]:
        disks = self.wmic.Win32_LogicalDisk()
        path = None
        for disk in disks:
            if disk.volumeName == self.usb_label:
                path = disk.Name + '/'
                break
        del disks
        return path

    def __get_pdf_path(self) -> Optional[str]:
        usb_path = self.__get_usb_path()
        path = None
        if usb_path is None:
            return None
        files = os.listdir(usb_path)
        for file in files:
            if file.split('.')[-1].lower() == 'pdf':
                self.pdf_file = file
                path = os.path.join(usb_path, file)
                break
        del files, usb_path
        return path

    def __get_txt_path(self) -> Optional[str]:
        usb_path = self.__get_usb_path()
        path = None
        if usb_path is None:
            return None
        files = os.listdir(usb_path)
        for file in files:
            if file.split('.')[-1].lower() == 'txt':
                self.txt_file = file
                path = os.path.join(usb_path, file)
                break
        del files, usb_path
        return path

    def __get_csv_path(self) -> Optional[str]:
        usb_path = self.__get_usb_path()
        path = None
        if usb_path is None:
            return None
        files = os.listdir(usb_path)
        for file in files:
            if file.split('.')[-1].lower() == 'csv':
                self.csv_file = file
                path = os.path.join(usb_path, file)
                break
        del files, usb_path
        return path

    def save_pdf_report(self):
        path = self.__get_pdf_path()
        if path is None:
            raise OSError
        save_path = asksaveasfile(initialfile=self.pdf_file, defaultextension='.pdf',
                                  filetypes=[('pdf', '*.pdf'), ], mode='w')
        if save_path is not None:
            shutil.copy2(path, save_path.name)
            save_path.close()
        del save_path
        del path
        gc.collect(1)

    def save_txt_report(self):
        path = self.__get_txt_path()
        if path is None:
            raise OSError
        save_path = asksaveasfile(initialfile=self.txt_file, defaultextension='.txt',
                                  filetypes=[('txt', '*.txt'), ], mode='w')
        if save_path is not None:
            shutil.copy2(path, save_path.name)
            save_path.close()
        del save_path
        del path
        gc.collect(1)

    def save_csv_report(self):
        path = self.__get_csv_path()
        if path is None:
            raise OSError
        save_path = asksaveasfile(initialfile=self.csv_file, defaultextension='.csv',
                                  filetypes=[('csv', '*.csv'), ], mode='w')
        if save_path is not None:
            shutil.copy2(path, save_path.name)
            save_path.close()
        del save_path
        del path
        gc.collect(1)
    
    def upload_pdf_report(self):
        path = self.__get_pdf_path()
        if path is None:
            raise OSError
        
        return path, self.usb_label

    def clean(self):
        del self.usb_label
        del self.csv_file
        del self.txt_file
        del self.pdf_file
        del self.wmic
        gc.collect(1)
