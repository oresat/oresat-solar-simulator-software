"""Bootstrap the microcontroller on start up (hard reset and power on).

Docs: https://learn.adafruit.com/circuitpython-essentials/circuitpython-storage
"""

import supervisor

supervisor.status_bar.console = False
