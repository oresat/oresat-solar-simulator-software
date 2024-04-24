from tkinter import *
import serial as s
import time

DEVICE_PORT = '/dev/ttyACM0'
BAUDRATE = 115200

root = Tk()
root.geometry("264x148")

v1 = IntVar()

def show1():
	sel = f"Solar Intensity = {str(v1.get())}"
	l1.config(text = sel, font =("Consolas", 14), pady=10)

	with s.Serial(DEVICE_PORT, BAUDRATE, timeout=1) as serial:
		send = str(v1.get())
		send += '\r'
		serial.write(send.encode())


s1 = Scale(root, variable = v1,
		from_ = 0, to = 100,
		orient = HORIZONTAL,)

l3 = Label(root, text = "Set intensity", pady=5)

b1 = Button(root, text ="Send to Pico",
			command = show1,
			bg = "yellow")

l1 = Label(root)

s1.pack(anchor = CENTER)
l3.pack()
b1.pack(anchor = CENTER)
l1.pack()

root.mainloop()
