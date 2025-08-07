# BBQ mode with thermal safety
# Import dependencies
from lib import solar_simulator as ss
from ulab import numpy as np
from time import sleep, monotonic_ns
import supervisor as sup

sup.runtime.autoreload = False

# Set up constants
SERIAL_LOG = True
THERM_LOG = True
THERM_SAFE_EN = True # TODO: Enable/disable flag for thermal protection

# Create the simulator
sim = ss.SolarSimulator()

# Calculate LED interpolated brightness steps
steps = ss.calcSteps()

# Sine wave vars
level = 0
intensity = 0
wave = np.sin(np.linspace(0, np.pi, 360))

# STATE MACHINE ITEMS
NS_OFFSET = monotonic_ns()
def getCurrentTime() -> int:
    return int((monotonic_ns()-NS_OFFSET)/1000000)

# Thermal check timing
THRM_CHECK      = 50  # Elapsed time before checking thermals
THRM_LEDS_SHTDN = 100 # In Celsius, thermistor temperature shutoff value at RGB LEDs (under PCB)
THRM_HTSK_SHTDN = 60  # In Celsius, thermistor temperature shutoff value at heatsinks
THRM_CELL_SHTDN = 80  # In Celsius, thermistor temperature shutoff value at solar cell (bottom plate)
THRM_RSM        = 45  # In Celsius, all thermistors must be at or below this value before lights are enabled again
therm_timer     = 0
lights_en       = True
lights_upd      = True

# Reset any active lights
sim.setLEDs()

while True:
    # Calculate a 0-100 value from the wave
    intensity = int(100*wave[level])

    # Gets LED brightness values at the appropriate level
    red = steps[0][intensity]
    grn = steps[1][intensity]
    blu = steps[2][intensity]
    hal = steps[3][intensity]
    
    # Check if the elapsed time is longer than the thermal check interval
    c_time = getCurrentTime()
    if (c_time - therm_timer > THRM_CHECK) and THERM_SAFE_EN:
        channels = sim.checkThermals()
        try:
            if (channels[0] > THRM_LEDS_SHTDN) \
            or (channels[1] > THRM_HTSK_SHTDN) \
            or (channels[2] > THRM_CELL_SHTDN):
                lights_en = False
                sim.setLEDs()
        except TypeError:
            print("Unable to read thermistor value")
        
        # Set cold to False if any of the thermistors are above their respective thresholds
        # Or set cold to True if all of the thermistors are below the resume temperature threshold
        cold = True
        for i in range(len(channels)):
            if i > 2: continue
            
            temp_c = channels[i]
            try:
                cold = cold if temp_c < THRM_RSM else False
                if not sim.verbose and THERM_LOG: print(f"CH{i}: {temp_c:0.2f}C")
            except TypeError:
                print(f"Unable to read thermistor channel {i}")

        # Disable lights if hot
        if not lights_en and cold: lights_en = True
        therm_timer = getCurrentTime()
    
    if lights_en: sim.setLEDs(red, grn, blu, hal)

    if not sim.verbose and lights_en and SERIAL_LOG: print(f"Intensity: {intensity}, Level: {level}")

    # Increment and overflow the level every iteration
    if lights_en: level += 1
    if level > len(wave)-1: level = 0
    sleep(0.05)
