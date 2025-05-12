from lib.solar_simulator import SolarSimulator
import usb_cdc
import time

sim = SolarSimulator(verbose=1)

def handle_command(cmd: str):
    try:
        parts = cmd.strip().split()
        if len(parts) == 3 and parts[0] == "SET":
            channel = parts[1].lower()
            value = int(parts[2])
            update_channel(channel, value)
    except Exception as e:
        print(f"Command error: {e}")

def update_channel(channel: str, value: int):
    current = sim.current_light_settings
    if channel[0] in current:
        current[channel[0]] = value
    sim.setLEDs(
        v=current['v'],
        w=current['w'],
        c=current['c'],
        h=current['h']
    )

print("Ready to receive commands...")

while True:
    if usb_cdc.data.in_waiting:
        cmd = usb_cdc.data.readline().decode('utf-8')
        handle_command(cmd)
    time.sleep(0.01)
