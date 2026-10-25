#!/usr/bin/env python3
import time
from argparse import ArgumentParser
from math import cos, pi
from serial import Serial


parser = ArgumentParser()
parser.add_argument('--path', default='/dev/ttyACM0')
parser.add_argument('--intensity', type=float, default=0.5)
parser.add_argument('--period', type=float, default=10)
parser.add_argument('--step', type=float, default=0.1)
args = parser.parse_args()

if not 0 <= args.intensity <= 1:
    raise SystemExit("Intensity must be between 0 and 1")

with Serial(args.path, 115200) as s:
    try:
        start = time.monotonic()
        while True:
            val = max(0, -cos(2*pi * (time.monotonic() - start)/args.period) * args.intensity)

            s.write(f'{val:.6f}\n'.encode())
            print(s.readline().decode().strip())

            before_sleep = time.monotonic() - start
            time.sleep(args.step - before_sleep % args.step)
    finally:
        s.write('0\n'.encode())

