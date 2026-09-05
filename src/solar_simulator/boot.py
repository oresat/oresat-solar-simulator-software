"""Bootstrap the microcontroller on start up (hard reset and power on).

Docs: https://learn.adafruit.com/circuitpython-essentials/circuitpython-storage
"""

import usb_cdc

usb_cdc.enable(console=True, data=False)
