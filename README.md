## Requirements

- Windows
- Python 3.8


### Windows

Install Python 3.8 or higher from an official website - https://www.python.org/downloads/   
Open your terminal, mode to the folder with the project. 
Install all required dependencies using 'reuirements.txt' file using two commands below.
Given commands are example for Python 3.8, if you are using newer version of Python, for example Python 3.11, then change argument '-3.8' on '-3.11'.

```sh
py -3.8 -m pip install cx_freeze
py -3.8 -m pip install -r requirements.txt
```

To build executable application use command below in project folder.
Given commands are example for Python 3.8, if you are using newer version of Python, for example Python 3.11, then change argument '-3.8' on '-3.11'.

```sh
py -3.8 setup.py build
```

To build setup file from executable application you may use Inno Setup software (https://jrsoftware.org/isdl.php).
Script file, necessarry for building setup file, is included into this repository - "logger_setup.iss".
Just open Inno Setup software, open above mentioned script file and press "Compile" button. The result setup file is located in "SetupFile" folder inside project's directory.



C:\Users\Carlo\AppData\Local\Programs\Python\Python311\python.exe setup.py build
python.exe setup.py build