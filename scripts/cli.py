#!/usr/bin/env python3

"""Interactive cli for driving the solar simulator from the host over serial."""

from __future__ import annotations

import math
import time

import serial


def main() -> None:
    """Open the board and run the mode menu."""
    with serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1) as conn:
        print("Solar Simulator")

        try:
            while True:
                print()
                print("1. Auto Mode")
                print("2. Manual Mode")
                print("q. Quit")

                choice = input("Your choice: ").strip()

                if choice == "1":
                    AutoMode(conn).run()
                elif choice == "2":
                    ManualMode(conn).run()
                elif choice == "q":
                    break
                else:
                    print("Invalid input. Please enter 1, 2, or q.")
        except (EOFError, KeyboardInterrupt):
            print()
        finally:
            print(exchange(conn, 0))


def exchange(conn: serial.Serial, req: object) -> str:
    """Send a request to the board and return its answer."""
    conn.write(f"{req}\n".encode())
    return conn.readline().decode().rstrip()


class AutoMode:
    """Auto Mode helper class for the Solar Simulator App."""

    WAVE_SAMPLES = 101
    MIN_PERIOD = 10

    def __init__(self, conn: serial.Serial) -> None:
        """Initialize auto mode."""
        self.conn = conn

    def run(self) -> None:
        """Prompt for a peak and period, then drive the wave until interrupted."""
        print("Entering Auto Mode")

        prompt = "Please enter the desired peak light intensity (0 to 100): "
        peak = int(input(prompt).strip())

        print(f"Maximum light intensity set to: {peak}")

        try:
            period = int(input(f"Please enter desired period of sinusoid "
                               f"(at least {self.MIN_PERIOD}, in seconds): "))
        except ValueError:
            print("Invalid input. Please enter a whole number of seconds.")
            return

        if period < self.MIN_PERIOD:
            print(f"Invalid input. Please enter a number of at least {self.MIN_PERIOD}.")
            return

        wave = self.build_wave(self.WAVE_SAMPLES)
        loop_time = period / self.WAVE_SAMPLES
        level = 0

        print("Running. Press Ctrl-C to return to the menu.")

        try:
            loop_start = time.monotonic()

            while True:
                response = exchange(self.conn, round(wave[level] * peak))
                print(response)

                if response.startswith("ERR"):
                    print("Board reported an error, returning to the menu.")
                    return

                level = (level + 1) % len(wave)

                # Adjust current repetition's timing as needed by sleeping
                before_sleep = time.monotonic() - loop_start
                time.sleep(loop_time - before_sleep % loop_time)
        except KeyboardInterrupt:
            print("\nExiting Auto Mode.")

    @staticmethod
    def build_wave(samples: int) -> list:
        """Return one period of an inverted cosine, clamped at zero, scaled 0 to 1."""
        return [max(0.0, -math.cos(2 * math.pi * i / (samples - 1))) for i in range(samples)]


class ManualMode:
    """Send intensities from the user to the board."""

    def __init__(self, conn: serial.Serial) -> None:
        """Initialize manual mode against an open serial connection."""
        self.conn = conn

    def run(self) -> None:
        """Read intensities from user (or quit if they want to leave)."""
        print("Entering Manual Mode")
        print("Enter a light intensity from 0 to 100.")
        print("Type 'q' to return to the main menu.")

        while True:
            entry = input("> ").strip()

            if entry.lower() == "q":
                print("Exiting Manual Mode.")
                return

            if not entry:
                continue

            intensity = self.parse_intensity(entry)
            if intensity is not None:
                print(exchange(self.conn, intensity))

    @staticmethod
    def parse_intensity(entry: str) -> int | None:
        """Return the entry as an intensity from 0 to 100, or None."""
        # TODO: The original 'Manual Mode' takes intensity vals 0-1, which is odd, because it
        # breaks the pattern we expect everywhere else (an integer 0-100). Fix.

        # TODO: Manual Mode should be able to manually adjust individual light intensities, but
        # that's not something the protocol can handle as implemented. Fix.
        try:
            intensity = int(entry)
        except ValueError:
            print("Invalid input. Please enter a whole number between 0 and 100.")
            return None

        if not 0 <= intensity <= 100:
            print("Invalid input. Please enter a number between 0 and 100.")
            return None

        return intensity


if __name__ == "__main__":
    main()
