# Write your code here :-)

global system_state = 1
global BB_PER = 4000 # what is BB_PER ??? it was from sample code
global limiter = 0.3
global level = 100


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
    red_max = int(65535 * limiter)
    grn_max = int(65535 * limiter)
    blu_max = int(65535 * limiter)
    UV_max  = int(65535 * limiter)
    PWM_max = int(75 * limiter * BB_PER / 100)
    red_steps = linspace(red_start, red_max, num=101, dtype=uint16)
    grn_steps = linspace(grn_start, grn_max, num=101, dtype=uint16)
    blu_steps = linspace(blu_start, blu_max, num=101, dtype=uint16)
    PWM_steps = linspace(PWM_start, PWM_max, num=101, dtype=uint16)
    if system_state == 2:
        UV_steps = [0] * 101
    else:
        UV_steps = linspace(UV_start, UV_max, num=101, dtype=uint16)
    return [red_steps, grn_steps, blu_steps, UV_steps, PWM_steps]

mcp4728.channel_a.value = steps[0][level]
mcp4728.channel_b.value = steps[1][level]
mcp4728.channel_c.value = steps[2][level]
mcp4728.channel_d.value = steps[3][level]

