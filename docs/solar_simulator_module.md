# Solar Simulator CircuitPython Module

The Solar Simulator module is used to interface with the hardware. It is designed to create custom scripts as easily and safely as possible without limiting control.

## Usage

Using the module is as simple as import, create the simulator object, and the rest is up to you.

```py
from lib import solar_simulator as ss

sim = ss.SolarSimulator()

# Your main loop
while True:
    ...
```

### `ss.SolarSimulator()` Object

When this object is first instantiated, it will connect and setup all of the hardware for you (including I2C and PWM).

### `check_thermals() -> list`

`check_thermals()` returns a list of temperature values that are read from the hardware's thermistors in order of location. If you would like to learn how we converted these temperatures from analog voltage values, check out the [thermistor documentation](thermistor.md).

#### Minimal `check_thermals()` Example

```py
from lib import solar_simulator as ss
import time

# Create the simulator instance
sim = ss.SolarSimulator()

# Read and print temperature values every second
while True:
    temps = sim.check_thermals()
    print('~' * 21)
    for i, temp in zip(range(3), temps):
        print(f"Thermistor[{i}]: {temp:.2f}C")

    time.sleep(1)
```

The output will look something like this:

```sh
~~~~~~~~~~~~~~~~~~~~~
Thermistor[0]: 82.93C
Thermistor[1]: 57.62C
Thermistor[2]: 64.11C
```

### `set_leds(r: int, g: int, b: int, h: int)`

`set_leds()` takes 4 optional arguments to set the brightness value of the lights. The input values are 16-bit unsigned integers and use a default value of 0, so if nothing is entered into any of the arguments, it will turn off that channel.

> [!TIP]
> A quick way to turn off all the lights on the simulator is to execute `sim.set_leds()`.

#### Minimal `set_leds()` Example

```py
from lib import solar_simulator as ss
import time

# Create the simulator instance
sim = ss.SolarSimulator()

while True:
    # set all of the lights to its max brightness
    sim.set_leds(65535, 65535, 65535, 65535)
    time.sleep(1)

    # Turn all of the lights off
    sim.set_leds(0, 0, 0, 0)
    time.sleep(1)

    # Set all of the lights to half brightness
    sim.set_leds(65535 // 2, 65535 // 2, 65535 // 2, 65535 // 2)
    time.sleep(1)

    # Turn all of the lights off (quick method)
    sim.set_leds()
    time.sleep(1)
```
