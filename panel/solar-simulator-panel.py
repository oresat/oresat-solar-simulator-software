from Adafruit_I2C import Adafruit_I2C
import adafruit_mcp4728
import socketio
import argparse
import json
import os

with open('panel-options.conf', 'r') as jsonfile:
    data = json.load(jsonfile)

# Setup led control

led0 = '/sys/class/leds/beaglebone:green:usr0'
led1 = '/sys/class/leds/beaglebone:green:usr1'
led2 = '/sys/class/leds/beaglebone:green:usr2'
led3 = '/sys/class/leds/beaglebone:green:usr3'

os.system(f'echo none > {led0}/trigger')
os.system(f'echo 0 > {led0}/brightness')
os.system(f'echo none > {led1}/trigger')
os.system(f'echo 0 > {led1}/brightness')
os.system(f'echo none > {led2}/trigger')
os.system(f'echo 0 > {led2}/brightness')
os.system(f'echo none > {led3}/trigger')
os.system(f'echo 0 > {led3}/brightness')

# Setup SocketIO
global client_connected
client_connected = False
sio = socketio.Client(logger=True)

# Initialize ArgParse
parser = argparse.ArgumentParser(prog='solar-sim-client', description='oresat-solar-simulator client node', 
                                 epilog='https://github.com/oresat/oresat-solar-simulator')

parser.add_argument('-i', '--ipaddress',type=str, help='ip-address of the server', 
                    required=False, default=data['server-ip'], metavar='192.168.X.2')
parser.add_argument('-p', '--port', type=int, help='port hub is listening on',
                     required=False, default=data['port'])
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
    sio.emit('set_sid', args.clientid)
    client_connected = True
    os.system(f'echo 1 > {led3}/brightness')
    
    
@sio.event
def disconnect():
    '''
    Executed upon client disconnection from the server.
    '''
    global client_connected
    print('Disconnected from server')
    client_connected = False
    os.system(f'echo 0 > {led3}/brightness')


@sio.event
def pwm_comm(level):
    '''
    Message received from the server that sets the client's PWM value.
    Client responds with a message containing its client_id, and data from photodiode and thermistor.

    :param level: power level
    '''
    LEDPWM = level
    print(f'my LED is at {LEDPWM}')
    # update to actually do stuff
    
    sio.emit('panel_response', [args.clientid, 'temp', 'photo'])
    os.system(f'echo 1 > {led2}/brightness')
    os.system(f'echo 0 > {led2}/brightness')

# Connect to the server
sio.connect(f'http://{args.ipaddress}:{8000}')


# Wait for events
sio.wait()
