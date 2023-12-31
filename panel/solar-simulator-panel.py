from Adafruit_I2C import Adafruit_I2C
import adafruit_mcp4728
import Adafruit_ADS1x15
import socketio
import argparse
import json
import os
import busio
import time
from numpy import linspace, uint16
GAIN = 1
global system_state
system_state = 0

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


# Setup I2C
i2c = busio.I2C('I2C1_SCL', 'I2C1_SDA')
mcp4728 = adafruit_mcp4728.MCP4728(i2c)
adc = Adafruit_ADS1x15.ADS1015(busnum=1)

# Setup PWM
BB_PER = 4000
PWM_PIN = "P2_1"
PWM_PATH = '/dev/bone/pwm/1/a'

print('Setting Period')
os.system(f'sudo echo {BB_PER} >> {PWM_PATH}/period')
print('Setting enable')
if os.system(f'cat {PWM_PATH}/enable') == 0:
    os.system(f'sudo echo 1 >> {PWM_PATH}/enable')
print('Setting duty_cycle')
os.system(f'echo 0 >> {PWM_PATH}/duty_cycle')


@sio.event
def connect():
    '''
    Executed upon client connecting to server. 
    Client emits a 'set_sid' message so that the server assigns it the correct session.
    '''
    global client_connected, system_state
    print('Connected to server')
    # Set the sid for the client upon reconnection
    sio.emit('set_sid', args.clientid)
    client_connected = True
    os.system(f'echo 1 > {led3}/brightness')
    system_state = 1
    
    
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
def set_panel(level):
    '''
    Message received from the server that sets the client's PWM value.
    Client responds with a message containing its client_id, and data from photodiode and thermistor.

    :param level: power level
    '''
    if system_state > 0:
        print(f'my power level is at {level}')
        try:
            mcp4728.channel_a.value = steps[0][level]
            mcp4728.channel_b.value = steps[1][level]
            mcp4728.channel_c.value = steps[2][level]
            mcp4728.channel_d.value = steps[3][level]
            
            os.system(f'echo {steps[4][level]} >> {PWM_PATH}/duty_cycle')
            print(f'PWM duty_cycle is: {steps[4][level]}')
        except Exception as e:
            print(e)
            print('Failed to set light levels')
            
        try:
            values = [0] * 4
            for i in range(4):
            # Read the specified ADC channel using the previously set gain value.
                values[i] = adc.read_adc(i, gain=GAIN)
        except Exception as e:
            print(e)
            print('Failed to get temperature data')
            temp_values = (0, 0, 0)
            photo_value = 0
        else:
            print(values)
            temp_values = (values[0], values[1], values[2])
            photo_value = values[3]
            
    sio.emit('panel_response', [args.clientid, temp_values, photo_value])
    os.system(f'echo 1 > {led2}/brightness')
    os.system(f'echo 0 > {led2}/brightness')

@sio.event
def set_state(msg):
    '''
    sets the running state that the panel is in
    0 - halt, all lamps off
    1 - normal, lamps can accept normal values
    2 - safe, lamps are limited to 30% power and UV is off
    '''
    global new_state
    new_state = msg

def state_mon():
    global steps, new_state, system_state
    while True:
        if system_state != new_state:
            system_state = new_state
            print(f'Changing state to {new_state}')
            if system_state == 0:
                os.system(f'echo none > {led0}/trigger')
                os.system(f'echo 1 > {led0}/brightness')
                os.system(f'echo 1 > {led1}/brightness')
                steps = calc_steps(0)
            elif system_state == 1:                
                os.system(f'echo 0 > {led0}/brightness')
                os.system(f'echo 0 > {led1}/brightness')
                os.system(f'echo heartbeat > {led0}/trigger')
                steps = calc_steps(1)
            elif system_state == 2:
                os.system(f'echo 0 > {led0}/brightness')
                os.system(f'echo 1 > {led1}/brightness')
                os.system(f'echo heartbeat > {led0}/trigger')
                steps = calc_steps(0.3)
 
                
def calc_steps(limiter):
    '''
    Calculates the light steps for the LEDs based on calibrated
    mins/max and any specified limiter

    params limiter: float between 0-1 to scale the power for safety
    '''
    max_voltage = int(65535 * limiter)
    red_start = data['red_start']
    grn_start = data['grn_start']
    blu_start = data['blu_start']
    UV_start  = data['UV_start']
    PWM_start = data['PWM_start'] * BB_PER / 100
    red_max = int(data['red_max'] * limiter)
    grn_max = int(data['grn_max'] * limiter)
    blu_max = int(data['blu_max'] * limiter)
    UV_max  = int(data['UV_max'] * limiter)
    PWM_max = int(data['PWM_max'] * limiter * BB_PER / 100)
    red_steps = linspace(red_start, red_max, num=101, dtype=uint16)
    grn_steps = linspace(grn_start, grn_max, num=101, dtype=uint16)
    blu_steps = linspace(blu_start, blu_max, num=101, dtype=uint16)
    PWM_steps = linspace(PWM_start, PWM_max, num=101, dtype=uint16)
    if system_state == 2:
        UV_steps = [0] * 101
    else:
        UV_steps = linspace(UV_start, UV_max, num=101, dtype=uint16)
    return [red_steps, grn_steps, blu_steps, UV_steps, PWM_steps]
        

# Wait for events
sio.wait()
while True:
    try:
        # Connect to the server
        sio.connect(f'http://{args.ipaddress}:{8000}') 
    except Exception as e:
        print(e)
    else:
        # Monitor State
        new_state = 1
        thread = sio.start_background_task(state_mon)
        # Load Calibration
        steps = calc_steps(1)
        sio.wait()

    print("Attempting to connect...")
    time.sleep(5)
    
