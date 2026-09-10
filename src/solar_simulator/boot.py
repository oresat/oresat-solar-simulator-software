"""Bootstrap the microcontroller on start up (hard reset and power on).

Docs: https://learn.adafruit.com/circuitpython-essentials/circuitpython-storage
"""

import supervisor
import usb_cdc

usb_cdc.enable(console=True, data=False)

# Auto-reload restarts code.py whenever anything writes to the board's drive, which is not
# a thing that may happen partway through an orbit: the restart drops the lamp to zero and
# every sample after it measures something other than the scenario. FlatHILS reads
# `boot_out.txt` and `commit` off that same drive to record which firmware drove a run, so
# the host asking a run's most basic question was itself enough to end it.
supervisor.runtime.autoreload = False
