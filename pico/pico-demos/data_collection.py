# Manual data collection code
# THE COMBINATION FOR RGBUH IF THE WARNING DOESN'T MEAN ANYTHING
# R:10, G:75, B:25, UV:25, H:72 .. while the spectrometer is at 30nm measurements

# Import dependencies
from lib import solar_simulator as ss
from time import sleep, monotonic_ns
import digitalio as dio
import board

# Serial console logging settings
SERIAL_LOG = False
PORT_SCAN  = False
PRETTY     = True

# Set the debug LED
led = dio.DigitalInOut(board.LED)
led.direction = dio.Direction.OUTPUT
led.value = True

# Create the solar simulator
sim = ss.SolarSimulator()

# Calculate steps
steps = ss.calcSteps()

# Data collection message prompt
command_prompt = """Select a channel: [red, grn, blu, hal]
Give an integer value: 0-100
Multiple channels can be set by using comma separation
Use 'clear' or 'reset' to reset all brightness values
Example inputs: (g:50), (r:100, b:32), etc."""

# Valid string inputs from the terminal
valid_inputs = [ 'r', 'red', 'g', 'grn', 'green', 'b', 'blu', 'blue', 'h', 'hal', 'halogen' ]

# LED channel value buffer
led_buf = {
    'r': 0,
    'g': 0,
    'b': 0,
    'u': 0,
    'h': 0,
}

# Reset any active lights
sim.setLEDs()
led.value = False

while True:
    #if supervisor.runtime.serial_bytes_available:
    if PRETTY:
        print(f"======= Current values - R={led_buf['r']}, G={led_buf['g']}, B={led_buf['b']}, H={led_buf['h']} =======")
        print(command_prompt)
        print('-' * 60)

        # Get the data from the serial connection
        data = input("Enter a command: ")
    else:
        data = input().strip()
    # Format input string and split between every comma
    data = data.replace(' ', '').lower().split(',')

    # Get data from each input
    # TODO: Turn into `parseInput()` function that returns the changed values
    for item in data:
        item = item.split(':')
        if len(item) > 1:
            item[1] = int(item[1])
            if item[0] in valid_inputs and item[1] <= 100 and item[1] >= 0:
                led_buf[item[0][0]] = item[1]

    # Keywords to clear LED buffer
    if 'reset' in data or 'clear' in data:
        led_buf['r'] = 0
        led_buf['g'] = 0
        led_buf['b'] = 0
        led_buf['u'] = 0
        led_buf['h'] = 0

    calc_start = monotonic_ns()
    #steps = sim.calc_steps(LIMITER) # 1ms slower lol

    # Gets LED brightness values at the appropriate level
    red = steps[0][led_buf['r']]
    grn = steps[1][led_buf['g']]
    blu = steps[2][led_buf['b']]
    uv  = steps[3][led_buf['u']]
    hal = steps[4][led_buf['h']]

    calc_end = monotonic_ns()

    if SERIAL_LOG: print(f"red:{red},grn:{grn},blu:{blu},hal:{hal},lim:{LIMITER},calc_time:{(calc_end-calc_start)/1000:0.3f}us")

    # Set the LEDs and bulb
    sim.setLEDs(red,grn,blu,hal)

    if PRETTY: print()
    sleep(0.01)
