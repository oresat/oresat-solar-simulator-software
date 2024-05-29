'''
Talker code from Romilly (see https://gist.github.com/romilly/66db6afa88e5a113b3804308e8c4c37c )

demo stolen by : Daniel Monahan (dkm-ee@github.com)

To use this script, first load the demo onto your pico
cp .../pico-demos/pyserial-demo.py -> /yourboard/main.py

then open a python repl on your computer and run the following:
    from talker import Talker
    t = Talker()

    # should run even if main.py isnt on your board:
    t.send('2 + 2')
    t.recieve() # Should print '4'

    # requires the demo on your board:
    t.send('from main.py import *') # Import on/off functions
    t.send('on()') # This should turn the onboard LED on
    t.send('off()') # This SHOULD turn the onboard LED off

'''

import serial


class Talker:
    TERMINATOR = '\r'.encode('UTF8')

    def __init__(self, timeout=1):
        self.serial = serial.Serial('/dev/ttyACM0', 115200, timeout=timeout)

    def send(self, text: str):
        line = '%s\r\f' % text
        self.serial.write(line.encode('utf-8'))
        reply = self.receive()
        reply = reply.replace('>>> ','') # lines after first will be prefixed by a propmt
        if reply != text: # the line should be echoed, so the result should match
            raise ValueError('expected %s got %s' % (text, reply))

    def receive(self) -> str:
        line = self.serial.read_until(self.TERMINATOR)
        return line.decode('UTF8').strip()

    def close(self):
        self.serial.close()
