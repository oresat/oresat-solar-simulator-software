# oresat-solar-simulator-software

The software repository for our solar simulator for testing 1U solar panels [Hardware Repo](https://github.com/oresat/oresat-solar-simulator-hardware).

## General Information

The OreSat Solar Simulator is a benchtop simulator for hardware-in-the-loop testing of CubeSat solar modules. It uses LED and halogen light bulbs to emit light that simulates the sun's solar spectrum in low Earth orbit (Air Mass 0 or 'AM0').

The original work for this was done as an MCECS Capstone Project from January to June of 2023 by Bendjy Faurestal, Adam Martinez, Cesar Ordaz-Coronel, and Charles Nasser. Andrew Greenberg was both representing PSAS as the Industry Sponsor and the Faculty Advisor to the students.

In February 2024 to March 2024, work to convert the OreSat Solar Simulator Software from using the Beaglebone microcontroller to the Raspberry Pi Pico was completed by Oresat engineers Jake Taylor, Charlene de la Paz, John Albert Abed, and Angeline Vu.

## Drawbacks

Write something about the drawbacks

## Software

The software consists of a hub and client modules, both written in CircuitPython 9.0.1. The hub utilizes the Basilisk Simulation Framework(http://hanspeterschaub.info/basilisk/) to determine which sides of the CubeSat would be exposed to light.

## Libraries

[CircuitPython ulab](https://docs.circuitpython.org/en/latest/shared-bindings/ulab/index.html) - Numpy on a microcontroller

[Adafruit Python MCP4728](https://github.com/adafruit/Adafruit_CircuitPython_MCP4728) - Controls each of the LED light channels

[Adafruit Python ADS1X15](https://github.com/Ayush2309/Adafruit_ADS) - Reads all of the onboard thermocouples on the simulator

[CircuitPython pwmio](https://docs.circuitpython.org/en/latest/shared-bindings/pwmio/index.html) - Controls the halogen bulb

## License

All materials in this repo are copyright Portland State Aerospace Society and are licensed under the CERN Open Hardware Licence Version 2 - Strongly Reciprocal (CERN-OHL-S v2) and the GNU General Public License v3.0, or any later versions. A copy of the license is located [here](https://github.com/oresat/oresat-solar-simulator-software/blob/master/LICENSE.md).
