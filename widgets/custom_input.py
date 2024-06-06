import tkinter as tk
import tkinter.ttk as ttk
from idlelib.tooltip import Hovertip


class CustomInput(ttk.Entry):

    def __init__(self, parent, min=None, max=None, tip=None, command=None, validator='none', args=(), **kw):
        self.max = max
        self.min = min
        self.variable = tk.StringVar()
        self.validator = validator
        supported_validators = {
            'none': lambda *_args: None,
            'float': self.__validator_float,
            'integer': self.__validator_int,
            'unsigned': self.__validator_uint
        }
        validator_func = parent.register(supported_validators.get(self.validator, None))
        super().__init__(parent, textvariable=self.variable,
                         validate="all", validatecommand=(validator_func, '%P', '%S'), **kw)
        self.variable.trace('w', self.__onchange)
        self.command = command
        self.args = args
        if tip is not None:
            Hovertip(self, tip)
        self.bind('<FocusOut>', self.__focus_out, '+')

    def get(self) -> str:
        return self.variable.get()

    def set(self, text: str):
        self.variable.set(text)

    def set_state(self, state: bool):
        self.config(state='normal' if state else 'disabled')

    def set_max(self, new_max: int):
        self.max = new_max

    def set_min(self, new_min: int):
        self.min = new_min

    def __focus_out(self, event):
        if not self.variable.get():
            if self.min is None:
                self.variable.set(0)
            else:
                self.variable.set(0 if self.min < 0 else self.min)
        else:
            if self.max is not None and float(self.variable.get()) > self.max:
                self.variable.set(self.max)
            elif self.min is not None and float(self.variable.get()) < self.min:
                self.variable.set(self.min)

    @staticmethod
    def __validator_float(user_input, new_value):
        try:
            if len(user_input) >= 1 and user_input != '-' and user_input is not None:
                _user_input = float(user_input)
        except ValueError:
            return False
        return True

    @staticmethod
    def __validator_int(user_input, new_value):
        try:
            if len(user_input) >= 1 and user_input != '-' and user_input is not None:
                _user_input = int(user_input)
        except ValueError:
            return False
        return True

    @staticmethod
    def __validator_uint(user_input, new_value):
        if new_value == '-':
            return False
        try:
            if len(user_input) >= 1 and user_input is not None:
                _user_input = int(user_input)
        except ValueError:
            return False
        return True

    def __onchange(self, *args):
        if self.command is not None:
            self.command(*self.args)