# Basilisk emulator server code
# Import dependencies
from tkinter import *
import serial as s

# Device settings
DEVICE_PORT = '/dev/ttyACM0'
BAUDRATE = 115200

# Create the Tkinter GUI object
root = Tk()
root.geometry("264x148")

# Integer value buffer
v1 = IntVar()

# Send serial data to Pico
# TODO: Refactor to make any amount of sense
def show1():
	sel = f"Solar Intensity = {str(v1.get())}"
	l1.config(text = sel, font =("Consolas", 14), pady=10)

	# Send data to Pico
	with s.Serial(DEVICE_PORT, BAUDRATE, timeout=1) as serial:
		send = str(v1.get())
		send += '\r'
		serial.write(send.encode())

# TODO: From this line down needs to be refactored to make much more sense

# Slider widget
s1 = Scale(root, variable = v1,
		from_ = 0, to = 100,
		orient = HORIZONTAL,)

# Label widget
l3 = Label(root, text = "Set intensity", pady=5)

# Button widget
b1 = Button(root, text ="Send to Pico",
			command = show1,
			bg = "yellow")

# Root label?
l1 = Label(root)

s1.pack(anchor = CENTER)
l3.pack()
b1.pack(anchor = CENTER)
l1.pack()

root.mainloop()
