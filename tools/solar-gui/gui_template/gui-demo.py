#   Basilisk Emulator GUI testing verison 1.0
#   Written by Daniel Monahan (dmonahan@pdx.edu)
#
#   The basilisk emulator will become a GUI interface that allows the solar simulator team to test
#   input and output parameters for the solar simulator hardware. The hardware runs off of a RP2042 Pico
#   and controls three LED bulbs (red, blue, green) and one halogen bulb with the goal of producing a 
#   programmable class A solar simulator.
#

from tkinter import *
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

root = Tk()
root.title("BSK Emulator")
dpi = root.winfo_fpixels('1i')
root.tk.call('tk', 'scaling', '-displayof', '.' , dpi / 72.0)

# include 3rd party theme, awdark
cwdir = Path.cwd()
awpath = str(cwdir) + '/style/awthemes-10.4.0'

root.tk.call('lappend', 'auto_path', awpath)
root.tk.call('package', 'require', 'awdark')

# use awdark
s = ttk.Style()
s.theme_use('awdark')

# This progam will demonstrate some of the functionalities to be included in the BSK emulator.
# We produce a sine wave array using numpy and apply tkinter sliders to control some basic parameters of the
# function, and plot the results via matplotlib. We also create GUI interfaces for basic mode controls and Pico
# serial controls.

def sine_print(*args): # demo for plotting configurable output
    print("Generating Plot...") # FIXME : use tkinter label
    t = np.linspace(t_min.get(), t_max.get(), t_step.get())
    f = np.sin(t)
    plt.plot(t, f, 'ro--')
    plt.title('Sine wave')
    plt.xlabel('time')
    plt.ylabel('magnitude')
    plt.show()

# sliders will need command functions that update their label values
def update_min(*args):
    t_min_label['text'] = str(t_min.get())

def update_max(*args):
    t_max_label['text'] = str(t_max.get())

def update_step(*args):
    t_step_label['text'] = str(t_step.get())

mainframe = ttk.Frame(root, padding=(30, 30, 10, 10))
mainframe.grid(column=0, row=0)

# slider parameters (scales)
t_min = IntVar(value=0)
t_max = IntVar(value=10)
t_step = IntVar(value=50)

# create scale objects, we use command=<label updater> to automatically update the scale values shown
t_min_scale = ttk.Scale(mainframe, orient=HORIZONTAL, variable=t_min, length=100, from_=0, to=10, command=update_min)
t_min_scale.grid(column=0, row=1, sticky='sw')
t_min_label = ttk.Label(mainframe, text='init1')
t_min_label.grid(column=1, row=1, sticky='se')

t_max_scale = ttk.Scale(mainframe, orient=HORIZONTAL, variable=t_max, length=100, from_=0, to=10, command=update_max)
t_max_scale.grid(column=0, row=2, sticky='sw')
t_max_label = ttk.Label(mainframe, text='init2')
t_max_label.grid(column=1, row=2, sticky='se')

t_step_scale = ttk.Scale(mainframe, orient=HORIZONTAL, variable=t_step, length=100, from_=1, to=100, command=update_step)
t_step_scale.grid(column=0, row=3, sticky='sw')
t_step_label = ttk.Label(mainframe, text='init3')
t_step_label.grid(column=1, row=3, sticky='se')

# generate button, calls plot function
btn = ttk.Button(mainframe, text='Generate', command=sine_print)
btn.grid(column=2)

# combo box is used to select the output mode
modevar = StringVar()
mode = ttk.Combobox(mainframe, textvariable=modevar)
mode.grid(column=3, row=0)
mode.state(["readonly"])
mode['values'] = ('BBQ Mode', 'Duty Cycle') # append new modes to this tuple

# connection label for the pico is currently controlled by the 'pico_connect' button
def pico_connected(*args):
    if (pico_connect_var.get()) :
        pico_connected_msg.set('Pico is Connected')
    else :
        pico_connected_msg.set('Pico is Disconnected')
def pico_toggle(*args) :
    pico_connect_var.set( not pico_connect_var.get())

pico_connect_var = BooleanVar(value=False)
pico_connected_msg = StringVar()

pico_connect = ttk.Button(mainframe, text='Connect Pico', command=pico_toggle)
pico_connect.bind('<1>', lambda e: pico_connected.configure(text='Pico is Connected'))
pico_connect.grid(column=0, row=4, sticky='sw')

pico_connected = ttk.Label(mainframe, text='Pico is Disconnected')
pico_connected.grid(column=3, row=4, sticky='se')

# begin main loop and open up GUI
root.mainloop()
