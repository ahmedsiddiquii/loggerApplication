import tkinter as tk
import tkinter.ttk as ttk
from idlelib.tooltip import Hovertip


class CustomCheckboxBool(ttk.Checkbutton):

    def __init__(self, parent, tip=None, **kw):
        self.variable = tk.BooleanVar()
        super().__init__(parent, variable=self.variable, onvalue=True, offvalue=False, takefocus=False, **kw)
        if tip is not None:
            Hovertip(self, tip)

    def get(self) -> bool:
        return self.variable.get()

    def set(self, state: bool):
        self.variable.set(state)
