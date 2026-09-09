"""Solar Simulator App 'Basilisk Mode' helper module."""

import sys
import time

import supervisor

from ..solar_simulator import SolarSimulator as Sim
from ..utils import calculate_light_intensity, check_temperature

try:
    from typing import Callable
except ImportError:
    Callable = None


def _reading(thermals: list) -> str:
    """Render a thermal reading as trailing protocol fields, or nothing if none was taken."""
    if not thermals:
        return ""

    led, heatsink, cell = thermals
    return f" led={led:.1f} heatsink={heatsink:.1f} cell={cell:.1f}"


class BasiliskMode:
    """Implements the Basilisk Mode functionality with UART communication for CircuitPython."""

    QUIET_TIMEOUT_S = 5.0
    """How long the host may say nothing before the lamp is driven to zero.

    Five missed commands at the one-per-second cadence FlatHILS drives (`STEP_S`), which
    is long enough to ride out a host that is merely late and short enough that a host
    that is gone cannot leave the lamp lit and unwatched.
    """

    def __init__(self, sim: Sim, clock: "Callable[[], float]" = time.monotonic) -> None:
        """Initialize basilisk mode."""
        self.sim = sim
        self.clock = clock
        self.buffer = ""
        self.last_line_at = clock()
        self.safed = False

    def run(self) -> None:
        """Run basilisk mode loop."""
        while True:
            self.tick()

    def tick(self) -> None:
        """Advance the loop one step: take a waiting byte, then watch the host's silence.

        Nothing here blocks, so the watchdog is still reached when the host has stopped
        mid-line or stopped altogether.
        """
        if supervisor.runtime.serial_bytes_available:
            self.buffer += sys.stdin.read(1)

            if "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                self.receive(line)
                time.sleep(0.1)

        if not self.safed and self.clock() - self.last_line_at > self.QUIET_TIMEOUT_S:
            self.safe_the_lamp()
            self.safed = True

    def receive(self, line: str) -> None:
        """Answer one line from the host, and note that the host is alive.

        A line the protocol rejects still rearms the watchdog: a host sending a value this
        board will not take is a host that is talking, and the watchdog exists to catch
        one that has stopped.
        """
        self.apply_line(line)
        self.last_line_at = self.clock()
        self.safed = False

    def safe_the_lamp(self) -> None:
        """Drive the lamp to zero because the host has gone quiet.

        The only mechanism that can safe the lamp once the host is gone. A crashed or
        unplugged host cannot act, and thermal monitoring runs only when a command arrives,
        so without this a lit lamp would hold its last setpoint unwatched and unmeasured
        (ADR-0007 in `brysat-flathils`).

        Drops the held setpoint along with the live one. A panel cooling out of thermal
        shutdown resumes at whatever `pending_light_settings` carries, and resuming to a
        value commanded before the silence would relight a lamp nobody is watching.

        Says nothing on the wire. Every response answers a command, and a host that has
        stopped sending is either gone or can see the gap on its own clock.
        """
        self.sim.set_leds(0, 0, 0, 0)
        self.sim.pending_light_settings = {'v': 0, 'w': 0, 'c': 0, 'h': 0}

    def apply_line(self, line: str) -> None:
        """Apply one line of the Basilisk protocol: a bare integer from 0 to 100.

        Answers with exactly one response line, so that a stray byte on the wire cannot
        take down an unattended run:

            OK <intensity> <reading>          the value was applied
            WARN THERMAL <intensity> <reading>
                                              the value is valid and is now the pending
                                              setpoint, held off while thermal shutdown
                                              is active
            ERR <CODE> <description>          the line could not be acted on; CODE is the
                                              token the caller branches on

        `OK` and `WARN` carry the reading the thermal decision was made on, as
        `led=<C> heatsink=<C> cell=<C>`. The token is the state and the temperatures say
        how far that state is from changing, so a host can tell a panel that is cooling
        from a board that has died (ADR-0007 in `brysat-flathils`). An `ERR` answers a
        line that never reached the thermal check, and carries no reading.
        """
        line = line.replace("\x00", "").strip()

        if not line:
            print("ERR EMPTY no intensity value received")
            return

        try:
            intensity = int(line)
        except ValueError:
            print(f"ERR PARSE invalid intensity value received: {line}")
            return

        if not 0 <= intensity <= 100:
            print(f"ERR RANGE invalid intensity value received: {line}")
            return

        intensity_values = calculate_light_intensity(intensity / 100)
        violet = int(intensity_values["Violet"] * 655)
        white = int(intensity_values["White"] * 655)
        cyan = int(intensity_values["Cyan"] * 655)
        halogen = int(intensity_values["Halogen"] * 655)

        # Driving the lamp while the panel is cooling would relight it until the check
        # below cut it again, once per line the host sends. Hold the value instead.
        if self.sim.therm_safe:
            self.sim.set_leds(v=violet, w=white, c=cyan, h=halogen)
        else:
            self.sim.pending_light_settings = {'v': violet, 'w': white, 'c': cyan, 'h': halogen}

        lit, thermals = check_temperature(self.sim)

        if lit:
            print(f"OK {intensity}{_reading(thermals)}")
        else:
            print(f"WARN THERMAL {intensity}{_reading(thermals)}")
