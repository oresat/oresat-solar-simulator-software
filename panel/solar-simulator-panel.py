from Adafruit_I2C import Adafruit_I2C
import adafruit_mcp4728
import socketio
import argparse
import json
from debugdata import fake_photo, fake_temp

with open('panel-options.conf', 'r') as jsonfile:
    data = json.load(jsonfile)


# Setup SocketIO
global client_connected
client_connected = False
sio = socketio.Client(logger=True)

# Initialize ArgParse
parser = argparse.ArgumentParser(prog='solar-sim-client', description='oresat-solar-simulator client node', 
                                 epilog='https://github.com/oresat/oresat-solar-simulator')

parser.add_argument('-i', '--ipaddress',type=str, help='ip-address of the server', 
                    required=False, default=data['server-ip'], metavar='192.168.X.2')
parser.add_argument('-c', '--clientid', type=int, help='id the client will report to server', 
                    required=False, default=data['client-id'], choices=range(0,4))

args = parser.parse_args()

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
sio.connect(f'http://{args.ipaddress}:{8000}')

# thread = sio.start_background_task(notificationLED)

# Wait for events
sio.wait()
