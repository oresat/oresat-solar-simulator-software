from Adafruit_I2C import Adafruit_I2C
import adafruit_mcp4728
import argparse
import json
import os
import busio
import time
from numpy import linspace, uint16
GAIN = 1


# Initialize ArgParse
parser = argparse.ArgumentParser(prog='solar-sim-client', description='oresat-solar-simulator client node', 
                                 epilog='https://github.com/oresat/oresat-solar-simulator')

parser.add_argument('-r', '--red', type=int, help='set red LED', required=False, default=0)
parser.add_argument('-g', '--green', type=int, help='set green LED', required=False, default=0)
parser.add_argument('-b', '--blue', type=int, help='set blue LED', required=False, default=0)
parser.add_argument('-u', '--uv', type=int, help='set UV LED', required=False, default=0)
parser.add_argument('-p', '--pwm', type=int, help='set PWM', required=False, default=0)
parser.add_argument('-a', '--all', type=int, help='set all', required=False, default=0)

args = parser.parse_args()

if args.all > 0:
    args.red = args.all
    args.green = args.all
    args.blue = args.all
    args.uv = args.all
    args.pwm = args.all

# Setup I2C
i2c = busio.I2C('I2C1_SCL', 'I2C1_SDA')
mcp4728 = adafruit_mcp4728.MCP4728(i2c)

# Setup PWM
BB_PER = 4000
PWM_PIN = "P2_1"
PWM_PATH = '/dev/bone/pwm/1/a'

print('Setting Period')
os.system(f'sudo echo {BB_PER} >> {PWM_PATH}/period')
print('Setting duty_cycle to 0')
os.system(f'echo 0 >> {PWM_PATH}/duty_cycle')
print('Setting enable')
if os.system(f'cat {PWM_PATH}/enable') == 0:
    os.system(f'sudo echo 1 >> {PWM_PATH}/enable')

def calc_steps(limiter):
    '''
    Calculates the light steps for the LEDs based on calibrated
    mins/max and any specified limiter

    params limiter: float between 0-1 to scale the power for safety
    '''
    max_voltage = int(65535 * limiter)
    red_start = 10756
    grn_start = 10140
    blu_start = 10620
    UV_start  = 10620
    PWM_start = 0 * BB_PER / 100
    red_max = 65535
    grn_max = 65535
    blu_max = 65535
    UV_max  = 65535
    PWM_max = int(75 * limiter * BB_PER / 100)
    red_steps = linspace(red_start, red_max, num=101, dtype=uint16)
    grn_steps = linspace(grn_start, grn_max, num=101, dtype=uint16)
    blu_steps = linspace(blu_start, blu_max, num=101, dtype=uint16)
    PWM_steps = linspace(PWM_start, PWM_max, num=101, dtype=uint16)

    UV_steps = linspace(UV_start, UV_max, num=101, dtype=uint16)
    return [red_steps, grn_steps, blu_steps, UV_steps, PWM_steps]


steps = calc_steps(1)
print(f'Setting LEDs')

print(args.red)
try:
    print(f'Red = {steps[0][args.red]} ({args.red}%)')
    mcp4728.channel_a.value = steps[0][args.red]
    print(f'Green = {steps[0][args.green]} ({args.green}%)')
    mcp4728.channel_b.value = steps[1][args.green]
    print(f'Blue = {steps[0][args.blue]} ({args.blue}%)')
    mcp4728.channel_c.value = steps[2][args.blue]
    print(f'UV = {steps[0][args.uv]} ({args.uv}%)')
    mcp4728.channel_d.value = steps[3][args.uv]
    
    print(f'PWM = {steps[4][args.pwm]}ns on of {BB_PER}ns period ({args.pwm}%)')
    os.system(f'echo {steps[4][args.pwm]} >> {PWM_PATH}/duty_cycle')
except Exception as e:
    print(e)
    print('Failed to set light levels')
    