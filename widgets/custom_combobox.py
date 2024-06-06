import tkinter as tk


class CustomCombobox(tk.Canvas):

    def __init__(self,
                 parent,
                 width,
                 height,
                 data=None,
                 maincolor='red',
                 bgcolor='green',
                 borderwidth=1,
                 cornerradius=5,
                 dropdownheight=5):
        if data is None:
            data = []
        self.parent = parent
        self.height = height
        self.width = width
        self.mainColor = maincolor
        self.bgColor = bgcolor
        self.focusedColor = '#3a75c4'
        self.borderwidth = borderwidth
        self.cornerRadius = cornerradius
        self.fontFamily = 'TimesNewRoman'
        self.dropdownHeight = dropdownheight
        self.listOfData = data
        tk.Canvas.__init__(self, self.parent,
                           borderwidth=0,
                           relief='flat',
                           highlightthickness=0,
                           width=self.width,
                           height=(self.height + 1),
                           bg=self.bgColor)
        self.config(cursor='hand2')
        self.dropdownFrame = None
        if len(self.listOfData).__eq__(0):
            self.chosenElementVariable = ''
        else:
            self.chosenElementVariable = self.listOfData[0]
        self._draw_current_selection()
        self.selected_item = self.create_text(5 + self.borderwidth, self.height / 2 - 2 + self.borderwidth / 2,
                                              anchor=tk.W,
                                              text=self.chosenElementVariable,
                                              font=(self.fontFamily, '12'),
                                              fill=self.mainColor)
        self.dropdownButtonExt = self.create_rectangle((self.width - 20), 0,
                                                       self.width, self.height + 1,
                                                       fill=maincolor,
                                                       activefill=maincolor,
                                                       outline='')
        self.labelSign = self.create_text(self.width - 11, self.height / 2,
                                          anchor=tk.CENTER,
                                          text='V',
                                          fill=self.bgColor,
                                          font=(self.fontFamily, '12', 'bold'))
        self.bind('<ButtonPress-1>', self._on_press)

    def set(self, text):
        self.itemconfig(self.selected_item, text=text)
        self.chosenElementVariable = str(text)

    def get(self):
        return self.chosenElementVariable

    def _on_press_dropdown(self, event):
        self.dropdownFrame.destroy()
        self.dropdownFrame = None

    def _on_press(self, event):
        if self.dropdownFrame.__ne__(None):
            self.dropdownFrame.destroy()
            self.dropdownFrame = None
            self.itemconfig(self.labelSign, text='V')
        else:
            if len(self.listOfData).__eq__(0):
                frame_height = self.height
            elif len(self.listOfData).__le__(self.dropdownHeight):
                frame_height = self.height * len(self.listOfData) + self.borderwidth * 2
            else:
                frame_height = self.height * self.dropdownHeight + self.borderwidth * 2
            self.dropdownFrame = tk.Frame(self.parent,
                                          width=self.width - self.cornerRadius,
                                          height=frame_height,
                                          highlightthickness=self.borderwidth,
                                          highlightbackground=self.mainColor)
            self.dropdownFrame.pack_propagate(False)
            self.itemconfig(self.labelSign, text='X')
            _canvas = tk.Canvas(self.dropdownFrame,
                                width=(self.width - 20 - self.cornerRadius - self.borderwidth),
                                borderwidth=0,
                                highlightthickness=0)
            _scrollbar = tk.Scrollbar(self.dropdownFrame,
                                      width=20,
                                      orient='vertical',
                                      command=_canvas.yview)
            _canvas.configure(yscrollcommand=_scrollbar.set)
            _scrollable_frame = tk.Frame(_canvas)
            _scrollable_frame.bind('<Configure>',
                                   lambda e: _canvas.configure(
                                       scrollregion=_canvas.bbox('all')
                                   )
                                   )
            for each in self.listOfData:
                _frame = tk.Frame(_scrollable_frame,
                                  width=(self.width - 20),
                                  height=self.height)
                _frame.pack_propagate(False)
                _label = tk.Label(_frame,
                                  text=each,
                                  width=(self.width + 1),
                                  font=(self.fontFamily, '12'),
                                  bg=self.bgColor,
                                  padx=3 + self.borderwidth,
                                  anchor=tk.W,
                                  fg=self.mainColor)
                _label.pack(fill='y', expand=True)

                def select_new_item(event):
                    self.chosenElementVariable = event.widget['text']
                    self.set(event.widget['text'])
                    self.dropdownFrame.destroy()
                    self.itemconfig(self.labelSign, text='V')
                    self.dropdownFrame = None

                def on_enter(event):
                    event.widget['bg'] = self.focusedColor
                    event.widget['fg'] = self.bgColor

                def on_leave(event):
                    event.widget['bg'] = self.bgColor
                    event.widget['fg'] = self.mainColor

                _label.bind('<Enter>', lambda e: on_enter(e))
                _label.bind('<Leave>', lambda e: on_leave(e))
                _label.bind('<ButtonPress-1>', lambda e: select_new_item(e))
                _frame.pack(side='top')
            _canvas.create_window(0, 0, anchor=tk.NW, window=_scrollable_frame)
            self._canvas_allow_scroll = False

            def _mousewheel_process(event):
                if self._canvas_allow_scroll.__eq__(True):
                    try:
                        _canvas.yview_scroll(int(-1 * (event.delta / 60)), 'units')
                    except tk.TclError:
                        pass

            def _allow_scroll(event):
                self._canvas_allow_scroll = True
                _canvas.bind_all('<MouseWheel>', _mousewheel_process)

            def _forbid_scroll(event):
                self._canvas_allow_scroll = False
                _canvas.unbind_all('<MouseWheel>')

            _canvas.bind('<Enter>', _allow_scroll)
            _canvas.bind('<Leave>', _forbid_scroll)
            _canvas.pack(side='left', fill='both', expand=True)
            _scrollbar.pack(side='right', fill='y')
            self.dropdownWindow = self.create_window(self.cornerRadius, self.height, anchor=tk.NW,
                                                     window=self.dropdownFrame)
            self.dropdownFrame.bind('<ButtonPress-1>', self._on_press_dropdown)
        pass

    def _draw_current_selection(self):
        rad = 2 * self.cornerRadius
        self.polygonExt = self.create_polygon(
            (0, self.height - self.cornerRadius),
            (0, self.cornerRadius),
            (self.cornerRadius, 0),
            (self.width - 20, 0),
            (self.width - 20, self.height),
            (self.cornerRadius, self.height),
            fill=self.mainColor, outline=self.mainColor)
        self.arcTopExt = self.create_arc((0, rad, rad, 0), start=90, extent=90, fill=self.mainColor,
                                         outline=self.mainColor)

        self.arcBotExt = self.create_arc((0, self.height - rad, rad, self.height), start=180, extent=90,
                                         fill=self.mainColor, outline=self.mainColor)
        self.polygonInn = self.create_polygon(
            (self.borderwidth, self.height - self.cornerRadius - self.borderwidth),
            (self.borderwidth, self.cornerRadius + self.borderwidth),
            (self.cornerRadius, 0 + self.borderwidth),
            (self.width - 20, self.borderwidth),
            (self.width - 20, self.height - self.borderwidth),
            (self.cornerRadius, self.height - self.borderwidth),
            fill=self.bgColor, outline=self.bgColor)
        self.arcTopInn = self.create_arc((self.borderwidth, rad,
                                          rad - self.borderwidth, self.borderwidth),
                                         start=90,
                                         extent=90,
                                         fill=self.bgColor,
                                         outline=self.bgColor)

        self.arcBotInn = self.create_arc((self.borderwidth, self.height - rad,
                                          rad - self.borderwidth, self.height - self.borderwidth),
                                         start=180,
                                         extent=90,
                                         fill=self.bgColor,
                                         outline=self.bgColor)

    def set_data(self, data_list):
        self.listOfData = data_list