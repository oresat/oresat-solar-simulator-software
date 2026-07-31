# Installation

On this page, you'll find step-by-step instructions to install everything to a working order.

## Hardware Requirements

- [Oresat Solar Simulator Hardware](https://github.com/oresat/oresat-solar-simulator-hardware)
- Raspberry Pi Pico (RP2040) and Solar Simulator Board
- 12v 10A power supply (get higher current supply if running multiple on the same supply)

## Pico Firmware

Flashing the CircuitPython firmware onto the Raspberry Pi Pico is a well documented exercise.
See [CircuitPython for Raspberry Pi Pico](https://circuitpython.org/board/raspberry_pi_pico/) for the `.uf2` download,
and follow the instructions under "Learn how to install CircuitPython on this board" for detailed instructions.

Once CircuitPython is flashed to the board, and while it's still plugged into your developer machine, run:

```sh
make deploy
```

This command will build the Solar Simulator Software and deploy it to the Pico.
