import tkinter as tk
from tkinter import CENTER


class CustomButton(tk.Canvas):
    shape = None

    def __init__(self, parent, width, height, text, border_color, bgcolor, text_color, corner_radius=5, padding=0,
                 font_size=12, focused_color='#3a75c4', disabled_color='#979aaa', command=None, args=(), **kw):
        super().__init__(parent, borderwidth=0, highlightthickness=0, relief='flat', bg=bgcolor, cursor='hand2', **kw)
        self.border_color = border_color
        self.focused_color = focused_color
        self.disabled_color = disabled_color
        self.state = 'ENABLED'
        self.command = command
        self.args = args
        self.font_size = font_size
        if corner_radius > 0.5 * width:
            raise ValueError('Error: corner radius must be half the width or less!')
        if corner_radius > 0.5 * height:
            raise ValueError('Error: corner radius must be half the height or less!')
        rad = 2 * corner_radius
        # Drawing the button
        self.polygon = self.create_polygon(
            (padding, height - corner_radius - padding, padding, corner_radius + padding,
             padding + corner_radius, padding, width - padding - corner_radius, padding,
             width - padding, corner_radius + padding, width - padding,
             height - corner_radius - padding, width - padding - corner_radius, height - padding,
             padding + corner_radius, height - padding), fill=self.border_color, outline=self.border_color)
        self.arc1 = self.create_arc((padding, padding + rad, padding + rad, padding), start=90, extent=90,
                                    fill=self.border_color, outline=self.border_color)
        self.arc2 = self.create_arc((width - padding - rad, padding, width - padding, padding + rad), start=0,
                                    extent=90, fill=self.border_color, outline=self.border_color)
        self.arc3 = self.create_arc((width - padding, height - rad - padding, width - padding - rad, height - padding),
                                    start=270, extent=90, fill=self.border_color, outline=self.border_color)
        self.arc4 = self.create_arc((padding, height - padding - rad, padding + rad, height - padding), start=180,
                                    extent=90, fill=self.border_color, outline=self.border_color)
        # Getting the actual size of button
        (x0, y0, x1, y1) = self.bbox('all')
        width = (x1 - x0)
        height = (y1 - y0)

        def on_press(event):
            if self.state.__eq__('ENABLED'):
                self.configure(relief='sunken')
                self.itemconfig(self.label, font=('TimesNewRoman', f'{self.font_size - 1}', 'bold'))
            elif self.state.__eq__('DISABLED'):
                pass

        def on_release(event):
            if self.state.__eq__('ENABLED'):
                self.configure(relief='raised')
                self.itemconfig(self.label, font=('TimesNewRoman', f'{self.font_size}', 'bold'))
                if self.command is not None:
                    self.command(*self.args)
            elif self.state.__eq__('DISABLED'):
                pass

        def on_mouse_over(event):
            if self.state.__eq__('ENABLED'):
                self.itemconfig(self.polygon, fill=self.focused_color, outline=self.focused_color)
                self.itemconfig(self.arc1, fill=self.focused_color, outline=self.focused_color)
                self.itemconfig(self.arc2, fill=self.focused_color, outline=self.focused_color)
                self.itemconfig(self.arc3, fill=self.focused_color, outline=self.focused_color)
                self.itemconfig(self.arc4, fill=self.focused_color, outline=self.focused_color)
            elif self.state.__eq__('DISABLED'):
                pass

        def on_mouse_away(event):
            if self.state.__eq__('ENABLED'):
                self.itemconfig(self.polygon, fill=self.border_color, outline=self.border_color)
                self.itemconfig(self.arc1, fill=self.border_color, outline=self.border_color)
                self.itemconfig(self.arc2, fill=self.border_color, outline=self.border_color)
                self.itemconfig(self.arc3, fill=self.border_color, outline=self.border_color)
                self.itemconfig(self.arc4, fill=self.border_color, outline=self.border_color)
            elif self.state.__eq__('DISABLED'):
                pass

        self.configure(width=width, height=height)
        self.bind('<ButtonPress-1>', on_press)
        self.bind('<ButtonRelease-1>', on_release)
        self.bind('<Enter>', on_mouse_over)
        self.bind('<Leave>', on_mouse_away)
        # Setting the label
        self.label = self.create_text(width / 2 - 3, height / 2 - 2, anchor=CENTER, text=text,
                                      font=('TimesNewRoman', f'{self.font_size}', 'bold'), fill=text_color)

    def set_state(self, new_state):
        if new_state.__eq__('DISABLED'):
            self.state = 'DISABLED'
            self.itemconfig(self.polygon, fill=self.disabled_color, outline=self.disabled_color)
            self.itemconfig(self.arc1, fill=self.disabled_color, outline=self.disabled_color)
            self.itemconfig(self.arc2, fill=self.disabled_color, outline=self.disabled_color)
            self.itemconfig(self.arc3, fill=self.disabled_color, outline=self.disabled_color)
            self.itemconfig(self.arc4, fill=self.disabled_color, outline=self.disabled_color)
        elif new_state.__eq__('ENABLED'):
            self.state = 'ENABLED'
            self.itemconfig(self.polygon, fill=self.border_color, outline=self.border_color)
            self.itemconfig(self.arc1, fill=self.border_color, outline=self.border_color)
            self.itemconfig(self.arc2, fill=self.border_color, outline=self.border_color)
            self.itemconfig(self.arc3, fill=self.border_color, outline=self.border_color)
            self.itemconfig(self.arc4, fill=self.border_color, outline=self.border_color)

    def bind_command(self, command, args=()):
        self.command = command
        self.args = args
