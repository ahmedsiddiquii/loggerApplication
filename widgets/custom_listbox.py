import tkinter as tk


class CustomListbox(tk.Canvas):
    ITEM_HEIGHT = 30

    def __init__(self, parent, width, height, data=(), border_width=3, corner_radius=10,
                 border_color='red', bgcolor='green', text_color=None, focused_color='#3a75c4',
                 hide_scrollbar=False):
        self.parent = parent
        self.width = width
        self.height = height
        self.border_width = border_width
        self.border_color = border_color
        self.bgcolor = bgcolor
        if text_color is None:
            self.text_color = self.border_color
        else:
            self.text_color = text_color
        self.focused_color = focused_color
        self.data_list = data
        self.hide_scrollbar = hide_scrollbar
        self.font_family = 'TimesNewRoman'
        self.selected_item = ''
        self.selected_label = None
        # self.config(cursor='hand2')
        tk.Canvas.__init__(self, parent,
                           borderwidth=0,
                           relief='flat',
                           highlightthickness=0,
                           bg=self.bgcolor,
                           width=self.width,
                           height=self.height)
        self.main_frame = tk.Frame(self,
                                   width=self.width,
                                   height=self.height,
                                   highlightthickness=self.border_width,
                                   highlightbackground=self.border_color,
                                   bg=self.bgcolor)
        self.main_frame.pack_propagate(False)
        if self.hide_scrollbar.__eq__(False):
            _scrollbar_offset = 20
        else:
            _scrollbar_offset = 0
        _canvas = tk.Canvas(self.main_frame,
                            width=(self.width - _scrollbar_offset - self.border_width),
                            borderwidth=0,
                            highlightthickness=0,
                            bg=self.bgcolor)
        _scrollbar = tk.Scrollbar(self.main_frame,
                                  width=20,
                                  orient='vertical',
                                  command=_canvas.yview)
        _canvas.configure(yscrollcommand=_scrollbar.set)
        self.scrollable_frame = tk.Frame(_canvas)
        self.scrollable_frame.bind('<Configure>',
                                   lambda e: _canvas.configure(
                                       scrollregion=_canvas.bbox('all')
                                   )
                                   )
        for each in self.data_list:
            self.add_item(each)
        _canvas.create_window(0, 0, anchor=tk.NW, window=self.scrollable_frame)
        self._canvas_allow_scroll = False

        def _mousewheel_process(event):
            if self._canvas_allow_scroll.__eq__(True) and (len(self.data_list) > (self.height / self.__class__.ITEM_HEIGHT)):
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
        self.create_window(0, 0, anchor=tk.NW, window=self.main_frame, tags='window')
        self.arcTopExt = self.create_arc((0, corner_radius * 2,
                                          corner_radius * 2, 0),
                                         start=90, extent=90,
                                         fill='red',
                                         outline='red', tags='arc')
        self.tag_lower('arc')
        self.tag_lower('window')

    # Adds new item to the bottom of the listbox
    def add_item(self, item):
        _frame = tk.Frame(self.scrollable_frame,
                          width=self.width,
                          height=self.__class__.ITEM_HEIGHT)
        _frame.pack_propagate(False)
        _label = tk.Label(_frame,
                          text=item,
                          width=self.width,
                          font=(self.font_family, '12'),
                          bg=self.bgcolor,
                          padx=self.border_width,
                          anchor=tk.W,
                          fg=self.text_color)
        _label.pack(fill='y', expand=True)

        def select_new_item(event):
            if event.widget['bg'].__ne__(self.border_color):
                self.selected_item = event.widget['text']
                event.widget['bg'] = self.border_color
                event.widget['fg'] = self.bgcolor
                # If we there is already exist selected label then we have to 'deselect' it
                if self.selected_label.__ne__(None):
                    self.selected_label['bg'] = self.bgcolor
                    self.selected_label['fg'] = self.border_color
                self.selected_label = event.widget
            else:
                event.widget['bg'] = self.focused_color
                event.widget['fg'] = self.bgcolor
                self.selected_label = None

        def on_enter(event):
            if event.widget['bg'].__ne__(self.border_color):
                event.widget['bg'] = self.focused_color
                event.widget['fg'] = self.bgcolor

        def on_leave(event):
            if event.widget['bg'].__ne__(self.border_color):
                event.widget['bg'] = self.bgcolor
                event.widget['fg'] = self.border_color

        _label.bind('<Enter>', lambda e: on_enter(e))
        _label.bind('<Leave>', lambda e: on_leave(e))
        _label.bind('<ButtonPress-1>', lambda e: select_new_item(e))
        _frame.pack(side='top')

    # Returns selected item
    def get_item(self):
        return self.selected_item

    # Selects new item. If there are duplicate items then it selects the first one
    def set_item(self, item):
        if item in self.data_list:
            self.selected_item = item
            for each_widget in self.scrollable_frame.winfo_children():
                label = each_widget.winfo_children()[0]
                if label['text'].__eq__(item):
                    if label['bg'].__ne__(self.border_color):
                        label['bg'] = self.border_color
                        label['fg'] = self.bgcolor
                        # If we there is already exist selected label then we have to 'deselect' it
                        if self.selected_label.__ne__(None):
                            self.selected_label['bg'] = self.bgcolor
                            self.selected_label['fg'] = self.border_color
                        self.selected_label = label
                    else:
                        label['bg'] = self.focused_color
                        label['fg'] = self.bgcolor
                        self.selected_label = None
                    break
        else:
            raise ValueError('There is no such item in the listbox!')