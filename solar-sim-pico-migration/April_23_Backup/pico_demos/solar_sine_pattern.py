from ulab.numpy import sin
import adafruit_mcp4728 as MCP  # 12-bit DAC
# import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
# from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep, monotonic_ns
import supervisor
import pwmio
import board
import busio

i2c = busio.I2C(board.GP27, board.GP26)
mcp = MCP.MCP4728(i2c) # Default address = 0x60

angle = 0
hz = 1

while True:
	print(angle)
	angle += 1

	if angle > 359: angle = 0
	if angle < 0: angle = 359
	sleep(1/360)