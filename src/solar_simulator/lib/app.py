"""Solar Simulator Application."""

import time

import usb_cdc

from .solar_simulator import SolarSimulator as Sim
from .utils import calculate_light_intensity, check_temperature, display_status


class SolarSimulatorApp:
    """Main application class for the Solar Simulator."""

    def __init__(self, sim: Sim) -> None:
        """Initialize Solar Simulator App."""
        self.sim = sim

    def run(self, build_mode: str) -> None:
        """Run the Solar Simulator App for a given build mode.

        Headless is the default build mode, which is optimized for integration
        with FlatHILS and Basilisk.
        """
        if build_mode == "complete":
            from .cli import Cli  # noqa: PLC0415

            cli = Cli(self.sim)
            cli.run()
        elif build_mode == "headless":
            headless = Headless(self.sim)
            headless.run()


class Headless:
    """Headless class.

    Encapsulates the main loop for headless operation.
    """

    def __init__(self, sim: Sim) -> None:
        """Initialize headless mode."""
        self.sim = sim
        self.data = usb_cdc.data

    def run(self) -> None:
        """Run headless mode."""
        self.data.write(b"READY\n")

        buffer = ""
        try:
            while True:
                if self.data.in_waiting:
                    buffer += self.data.read(self.data.in_waiting).decode()

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)

                        if not line:
                            return

                        # Try setting intensity, bail if not.
                        try:
                            intensity = int(line)
                        except ValueError:
                            self.data.write(f"ERR invalid line: {line!r}\n".encode())
                            return

                        # Check intensity is within range, bail if not.
                        if not 0 <= intensity <= 100:
                            self.data.write(f"ERR intensity out of range: {intensity}\n".encode())
                            return

                        vals = calculate_light_intensity(intensity / 100)
                        v, w, c, h = (
                            int(vals[k] * 655) for k in ("Violet", "White", "Cyan", "Halogen")
                        )
                        self.sim.set_leds(v=v, w=w, c=c, h=h)
                        self.sim.current_light_settings = {"v": v, "w": w, "c": c, "h": h}

                        check_temperature(self.sim)
                        display_status(
                            self.sim, writer=lambda s: self.data.write((f"{s}\n").encode())
                        )

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("SolarSimulatorHeadlessApp: interrupted, shutting down.")
        finally:
            self.sim.set_leds(0, 0, 0, 0)
