#!/usr/bin/env python3

"""Drive a solar simulator board from the host over serial."""

import argparse
import time

import serial


RAMP = (0, 25, 50, 75, 100)


def main() -> None:
    """Parse the command line and drive the board."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("ramp", help="step through a few intensities and print the answers")

    args = parser.parse_args()

    with serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1) as conn:
        try:
            if args.command == "ramp":
                run_ramp(conn)
            else:
                run_console(conn)
        except KeyboardInterrupt:
            print()
        finally:
            print(exchange(conn, 0))


def run_ramp(conn: serial.Serial) -> None:
    """Step through a few intensities, printing what the board answers to each."""
    for intensity in RAMP:
        time.sleep(1)
        print(exchange(conn, intensity))


def run_console(conn: serial.Serial) -> None:
    """Read commands from the operator and print the board's responses."""
    print("Enter an intensity from 0 to 100.")

    while True:
        cmd = input("> ").strip()

        if cmd:
            print(exchange(conn, cmd))


def exchange(conn: serial.Serial, line: object) -> str:
    """Send one line to the board and return its answer, without the newline."""
    conn.write(f"{line}\n".encode())

    return conn.readline().decode().rstrip()


if __name__ == "__main__":
    main()
