# input_handler.py

import supervisor

class InputHandler:
    """
    Handles user input and real-time Ctrl-C detection.
    """

    def __init__(self, simulator):
        self.simulator = simulator

    def check_for_interrupt(self):
        """
        Checks for a keyboard interrupt (Ctrl-C) and turns off LEDs if detected.
        """
        if supervisor.runtime.serial_bytes_available:
            input_char = input().strip()
            if input_char == '\x03':  # Ctrl-C ASCII: 3
                print("\nCtrl-C detected, turning off LEDs...")
                self.simulator.set_leds(0, 0, 0, 0, 0)
                raise KeyboardInterrupt

