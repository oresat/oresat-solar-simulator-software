#!/usr/bin/env python3

"""Ramp a board running the `headless` build through its intensity range.

Run it to see how headless mode answers a stream of intensity values, and after
changing the protocol to check that a real device still responds as expected.
"""

import serial

with serial.Serial("/dev/ttyACM0", 115200, timeout=1) as conn:
    for intensity in (0, 25, 50, 75, 100, 0):
        conn.write(f"{intensity}\n".encode())
        print(conn.readline())
