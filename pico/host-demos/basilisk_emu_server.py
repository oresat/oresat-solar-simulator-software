# GUI program
# TODO: Add pyserial integration

# Import dependencies
from tkinter import *
import serial as ser 

# Create led value buffer
p_led = {
    'r': 0,
    'g': 0,
    'b': 0,
    'u': 0,
    'h': 0,
}

# Create the Tkinter GUI object
root = Tk()
root.geometry = ("700x700")
root.resizable(height = FALSE, width = FALSE)

#Slider changed event
def slider_changed(value, text) -> None:
    text.delete("1.0", END)
    text.insert(END, value)
    updatePico()

#Text changed event
def text_changed(text, slider) -> None:
    try:
        value = int(text.get("1.0", END).strip())
        slider.set(value)
    except:
        pass
    finally:
        text.delete("1.0", END)
        updatePico()
    
def updatePico() -> None:
    # Get the LED buffer from the global scope
    global p_led

    # Set temporary vars
    changed = False
    r = red_val.get()
    g = grn_val.get()
    b = blu_val.get()
    u =  uv_val.get()
    h = hal_val.get()

    # Check if any values have changed
    if p_led['r'] != r:
        p_led['r'] = r
        changed = True
    if p_led['g'] != g:
        p_led['g'] = g
        changed = True
    if p_led['b'] != b:
        p_led['b'] = b
        changed = True
    if p_led['u'] != u:
        p_led['u'] = u
        changed = True
    if p_led['h'] != h:
        p_led['h'] = h
        changed = True

    if changed: print(f"Sending: r={r}, g={g}, b={b}, u={u}, h={h}")

# Integer value buffer
red_val = IntVar(value = 0)
grn_val = IntVar(value = 0)
blu_val = IntVar(value = 0)
uv_val  = IntVar(value = 0)
hal_val = IntVar(value = 0)
# limiter = IntVar(value = 100)

#Title
root.title("Light Intensity Test GUI")
title_label = Label(root, text = "Light Intensity Test GUI", pady=5)
title_label.config(font = 26)

# Slider widgets
sliders = Frame(root)
red_slider = Scale(sliders, variable = red_val, from_ = 0, to = 100, orient = HORIZONTAL, background = 'red')
grn_slider = Scale(sliders, variable = grn_val, from_ = 0, to = 100, orient = HORIZONTAL, background = 'green')
blu_slider = Scale(sliders, variable = blu_val, from_ = 0, to = 100, orient = HORIZONTAL, background = 'blue')
uv_slider  = Scale(sliders, variable = uv_val,  from_ = 0, to = 100, orient = HORIZONTAL, background = 'purple')
hal_slider = Scale(sliders, variable = hal_val, from_ = 0, to = 100, orient = HORIZONTAL, background = 'yellow')

# Slider text
red_inputtxt = Text(sliders, height = 1, width = 3)
grn_inputtxt = Text(sliders, height = 1, width = 3)
blu_inputtxt = Text(sliders, height = 1, width = 3)
uv_inputtxt  = Text(sliders, height = 1, width = 3)
hal_inputtxt = Text(sliders, height = 1, width = 3)

# Label widget
l3 = Label(root, text = "Set channel intensity", pady=5)

# Button widget
b1 = Button(root, text = "Send to Pico", bg = "yellow", command=updatePico)

# Root label?s
l1 = Label(root)

# Widget location in a grid
title_label.pack(anchor = CENTER)
red_slider.grid(column = 0, row = 0)
grn_slider.grid(column = 0, row = 1)
blu_slider.grid(column = 0, row = 2)
grn_slider.grid(column = 0, row = 3)
uv_slider.grid( column = 0, row = 4)
hal_slider.grid(column = 0, row = 5)

red_inputtxt.grid(column = 1, row = 0)
grn_inputtxt.grid(column = 1, row = 1)
blu_inputtxt.grid(column = 1, row = 2)
grn_inputtxt.grid(column = 1, row = 3)
uv_inputtxt.grid( column = 1, row = 4)
hal_inputtxt.grid(column = 1, row = 5)

sliders.pack()
l3.pack()
b1.pack(anchor = CENTER)
l1.pack()

#Bind Slider to Text
red_slider.bind("<Motion>", lambda event: slider_changed(red_slider.get(), red_inputtxt))
grn_slider.bind("<Motion>", lambda event: slider_changed(grn_slider.get(), grn_inputtxt))
blu_slider.bind("<Motion>", lambda event: slider_changed(blu_slider.get(), blu_inputtxt))
uv_slider.bind( "<Motion>", lambda event: slider_changed( uv_slider.get(),  uv_inputtxt))
hal_slider.bind("<Motion>", lambda event: slider_changed(hal_slider.get(), hal_inputtxt))

#Bind Text to Slider
red_inputtxt.bind("<Return>", lambda event: text_changed(red_inputtxt, red_slider))
grn_inputtxt.bind("<Return>", lambda event: text_changed(grn_inputtxt, grn_slider))
blu_inputtxt.bind("<Return>", lambda event: text_changed(blu_inputtxt, blu_slider))
uv_inputtxt.bind( "<Return>", lambda event: text_changed( uv_inputtxt,  uv_slider))
hal_inputtxt.bind("<Return>", lambda event: text_changed(hal_inputtxt, hal_slider))

root.mainloop()