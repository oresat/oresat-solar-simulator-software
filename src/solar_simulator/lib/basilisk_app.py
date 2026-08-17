"""Solar Simulator Basilisk Application."""

import time

import usb_cdc

from .solar_simulator import SolarSimulator as Sim
from .utils import calculate_light_intensity, check_temperature, display_status


class SolarSimulatorBasiliskApp:
    """Basilisk application class for the Solar Simulator."""

    def __init__(self, sim: Sim) -> None:
        """Initialize Solar Simulator Basilisk App."""
        self.sim = sim
        self.data = usb_cdc.data

    def run(self) -> None:
        """Run the Solar Simulator App."""
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

                        # Try setting intensity, error/bail if not.
                        try:
                            intensity = int(line)
                        except ValueError:
                            self.data.write(f"ERR invalid line: {line!r}\n".encode())
                            return

                        # Check intensity is within range, err/bail if not.
                        if not 0 <= intensity <= 100:
                            self.data.write(f"ERR intensity out of range: {intensity}\n".encode())
                            return

                        vals = calculate_light_intensity(intensity / 100)
                        v, w, c, h = (
                            int(vals[k] * 655) for k in ("Violet", "White", "Cyan", "Halogen")
                        )
                        self.sim.set_leds(v=v, w=w, c=c, h=h)
                        self.sim.current_light_settings = {'v': v, 'w': w, 'c': c, 'h': h}

                        check_temperature(self.sim)
                        display_status(
                            self.sim, writer=lambda s: self.data.write((s + "\n").encode())
                        )

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("SolarSimulatorBasiliskApp: interrupted, shutting down.")
        finally:
            self.sim.set_leds(0, 0, 0, 0)
