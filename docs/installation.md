# Installation

On this page, you'll find step-by-step instructions to install everything to a working order.

## Hardware Requirements

- [Oresat Solar Simulator Hardware](https://github.com/oresat/oresat-solar-simulator-hardware) and Pico adapter board
- Raspberry Pi Pico (4$)
- 12v 10A power supply (get higher current supply if running multiple on the same supply)

## Control GUI (name WIP)

TODO: Add installation instructions

## Basilisk

**NOTE:** These instructions assumes you are using a Linux machine (ie. Debian, Ubuntu, etc.), if you are using Windows or MacOS, please refer to the provided installation docs from [Basilisk](https://hanspeterschaub.info/basilisk/Install.html). These should be referred to if something in this process goes wrong.

| Prerequisite | Version |
|:------------:|:-------:|
|    Python    |  >3.8.x |
|    CMake     |  >3.14  |
|    Swig      |  >3.14  |
|    GCC       |  >3.14  |

1. Clone the [Solar Simulator Software repository](https://github.com/oresat/oresat-solar-simulator-software)

```sh
git clone https://github.com/oresat/oresat-solar-simulator-software
```

2. Clone the [Basilisk repository](https://github.com/AVSLab/basilisk) into the SS Software repository

```sh
git clone https://github.com/AVSLab/basilisk
```

3. Open the `basilisk` folder in your terminal of choice, your local directory should look as follows: `/oresat-solar-simulator-software/basilisk`
4. Create a virtual environment with `python3 -m venv env` (`conda` may also work)
5. Activate the environment with `source ./env/bin/activate`
6. Install Conan with `pip3 install wheel 'conan<2.0'`
7. Compile and install Basilisk with `python3 conanfile.py` (this may take a while depending on your hardware)
8. Once Basilisk is done compiling, verify it installed correctly by running `python3 examples/scenarioBasicOrbit.py`
9. If this script runs successfully, congratulations!

## Pico Firmware

These instructions will describe how to install, flash, and update the Pico's firmware as well as properly loading the Solar Simulator Software.

**NOTE:** Updating the firmware with a new version of CircuitPython will ERASE ALL OF ITS CONTENTS, so backup your stuff before loading new firmware

1. Clone the [Solar Simulator Software repository](https://github.com/oresat/oresat-solar-simulator-software) (if you have not followed the Basilisk installation steps)

```sh
git clone https://github.com/oresat/oresat-solar-simulator-software
```

2. Download the [CircuitPython UF2](https://circuitpython.org/board/raspberry_pi_pico/) firmware file for the Pico
3. While holding the `BOOTSEl` button, plug in the Pico to the host machine
4. Release the button and a file window should pop up with a drive labeled `RPI-RP2`
5. Copy the downloaded firmware file to this folder and the Pico should automatically update itself to the latest version of CircuitPython
   1. To ensure the new version is loaded, replug the Pico into the host machine
   2. Open the `CIRCUITPY` drive in your file manager
   3. Open the `boot_out.txt` file in the root directory; this should read as the latest version of CircuitPython
6. Once the new firmware is flashed, copy everything in the `oresat-solar-simulator-software/pico` folder into the root `CIRCUITPY` drive
