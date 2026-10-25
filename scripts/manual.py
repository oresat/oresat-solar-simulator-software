#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace

from serial import Serial

parser = ArgumentParser()
parser.add_argument('--path', default='/dev/ttyACM0')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--intensity', type=float)
group.add_argument('--raw', type=int, nargs=4)
group.add_argument('--percent', type=float, nargs=4)
args = parser.parse_args()

def command(args: Namespace) -> str:
    if args.intensity is not None:
        if not 0 <= args.intensity <= 1:
            raise SystemExit("Intensity must be between 0 and 1")
        return f'{args.intensity:0.6f}'

    if args.raw is not None:
        for v in args.raw:
            if not 0 <= v <= 65535:
                raise SystemExit("Raw value must be between 0 and 65535")
        return ' '.join(f'{v}' for v in args.raw)

    if args.percent is not None:
        for p in args.percent:
            if not 0 <= p <= 100:
                raise SystemExit("Percent must be between 0 and 100")
        return ' '.join(f'{int(p*655.35)}' for p in args.percent)

    raise SystemExit("Invalid argument set")


with Serial(args.path, 115200) as s:
    s.write(f'{command(args)}\n'.encode())
    while True:
        print(s.readline().decode().strip())

