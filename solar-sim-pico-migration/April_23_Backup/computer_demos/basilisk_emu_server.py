# Basilisk emulator server code
# Import dependencies
from tkinter import *
import serial as s

# Device settings
DEVICE_PORT = '/dev/ttyACM0'
BAUDRATE = 115200

# Create the Tkinter GUI object
root = Tk()
# root.geometry("264x148")

# Integer value buffer
red_val = IntVar(value = 0)
grn_val = IntVar(value = 0)
blu_val = IntVar(value = 0)
uv_val  = IntVar(value = 0)
hal_val = IntVar(value = 0)
# limiter = IntVar(value = 100)

# Send serial data to Pico
# TODO: Refactor to make any amount of sense
def sendData():
	sel = f"R={str(red_val.get())},G={str(grn_val.get())},B={str(blu_val.get())},UV={str(uv_val.get())},H={str(hal_val.get())}"
	l1.config(text = sel, font =("Consolas", 14), pady=10)

	# Send data to Pico
	with s.Serial(DEVICE_PORT, BAUDRATE, timeout=1) as serial:
		send = f"r:{red_val.get()},g:{grn_val.get()},b:{blu_val.get()},u:{uv_val.get()},h:{hal_val.get()}"
		send += '\r'
		serial.write(send.encode())

# TODO: From this line down needs to be refactored to make much more sense

# Slider widgets
sliders = Frame(root)

red_slider = Scale(sliders, variable = red_val, from_ = 0, to = 100, orient = HORIZONTAL, background = 'red')
grn_slider = Scale(sliders, variable = grn_val, from_ = 0, to = 100, orient = HORIZONTAL, background = 'green')
blu_slider = Scale(sliders, variable = blu_val, from_ = 0, to = 100, orient = HORIZONTAL, background = 'blue')
uv_slider  = Scale(sliders, variable = uv_val,  from_ = 0, to = 100, orient = HORIZONTAL, background = 'purple')
hal_slider = Scale(sliders, variable = hal_val, from_ = 0, to = 100, orient = HORIZONTAL, background = 'yellow')

# Label widget
l3 = Label(root, text = "Set channel intensity", pady=5)

# Button widget
b1 = Button(root, text ="Send to Pico", command = sendData, bg = "yellow")

# Root label?
l1 = Label(root)

red_slider.pack(anchor = CENTER)
grn_slider.pack(anchor = CENTER)
blu_slider.pack(anchor = CENTER)
uv_slider .pack(anchor = CENTER)
hal_slider.pack(anchor = CENTER)

sliders.pack()
l3.pack()
b1.pack(anchor = CENTER)
l1.pack()

root.mainloop()
