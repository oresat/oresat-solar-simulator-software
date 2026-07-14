from lib.solar_simulator import SolarSimulator
from lib.app import SolarSimulatorApp

def main():
    sim = SolarSimulator(verbose=0)
    sim.setLEDs(0, 0, 0, 0, 0)

    app = SolarSimulatorApp(sim)
    app.run()

if __name__ == "__main__":
    main()
