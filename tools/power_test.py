from Adafruit_I2C import Adafruit_I2C
import Adafruit_BBIO.PWM as PWM
import adafruit_mcp4728
import busio
from time import sleep
from numpy import linspace, uint16

BB_FREQ = 20e3
PWM_PIN = "P2_1"
PWM.start(PWM_PIN, 0, BB_FREQ)

min_voltage = 0
max_voltage = 65535
i2c = busio.I2C('I2C1_SCL', 'I2C1_SDA')
mcp4728 = adafruit_mcp4728.MCP4728(i2c)
steps = linspace(0, max_voltage, num=100, dtype=uint16)

for i in steps:
    print(steps[i])
    # Red LED
    mcp4728.channel_a.value = steps[i]# min_voltage to turn off. steps[i] to sweep

    # Green LED
    mcp4728.channel_b.value = steps[i]# min_voltage to turn off. steps[i] to sweep

    # Blue LED
    mcp4728.channel_c.value = steps[i]# min_voltage to turn off. steps[i] to sweep

    # # UV LED
    # mcp4728.channel_d.value = steps[i]
    
    # Halogen PWM
    PWM.set_duty_cycle(PWM_PIN, i)#0 to turn off, 100 to turn on. i to sweep

    sleep(1)
# Red LED off
mcp4728.channel_a.value = 0# min_voltage to turn off. steps[i] to sweep

# Green LED off
mcp4728.channel_b.value = 0# min_voltage to turn off. steps[i] to sweep

# Blue LED off
mcp4728.channel_c.value = 0 # min_voltage to turn off. steps[i] to sweep

#PWM off
PWM.stop(PWM_PIN)
PWM.cleanup()

$ ping github.com
