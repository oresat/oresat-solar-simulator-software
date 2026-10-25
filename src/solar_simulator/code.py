import asyncio

import board
from adafruit_ads1x15.ads1015 import ADS1015  # 4-channel ADC
from adafruit_mcp4728 import MCP4728  # 12-bit DAC
from busio import I2C
from pwmio import PWMOut

from lights import Lights
from thermal import Thermal

if board.board_id == "seeeduino_xiao_rp2040":
    # Solar simulator board v2.1
    scl = board.D5
    sda = board.D4
    pwm = board.D2
elif board.board_id == "raspberry_pi_pico":
    # Solar simulator board v2.0
    scl = board.GP27
    sda = board.GP26
    pwm = board.GP28
else:
    raise RuntimeError(f"Unknown board {board.board_id}")

hal = PWMOut(pin=pwm, frequency=5000, duty_cycle=0)
i2c = I2C(scl=scl, sda=sda)
ads = ADS1015(i2c)
mcp = MCP4728(i2c)

with Lights(dac=mcp, pwm=hal) as lights:
    temp = Thermal(adc=ads)
    therm = asyncio.create_task(temp.run(lights))
    stdin = asyncio.create_task(lights.run(temp))
    asyncio.run(asyncio.gather(therm, stdin))
