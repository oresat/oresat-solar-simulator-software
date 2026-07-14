# Solar Simulator CircuitPython Module

This module created in CircuitPython is used to interface with the hardware. It is designed to create custom scripts as easily and safely as possible without limiting control.

## Setup

Make sure the `solar_simulator.py` file (along with the Adafruit hardware modules) is in the `/lib` folder on the Pico and run the `pico-demos/sim_io_demo.py` file by copying its contents to the `code.py` file.

**TODO:** Integrate a system check button in the GUI settings menu.

## Usage

Using the module is as simple as import, create the simulator object, and the rest is up to you.

```py
# Import the Solar Simulator library
from lib import solar_simulator as ss

# Create the simulator
sim = ss.SolarSimulator()

# The rest of your code
while True:
    ...
```

## `ss` Module

The module itself contains a few helper functions that are used internally by the [`SolarSimulator()`](#sssolarsimulator-object) object and can also be used in your own scripts.

### `calcTemp(adc: float) -> float`

`calcTemp()` takes in a voltage value from the hardware's ADC and returns the temperature in Celsius. This is used internally by the [`SolarSimulator.checkThermals()`](#checkthermals---list) function to produce it's output.

It will also return `None` if there is 0v is used as an input. This is because if the thermistor on the solar cell plate is disconnected or not connected to the lid PCB properly, it might not read a voltage value and would otherwise error out due to a division by zero. So if you decide to use this function over `checkThermals()` and get `None` as a value, you can implement your own error handling.

#### Example code

```py
# Import dependencies
from lib import solar_simulator as ss

# Read a voltage value from a thermistor
voltage = 1.744

# Convert the voltage to a temperature value
temperature = ss.calcTemp(voltage)
print(f"{voltage}v -> {temperature:.2f}C")

>>> 1.744v -> 27.57C
```

## `ss.SolarSimulator()` Object

When this object is first instantiated, it will connect and setup all of the hardware for you (including I2C and PWM).

### `checkThermals() -> list`

`checkThermals()` returns a list of temperature values that are read from the hardware's thermistors in order of location. The returned list contains 3 temperatures in Celsius as a `float`. If you would like to learn how we converted these temperatures from analog voltage values, check out the `docs/thermistor.md` page.

Thermistor indicies:

- `checkThermals()[0]` - Thermistor located at the SMT LEDs under the lid PCB
- `checkThermals()[1]` - Thermistor attached to the heatsink on the top
- `checkThermals()[2]` - Thermistor located where the solar cell is placed in the chamber

> [!NOTE]
> There will be a feature in the future that will allow users to automatically disable the lights when the simulator gets too hot in certain places.

#### Example code

```py
# Import dependencies
from lib import solar_simulator as ss
import time

# Create the simulator
sim = ss.SolarSimulator()

# Read and print temperature values every second
while True:
    temps = sim.checkThermals()
    print('~'*21)
    for i, temp in zip(range(3), temps):
        print(f"Thermistor[{i}]: {temp:.2f}C")
    
    time.sleep(1)
```

#### Example output

```sh
~~~~~~~~~~~~~~~~~~~~~
Thermistor[0]: 82.93C
Thermistor[1]: 57.62C
Thermistor[2]: 64.11C
```

### `setLEDs(r: int, g: int, b: int, h: int)`

`setLEDs()` takes 5 optional arguments to set the brightness value of the lights. The input values are 16-bit unsigned integers and use a default value of 0, so if nothing is entered into any of the arguments, it will turn off that channel.

A quick way to turn off all the lights on the simulator is by executing `sim.setLEDS()`.

#### Example code

```py
# Import dependencies
from lib import solar_simulator as ss
import time

# Create the simulator
sim = ss.SolarSimulator(verbose=0)

while True:
    # set all of the lights to its max brightness
    sim.setLEDs(65535, 65535, 65535, 65535, 65535)
    time.sleep(1)

    # Turn all of the lights off
    sim.setLEDs(0, 0, 0, 0, 0)
    time.sleep(1)

    # Set all of the lights to half brightness
    sim.setLEDs(65535//2, 65535//2, 65535//2, 65535//2, 65535//2)
    time.sleep(1)

    # Turn all of the lights off (quick method)
    sim.setLEDs()
    time.sleep(1)
```
