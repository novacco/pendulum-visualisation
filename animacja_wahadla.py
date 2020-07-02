import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import mpl_toolkits.axes_grid1
import matplotlib.widgets
import pandas as pd
import tkinter as tk

pd.set_option('display.max_rows', None)
which_angle = 'roll'


def load_data():
    data = pd.read_csv("outputPendulum02.log", delim_whitespace=True)
    data.columns = ["roll", "pitch", "yaw", "a_x", "a_y", "a_z", "m_x", "m_y", "m_z", "omega_x", "omega_y", "omega_z"]
    data = data.drop(columns=["a_x", "a_y", "a_z", "m_x", "m_y", "m_z", "omega_x", "omega_y", "omega_z"])
    data.index = [x for x in range(1, len(data.values) + 1)]
    data.index.name = 'id'
    df = pd.DataFrame(data)
    seconds = []
    x_cord = []
    y_cord = []
    for (index_label, row_series) in df.iterrows():
        second = index_label * 0.04
        seconds.append(second)
        radians = np.deg2rad(row_series[which_angle])
        x = 50 * np.sin(radians)
        y = 50 - 50 * np.cos(radians)
        x_cord.append(x)
        y_cord.append(y)
    df['seconds'] = seconds
    df['x_cord'] = x_cord
    df['y_cord'] = y_cord
    return df


def previous_move(df, angle):
    previous = []
    katy = df[angle]
    ile = df.index[-1]
    counter = 0
    move = 0
    to_samo = []
    for i in range(2, ile):
        if i == 0 or i == ile-1 or i == 1:
            previous.append(0)
        else:
            if katy[i] == katy[i+1]:
                to_samo.append(i)
            if katy[i - 1] < katy[i] and katy[i + 1] < katy[i]:
                move = counter
                move = round(move*0.04, 3)
                # print('wiersz: ', i, round(katy[i - 1], 2), round(katy[i], 2), round(katy[i + 1], 2),
                #       'WARUNEK SPELNIONY', 'czas: ', move)
                previous.append(move)
                counter = 0
            else:
                # print('wiersz: ', i,  round(katy[i-1], 2), round(katy[i], 2), round(katy[i+1], 2))
                previous.append(move)
                counter = counter + 1
    df['previous'] = pd.Series(previous)
    # print(to_samo)
    # print(df['previous'])
    return df


class Pendulum(FuncAnimation):
    def __init__(self, fig, func, frames=None, init_func=None, fargs=None,
                 save_count=None, mini=None, maxi=None, pos=(0.125, 0.95), **kwargs):
        self.min = mini
        self.i = self.min - 1
        self.max = maxi
        self.runs = True
        self.forwards = True
        self.fig = fig
        self.func = func
        self.setup(pos)
        FuncAnimation.__init__(self, self.fig, self.update, frames=self.play(),
                               init_func=init_func, fargs=fargs,
                               save_count=save_count, **kwargs)
        print(self.min, self.max)

    def play(self):
        while self.runs:
            print(self.i, self.i + self.forwards)
            self.i = self.i + self.forwards - (not self.forwards)
            if self.min <= self.i < self.max:
                print('I spelniony', ' czy dziala ', self.runs)
                yield self.i
            else:
                print('I nie spełniony')
                self.stop()
                yield self.i

    def start(self):
        self.runs = True
        self.event_source.start()

    def stop(self, event=None):
        self.runs = False
        self.event_source.stop()

    def forward(self, event=None):
        self.forwards = True
        self.start()

    def onestep(self, event=None):
        if self.min <= self.i < self.max:
            self.i = self.i + self.forwards - (not self.forwards)
            print('spełniony 1.')
        elif self.i == self.min and self.forwards:
            self.i += 1
            print('spełniony 2')
        elif self.i == self.max and not self.forwards:
            self.i -= 1
            print('spełniony 3')
        else:
            print('nic')
        self.func(self.i)
        self.slider.set_val(self.i*0.04)
        self.fig.canvas.draw_idle()

    def setup(self, pos):
        wahadloax = self.fig.add_axes([pos[0], pos[1], 0.64, 0.04])
        divider = mpl_toolkits.axes_grid1.make_axes_locatable(wahadloax)
        sax = divider.append_axes("right", size="80%", pad=0.05)
        fax = divider.append_axes("right", size="80%", pad=0.05)
        oax = divider.append_axes("right", size="80%", pad=0.05)
        sliderax = divider.append_axes("right", size="500%", pad=0.07)
        self.button_stop = matplotlib.widgets.Button(sax, label='$\u25A0$')
        self.button_forward = matplotlib.widgets.Button(fax, label='$\u25B6$')
        self.button_onestep = matplotlib.widgets.Button(oax, label='$\u25C6$')
        self.button_stop.on_clicked(self.stop)
        self.button_forward.on_clicked(self.forward)
        self.button_onestep.on_clicked(self.onestep)
        self.slider = matplotlib.widgets.Slider(sliderax, '', self.min*0.04, self.max*0.04, valinit=self.min*0.04)
        self.slider.on_changed(self.set_pos)

    def set_pos(self, i):
        self.i = int(self.slider.val/0.04)
        print("z setpos() i = ", self.i, type(self.i), "DOSTALO ", i)
        self.func(self.i)

    def update(self, i):
        self.slider.set_val(i*0.04)


class Window:
    def __init__(self, window):
        self.ltime = tk.Label(window)
        self.lycord = tk.Label(window)
        self.langle = tk.Label(window)
        self.lprison = tk.Label(window)
        self.ltime.pack(fill=tk.X)
        self.lycord.pack(fill=tk.X)
        self.langle.pack(fill=tk.X)
        self.lprison.pack(fill=tk.X)
        self.ltime.configure(text='Czas poprzedniego wahniecia: ')
        self.lycord.configure(text='Aktualna wysokość: ')
        self.langle.configure(text='Aktualny kat: ')
        self.lprison.configure(text='Podaj n próbe do odrzucenia: ')
        self.t = tk.IntVar()
        self.odkad_entry = tk.Entry(textvariable=self.t)
        self.odkad_entry.pack(fill=tk.X)
        self.activate = tk.Button(window, text="Pokaz wykres", command=self.activated)
        self.activate.pack(fill=tk.X)
        self.odkad = self.t.get()
        self.wiersz = self.odkad - 1

    def update_labels(self, df, row):
        self.wiersz = row
        self.ltime.configure(text='Czas poprzedniego wahniecia: {}s'.format(df['previous'].iloc[self.wiersz]))
        self.lycord.configure(text='Aktualna wysokość: {}'.format(round(df['y_cord'].iloc[self.wiersz], 2)))
        self.langle.configure(text='Aktualny kat: {}'.format(round(df['roll'].iloc[self.wiersz], 2)))
        print(self.wiersz, "z update_labels()")

    def activated(self):
        print("pokaz wykres")
        ani = Pendulum(fig, update, mini=self.t.get(), maxi=int(df['seconds'].max() / 0.04))
        self.odkad_entry.pack_forget()
        self.lprison.pack_forget()
        self.activate.pack_forget()
        master.geometry('300x60')
        # plt.autoscale(enable=True, axis='both')
        plt.show()


df = load_data()
df = previous_move(df, which_angle)

master = tk.Tk()
new = Window(master)
master.geometry('300x130')
master.title("Informacje szczegółowe")

fig, ax = plt.subplots()
fig.canvas.set_window_title('Wykres wahadła wg. {}'.format(which_angle))

X = df['x_cord']
Y = df['y_cord']
katy = df[which_angle]

ax.plot(X, Y)
point, = ax.plot([], [], marker="o", color="crimson", ms=7)


def update(i):
    print(i, "z update(i)")
    # print(new.wiersz, ' aktualny wiersz na oknie')
    point.set_data(X[i], Y[i])
    new.update_labels(df=df, row=i)


master.mainloop()
