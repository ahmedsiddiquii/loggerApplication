import gc

MAX_ZOOM_Y_RANGE = 0.01
MIN_ZOOM_Y_RANGE = 220

class ZoomPan:

    def __init__(self, ax_temp, ax_hum):
        self.press = None
        self.x0 = None
        self.y0 = None
        self.xpress = None
        self.ypress = None

        self.ax_temp = ax_temp
        self.ax_hum = ax_hum
        self.active_ax = None
        # Parameters
        self.cur_xlim_t = None
        self.cur_ylim_t = None
        self.cur_xlim_h = None
        self.cur_ylim_h = None
        self.press_t = None
        self.press_h = None
        # Bindings
        self.press_cid = None
        self.motion_cid = None
        self.release_cid = None
        self.zoom_cid = None
        # Getting the figure of given axes. In this project both the axes are belonged to one figure
        self.figure = self.ax_temp.get_figure()

    def start_zoom_factory(self, base_scale=2.0):

        def __zoom(event):
            self.cur_xlim_t = self.ax_temp.get_xlim()
            self.cur_ylim_t = self.ax_temp.get_ylim()
            self.cur_xlim_h = self.ax_hum.get_xlim()
            self.cur_ylim_h = self.ax_hum.get_ylim()
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            if event.inaxes == self.ax_temp:
                main_ax = self.ax_temp
                sub_ax = self.ax_hum
                xlim_main = self.cur_xlim_t
                ylim_main = self.cur_ylim_t
                ylim_sub = self.cur_ylim_h
            else:
                main_ax = self.ax_hum
                sub_ax = self.ax_temp
                xlim_main = self.cur_xlim_h
                ylim_main = self.cur_ylim_h
                ylim_sub = self.cur_ylim_t
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)
            try:
                ratio = (ydata - ylim_main[0]) / (ylim_main[1] - ylim_main[0])
                ydata_sub = ratio * (ylim_sub[1] - ylim_sub[0]) + ylim_sub[0]
                new_width = (xlim_main[1] - xlim_main[0]) * scale_factor
                new_height = (ylim_main[1] - ylim_main[0]) * scale_factor
                new_height_sub = (ylim_sub[1] - ylim_sub[0]) * scale_factor
                relx = (xlim_main[1] - xdata) / (xlim_main[1] - xlim_main[0])
                rely = (ylim_main[1] - ydata) / (ylim_main[1] - ylim_main[0])
                rely_sub = (ylim_sub[1] - ydata_sub) / (ylim_sub[1] - ylim_sub[0])
                if new_height_sub > MIN_ZOOM_Y_RANGE or new_height_sub < MAX_ZOOM_Y_RANGE:
                    del main_ax, sub_ax
                    del xdata, ydata, ydata_sub
                    del xlim_main, ylim_main, ylim_sub
                    gc.collect(1)
                    return
                main_ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
                main_ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
                sub_ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
                sub_ax.set_ylim([ydata_sub - new_height_sub * (1 - rely_sub), ydata_sub + new_height_sub * rely_sub])
                self.figure.canvas.draw()
                del ydata_sub
            except TypeError:
                pass
            except ValueError:
                print('Limit reached!')
            except Exception as e:
                print(e)
            del main_ax, sub_ax
            del xdata, ydata
            del xlim_main, ylim_main, ylim_sub
            gc.collect(1)

        self.zoom_cid = self.figure.canvas.mpl_connect('scroll_event', __zoom)

    def start_pan_factory(self):

        def __on_press(event):
            if event.inaxes != self.ax_temp and event.inaxes != self.ax_hum:
                return
            self.active_ax = event.inaxes
            self.cur_xlim_t = self.ax_temp.get_xlim()
            self.cur_ylim_t = self.ax_temp.get_ylim()
            self.cur_xlim_h = self.ax_hum.get_xlim()
            self.cur_ylim_h = self.ax_hum.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def __on_release(event):
            self.press = None
            self.active_ax = None
            try:
                self.figure.canvas.draw()
            except ValueError:
                print('Limit reached!')
            except Exception as e:
                print(e)

        def __on_motion(event):
            if self.press is None:
                return
            if event.inaxes != self.ax_temp and event.inaxes != self.ax_hum:
                return
            if event.inaxes != self.active_ax:
                # Protection from cross-subplot motion
                return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim_t -= dx
            self.cur_xlim_h -= dx
            if event.inaxes == self.ax_temp:
                self.cur_ylim_t -= dy
            else:
                self.cur_ylim_h -= dy
            self.ax_temp.set_xlim(self.cur_xlim_t)
            self.ax_temp.set_ylim(self.cur_ylim_t)
            self.ax_hum.set_xlim(self.cur_xlim_h)
            self.ax_hum.set_ylim(self.cur_ylim_h)
            try:
                self.figure.canvas.draw()
            except ValueError:
                print('Limit reached!')
                self.cur_xlim_t += dx
                self.cur_xlim_h += dx
                if event.inaxes == self.ax_temp:
                    self.cur_ylim_t += dy
                else:
                    self.cur_ylim_h += dy
                self.ax_temp.set_xlim(self.cur_xlim_t)
                self.ax_temp.set_ylim(self.cur_ylim_t)
                self.ax_hum.set_xlim(self.cur_xlim_h)
                self.ax_hum.set_ylim(self.cur_ylim_h)
            except Exception as e:
                print(e)
            del dx, dy
            gc.collect(1)

        self.press_cid = self.figure.canvas.mpl_connect('button_press_event', __on_press)
        self.release_cid = self.figure.canvas.mpl_connect('button_release_event', __on_release)
        self.motion_cid = self.figure.canvas.mpl_connect('motion_notify_event', __on_motion)

    def destroy(self):
        self.figure.canvas.mpl_disconnect(self.press_cid)
        self.figure.canvas.mpl_disconnect(self.motion_cid)
        self.figure.canvas.mpl_disconnect(self.release_cid)
        self.figure.canvas.mpl_disconnect(self.zoom_cid)
        del self.press_cid
        del self.motion_cid
        del self.release_cid
        del self.zoom_cid
        del self.figure
        del self.ax_temp
        del self.ax_hum
        del self.active_ax
        gc.collect(1)
