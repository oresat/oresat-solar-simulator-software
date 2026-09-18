#!/usr/bin/env python3

"""Drive a solar simulator board from the host over its serial console.

The board takes one intensity value per line and answers one line back. Everything
interactive lives here rather than on the device: the prompt, the sweep, and turning the
lights off on the way out.
"""

import argparse
import math
import time

import serial

DEFAULT_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

# A known-dark start, then a few steps to watch a board answer. The trailing return to
# dark is left to the exit path, which every command goes through.
RAMP = (0, 25, 50, 75, 100)

SWEEP_STEPS = 101
MIN_PERIOD = 10


def sweep(peak: float) -> list:
    """Return one period of the sunrise-to-sunset sweep, as intensity values 0 to 100.

    An inverted cosine clamped at zero, so the sweep starts and ends dark and reaches
    `peak` halfway through. `peak` runs from 0 (dark) to 1 (the board's full rated
    output). The protocol carries whole percents, so each point is rounded to one.
    """
    points = []

    for step in range(SWEEP_STEPS):
        factor = -math.cos(2 * math.pi * step / (SWEEP_STEPS - 1))
        points.append(round(max(factor, 0.0) * peak * 100))

    return points


def exchange(conn: serial.Serial, line: object) -> str:
    """Send one line to the board and return its answer, without the newline."""
    conn.write(f"{line}\n".encode())

    return conn.readline().decode().rstrip()


def run_ramp(conn: serial.Serial) -> None:
    """Step through a few intensities, printing what the board answers to each."""
    for intensity in RAMP:
        print(exchange(conn, intensity))


def run_sweep(conn: serial.Serial, peak: float, period: float) -> None:
    """Sweep the lights through a full period, repeating until interrupted.

    A `WARN THERMAL` answer means the board is too hot and dropped the value. Nothing
    special is done about it: the next step offers a value again, which is what the board
    asks for, and the sweep picks up where it left off once the board has cooled.
    """
    points = sweep(peak)
    interval = period / SWEEP_STEPS
    step = 0
    start = time.monotonic()

    while True:
        print(exchange(conn, points[step]))
        step = (step + 1) % len(points)

        # Sleep off only what is left of this step, so the round trip to the board does
        # not stretch the period.
        elapsed = time.monotonic() - start
        time.sleep(interval - elapsed % interval)


def run_console(conn: serial.Serial) -> None:
    """Read lines from the operator and print what the board answers to each.

    Lines go to the board as typed. The board is the authority on what a valid intensity
    is, so an operator who fat-fingers one sees the protocol's own error rather than a
    second opinion from here.
    """
    print("Enter an intensity from 0 to 100. 'q' quits, leaving the lights off.")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            print()
            return

        if line.lower() in {"q", "quit", "exit"}:
            return

        if line:
            print(exchange(conn, line))


def main() -> None:
    """Parse the command line and drive the board."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default=DEFAULT_PORT, help="serial port the board is on")
    parser.add_argument("--baud", type=int, default=BAUD_RATE, help="serial port baud rate")

    commands = parser.add_subparsers(dest="command")
    commands.add_parser("ramp", help="step through a few intensities and print the answers")

    sweep_command = commands.add_parser("sweep", help="repeat a sunrise-to-sunset sweep")
    sweep_command.add_argument(
        "--peak", type=peak_intensity, default=0.5, help="brightest point, from 0 to 1"
    )
    sweep_command.add_argument(
        "--period", type=period_seconds, default=60.0, help="seconds per sweep"
    )

    args = parser.parse_args()

    with serial.Serial(args.port, args.baud, timeout=1) as conn:
        try:
            if args.command == "ramp":
                run_ramp(conn)
            elif args.command == "sweep":
                run_sweep(conn, args.peak, args.period)
            else:
                run_console(conn)
        except KeyboardInterrupt:
            print()
        finally:
            # The board holds the last value it was given until something replaces it, and
            # the only thing driving it is this process, which is now leaving.
            print(exchange(conn, 0))


def peak_intensity(value: str) -> float:
    """Parse a peak intensity, which runs from 0 (dark) to 1 (full rated output)."""
    peak = float(value)

    if not 0 <= peak <= 1:
        raise argparse.ArgumentTypeError("peak intensity must be between 0 and 1")

    return peak


def period_seconds(value: str) -> float:
    """Parse a sweep period, in seconds.

    Below the minimum the steps come faster than the board can answer them, and the sweep
    runs long rather than at the period asked for.
    """
    period = float(value)

    if period < MIN_PERIOD:
        raise argparse.ArgumentTypeError(f"period must be at least {MIN_PERIOD} seconds")

    return period


if __name__ == "__main__":
    main()
