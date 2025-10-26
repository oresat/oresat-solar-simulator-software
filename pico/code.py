# main.py

from lib.solar_simulator import SolarSimulator
from lib.app import SolarSimulatorApp

def main():
    # Initialize SolarSimulator
    sim = SolarSimulator(verbose=0)
    sim.setLEDs(0, 0, 0, 0, 0)  # Ensure all LEDs are turned off initially

    # Run the application
    app = SolarSimulatorApp(sim)
    app.run()

if __name__ == "__main__":
    main()
