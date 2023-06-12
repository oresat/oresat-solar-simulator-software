import Adafruit_BBIO.PWM as PWM # Used for demo validation
from Adafruit_I2C import Adafruit_I2C
import adafruit_mcp4728
from debugdata import fake_photo, fake_temp

import socketio

global client_connected
client_connected = False
sio = socketio.Client(logger=True)

# TODO: Read from file
server_address = '192.168.6.1'
server_port = '8000'
client_id = 2


### PWM Demo Remove for Final Code
BB_FREQ = 250e3
LED_PIN = "P9_16"
PWM.start(LED_PIN, 0, BB_FREQ)
###

@sio.event
def connect():
    '''
    Executed upon client connecting to server. 
    Client emits a 'set_sid' message so that the server assigns it the correct session.
    '''
    global client_connected
    print('Connected to server')
    # Set the sid for the client upon reconnection
    sio.emit('set_sid', client_id)
    client_connected = True
    
    
@sio.event
def disconnect():
    '''
    Executed upon client disconnection from the server.
    '''
    global client_connected
    print('Disconnected from server')
    client_connected = False


@sio.event
def pwm_comm(msg):
    '''
    Message received from the server that sets the client's PWM value.
    Client responds with a message containing its client_id, and data from photodiode and thermistor.
    '''
    LEDPWM = msg
    print(f'my LED is at {LEDPWM}')
    PWM.set_duty_cycle(LED_PIN, LEDPWM) # Remove for final
    sio.emit('sim_response', [client_id, fake_temp[client_id], fake_photo[client_id]])

def notificationLED():
    '''
    Updates the userLEDs on the PB to display information.
    Not working, for now the call is removed
    '''
    global client_connected
    while True:
        if client_connected:
            print('We are connected :)')
        else:
            print('We are not connected :(')
        sio.sleep(5)

# Connect to the server
sio.connect(f'http://{server_address}:{server_port}')

# thread = sio.start_background_task(notificationLED)

# Wait for events
sio.wait()
