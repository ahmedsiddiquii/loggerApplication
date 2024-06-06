import tkinter as tk
import tkinter.ttk as ttk
import re


class CustomTimeEntry(tk.Canvas):

    def __init__(self, parent, font, bgcolor='white', hours_limit=23, days_limit=999, days_enabled=False,
                 secs_enabled=False, **kw):
        super().__init__(parent, bg=bgcolor, borderwidth=0, highlightthickness=0, **kw)
        self.days_enabled = days_enabled
        self.secs_enabled = secs_enabled
        self.days = tk.StringVar()
        self.hours = tk.StringVar()
        self.minutes = tk.StringVar()
        self.seconds = tk.StringVar()
        self.days.set('0')
        self.hours.set('0')
        self.minutes.set('0')
        self.seconds.set('0')
        self.command = lambda: None
        self.spinner_days = ttk.Spinbox(self, from_=0, to=days_limit, wrap=True, textvariable=self.days, width=4,
                                        justify=tk.CENTER, font=font, format='%1.0f')
        self.spinner_hours = ttk.Spinbox(self, from_=0, to=hours_limit, wrap=True, textvariable=self.hours, width=4,
                                         justify=tk.CENTER, font=font, format='%01.0f')
        self.spinner_minutes = ttk.Spinbox(self, from_=0, to=59, wrap=True, textvariable=self.minutes, width=4,
                                           justify=tk.CENTER, font=font, format='%01.0f')
        self.spinner_seconds = ttk.Spinbox(self, from_=0, to=59, wrap=True, textvariable=self.seconds, width=4,
                                           justify=tk.CENTER, font=font, format='%01.0f')
        label_d = ttk.Label(self, font=font, width=2, text='d', background=bgcolor)
        label_h = ttk.Label(self, font=font, width=2, text='h', background=bgcolor)
        label_m = ttk.Label(self, font=font, width=2, text='m', background=bgcolor)
        label_s = ttk.Label(self, font=font, width=2, text='s', background=bgcolor)
        # Setting validator
        validator = self.register(self.__validator)
        self.spinner_days.config(validate="all", validatecommand=(validator, '%P', '%S', '%W'))
        self.spinner_hours.config(validate="all", validatecommand=(validator, '%P', '%S', '%W'))
        self.spinner_minutes.config(validate="all", validatecommand=(validator, '%P', '%S', '%W'))
        self.spinner_seconds.config(validate="all", validatecommand=(validator, '%P', '%S', '%W'))
        # Packing widget
        if self.days_enabled:
            self.spinner_days.pack(side=tk.LEFT)
            label_d.pack(side=tk.LEFT)
        self.spinner_hours.pack(side=tk.LEFT)
        label_h.pack(side=tk.LEFT)
        self.spinner_minutes.pack(side=tk.LEFT)
        label_m.pack(side=tk.LEFT)
        if self.secs_enabled:
            self.spinner_seconds.pack(side=tk.LEFT)
            label_s.pack(side=tk.LEFT)
        # Call callback on value change
        self.days.trace('w', lambda a, b, c: self.command())
        self.hours.trace('w', lambda a, b, c: self.command())
        self.minutes.trace('w', lambda a, b, c: self.command())
        self.seconds.trace('w', lambda a, b, c: self.command())

    def __validator(self, user_input, new_value, widget_name):
        if new_value == '':
            return False
        if new_value.isdigit():
            min_val = int(self.nametowidget(widget_name).config('from')[4])
            max_val = int(self.nametowidget(widget_name).config('to')[4])
            try:
                _user_input = int(user_input)
            except ValueError:
                return True
            if _user_input in range(min_val, max_val + 1):
                return True
        return False

    def set(self, time_in_secs: int):
        days = 0
        if self.days_enabled:
            days = time_in_secs / 86400
            time_in_secs %= 86400
        hours = time_in_secs / 3600
        time_in_secs %= 3600
        minutes = time_in_secs / 60
        time_in_secs %= 60
        seconds = time_in_secs
        self.set_time(hours, minutes, seconds, days)

    def get(self) -> int:
        seconds = int(self.days.get()) * 86400 + \
                  int(self.hours.get()) * 3600 + \
                  int(self.minutes.get()) * 60 + \
                  int(self.seconds.get())
        return seconds

    def set_time(self, hours, minutes, seconds=0, days=0):
        self.days.set(str(int(days)))
        self.hours.set(str(int(hours)))
        self.minutes.set(str(int(minutes)))
        self.seconds.set(str(int(seconds)))

    def get_time(self):
        return self.days.get(), self.hours.get(), self.minutes.get(), self.seconds.get()

    def on_change(self, command):
        self.command = command

    def state(self, state: str):
        if state in ['disabled', 'active']:
            self.spinner_days.config(increment=0 if state.__eq__('disabled') else 1, state=state)
            self.spinner_hours.config(increment=0 if state.__eq__('disabled') else 1, state=state)
            self.spinner_minutes.config(increment=0 if state.__eq__('disabled') else 1, state=state)
            self.spinner_seconds.config(increment=0 if state.__eq__('disabled') else 1, state=state)
