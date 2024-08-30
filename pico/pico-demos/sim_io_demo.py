# Simulator IO demo
# Import dependencies
from lib.solar_simulator import SolarSimulator
from time import sleep

# Set up constants
MAX_VALUE = 65535
SPEED = 1

# Create the Solar Simulator object
sim = SolarSimulator(verbose=0)
sim.uv_safety = True # Set this to False if you want to use the UV LEDs

# Reset any active lights
sim.setLEDs()

while True:
    print("Setting red")
    sim.setLEDs(r=MAX_VALUE//2)
    sleep(SPEED)

    print("Setting green")
    sim.setLEDs(g=MAX_VALUE//2)
    sleep(SPEED)

    print("Setting blue")
    sim.setLEDs(b=MAX_VALUE//2)
    sleep(SPEED)

    print("Setting uv")
    sim.setLEDs(uv=MAX_VALUE//2)
    sleep(SPEED)

    print("Setting halogen")
    sim.setLEDs(hal=MAX_VALUE//4)
    sleep(SPEED)

    print("Clearing lights")
    sim.setLEDs()
    sleep(SPEED)

    print("Reading thermal data")
    thermals = sim.checkThermals()
    if not sim.verbose:
        for therm, i in zip(thermals, range(3)): print(f"Channel[{i}]: {therm}C")
    sleep(SPEED); print()
