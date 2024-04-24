from ulab.numpy import sin
import adafruit_mcp4728 as MCP  # 12-bit DAC
# import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
# from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep, monotonic_ns
import pwmio
import board
import busio

# i2c = busio.I2C(board.GP27, board.GP26)
# mcp = MCP.MCP4728(i2c) # Default address = 0x60

angle = 0
hz = 10
high = 1
low = 0
direction = True
step = 0.01

while True:
	print(f"Angle: {angle:0.2f}, Dir: {'up' if direction else 'down'}")

	if direction:
		angle += step
	else:
		angle -= step

	if angle > high:
		angle = high - step
		direction = False
	if angle < low:
		angle = low + step
		direction = True
	
	sleep(1/hz/high)
