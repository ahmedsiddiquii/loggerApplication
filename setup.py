import os
from cx_Freeze import setup, Executable

if 'nt' == os.name:
    base = "Win32GUI"
    packages = ["idna", "tkinter", "threading", "time", "serial.tools.list_ports", "matplotlib", "numpy", "tkcalendar",
                "ttkthemes", "tksheet", "configparser", "ntplib", "wmi", "tendo"]
else:
    base = None
    packages = ["idna", "tkinter", "threading", "time", "serial.tools.list_ports", "matplotlib", "numpy", "tkcalendar",
                "ttkthemes", "tksheet", "configparser", "ntplib", "tendo"]

executables = [Executable("malme.py", base=base, target_name='Logger', icon='icons/icon.ico')]

includes = ["icons/"]

excludes = ['PyQt5', 'PySide2', 'scipy']

options = {
    'build_exe': {
        'packages': packages,
        'include_files': includes,
        'include_msvcr': True,
        'excludes': excludes,
        'build_exe': 'build/Logger configurator',
    },
}

setup(
    name="Logger",
    options=options,
    version="8.11.21",
    executables=executables
)
