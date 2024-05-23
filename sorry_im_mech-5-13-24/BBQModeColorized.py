# BBQ mode (to simulate a spinning satellite) NOW COLORIZED
# Import dependencies
from ulab import numpy as np
import adafruit_mcp4728 as MCP  # 12-bit DAC
from time import sleep
import digitalio as dio
import pwmio
import board
import busio

# Serial console logging settings
SERIAL_LOG  = False
PORT_SCAN = False

# Light step calculations
MAX_VALUE = 65535
PWM_FREQ = 50000
LIMITER = 1

# Set the debug LED
led = dio.DigitalInOut(board.LED)
led.direction = dio.Direction.OUTPUT
led.value = True

# Set the PWM pinout
halogen = pwmio.PWMOut(board.GP28, frequency=PWM_FREQ, duty_cycle=0)

# Init I2C and scan for ports
i2c = busio.I2C(board.GP27, board.GP26)

# Init I2C devices
mcp = MCP.MCP4728(i2c) # Default address = 0x60
print("MCP4728 initialized, running sine dimming")

def setLEDs(r: int = 0, g: int = 0, b: int = 0, u: int = 0, h: int = 0) -> None:
    # Set the value of the R, G, B, UV, and Halogen lights (docs coming soon :tm:)
    mcp.channel_a.value = r
    mcp.channel_b.value = g
    mcp.channel_c.value = b
    mcp.channel_d.value = u
    halogen.duty_cycle  = h

def calcSteps(LIMITER: float) -> list:
    # Calculate the interpolation steps from a set intensity limiter (docs coming soon :tm:)
    red_min = 10756
    grn_min = 10140
    blu_min = 10620
    uv_min  = 10620
    pwm_min = 0
    red_max = int(MAX_VALUE * LIMITER)
    grn_max = int(MAX_VALUE * LIMITER)
    blu_max = int(MAX_VALUE * LIMITER)
    uv_max  = int(MAX_VALUE * LIMITER)
    pwm_max = int(LIMITER * MAX_VALUE * .5) # KEEP .5 MULTIPLIER UNTIL BETTER POWER SUPPLY IS USED; DRAWS TOO MUCH POWER OTHERWISE

    # Calculate steps between minimum and maximum values
    red_steps = [31268, 64839, 65387, 399, 947, 1494, 2042, 2590, 3138, 3686, 4233, 4781, 5329, 5877, 6425, 6972, 7520, 8068, 8616, 9164, 9711, 10259, 10807, 11355, 11902, 12450, 12998, 13546, 14094, 14641, 15189, 15737, 16285, 16833, 17380, 17928, 18476, 19024, 19572, 20119, 20667, 21215, 21763, 22310, 22858, 23406, 23954, 24502, 25049, 25597, 26145, 26693, 27241, 27788, 28336, 28884, 29432, 29980, 30527, 31075, 31623, 32171, 32718, 33266, 33814, 34362, 34910, 35457, 36005, 36553, 37101, 37649, 38196, 38744, 39292, 39840, 40388, 40935, 41483, 42031, 42579, 43126, 43674, 44222, 44770, 45318, 45865, 46413, 46961, 47509, 48057, 48604, 49152, 49700, 50248, 50796, 51343, 51891, 52439, 52987, 53535]
    grn_steps = [35864, 5789, 6343, 6897, 7451, 8005, 8559, 9113, 9667, 10221, 10775, 11329, 11883, 12437, 12991, 13545, 14099, 14653, 15207, 15761, 16315, 16868, 17422, 17976, 18530, 19084, 19638, 20192, 20746, 21300, 21854, 22408, 22962, 23516, 24070, 24624, 25178, 25732, 26286, 26840, 27394, 27947, 28501, 29055, 29609, 30163, 30717, 31271, 31825, 32379, 32933, 33487, 34041, 34595, 35149, 35703, 36257, 36811, 37365, 37919, 38473, 39026, 39580, 40134, 40688, 41242, 41796, 42350, 42904, 43458, 44012, 44566, 45120, 45674, 46228, 46782, 47336, 47890, 48444, 48998, 49552, 50105, 50659, 51213, 51767, 52321, 52875, 53429, 53983, 54537, 55091, 55645, 56199, 56753, 57307, 57861, 58415, 58969, 59523, 60077, 60631]
    blu_steps = [30044, 54913, 55462, 56011, 56560, 57109, 57658, 58208, 58757, 59306, 59855, 60404, 60953, 61502, 62052, 62601, 63150, 63699, 64248, 64797, 65347, 360, 909, 1458, 2007, 2556, 3105, 3655, 4204, 4753, 5302, 5851, 6400, 6949, 7499, 8048, 8597, 9146, 9695, 10244, 10794, 11343, 11892, 12441, 12990, 13539, 14088, 14638, 15187, 15736, 16285, 16834, 17383, 17932, 18482, 19031, 19580, 20129, 20678, 21227, 21777, 22326, 22875, 23424, 23973, 24522, 25071, 25621, 26170, 26719, 27268, 27817, 28366, 28915, 29465, 30014, 30563, 31112, 31661, 32210, 32760, 33309, 33858, 34407, 34956, 35505, 36054, 36604, 37153, 37702, 38251, 38800, 39349, 39898, 40448, 40997, 41546, 42095, 42644, 43193, 43743]
    pwm_steps = [24525, 24852, 29547, 29875, 30202, 30530, 30858, 31185, 31513, 31841, 32168, 32496, 32824, 33151, 33479, 33807, 34134, 34462, 34790, 35117, 35445, 35773, 36100, 36428, 36756, 37083, 37411, 37739, 38066, 38394, 38722, 39049, 39377, 39705, 40032, 40360, 40688, 41015, 41343, 41671, 41998, 42326, 42654, 42981, 43309, 43637, 43964, 44292, 44620, 44947, 45275, 45603, 45930, 46258, 46586, 46913, 47241, 47569, 47896, 48224, 48552, 48879, 49207, 49535, 49862, 50190, 50518, 50845, 51173, 51501, 51828, 52156, 52484, 52811, 53139, 53467, 53794, 54122, 54450, 54777, 55105, 55433, 55760, 56088, 56416, 56743, 57071, 57399, 57726, 58054, 58382, 58709, 59037, 59365, 59692, 60020, 60348, 60675, 61003, 61331, 61659]
    uv_steps  = np.linspace( uv_min,  uv_max, num=101, dtype=np.uint16)
    return [red_steps, grn_steps, blu_steps, uv_steps, pwm_steps]

# Calculate steps
steps = calcSteps(LIMITER)

level = 0
intensity = 0
wave = np.sin(np.linspace(0, np.pi, 360))

# Reset any active lights
setLEDs()
led.value = False

while True:
    # Calculate a 0-100 value from the wave
    intensity = int(100*wave[level])

    print(intensity)
    # Gets LED brightness values at the appropriate level
    # From Charlene: Did some testing and calibration and looks like 80 is a magic number where
    # hal seemed to occupy most of the high spectrum, and blue was able to cover all of the bottom spectrum
    if intensity < 80:
        red = steps[0][0]
        grn = steps[1][0]
        blu = steps[2][0]
        uv  = steps[3][intensity]
        hal = steps[4][int(intensity)]
        #hal = steps[4][int(intensity/2.1)]
    if (intensity == 80 or intensity > 80):
        red = 0
        grn = 0
        blu = steps[2][100]
        uv  = steps[3][intensity]
        hal = steps[4][int(intensity)]

    # Set LEDs and bulbs
    uv = 0 # Disable UV for safety
    setLEDs(red,grn,blu,uv,hal)

    if SERIAL_LOG: print(f"Intensity: {intensity}, Level: {level}")

    # Increment and overflow the level every iteration
    level += 1
    if level > len(wave)-1: level = 0
    sleep(0.1)
