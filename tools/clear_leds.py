from Adafruit_I2C import Adafruit_I2C
import adafruit_mcp4728
import busio

i2c = busio.I2C('I2C1_SCL', 'I2C1_SDA')
mcp4728 = adafruit_mcp4728.MCP4728(i2c)

mcp4728.channel_a.value = 0
mcp4728.channel_b.value = 0
mcp4728.channel_c.value = 0
mcp4728.channel_d.value = 0