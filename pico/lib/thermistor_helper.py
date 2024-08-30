# Thermistor conversion helper
import ulab.numpy as np

# Takes a thermistor's voltage and returns it's temperature in Celsius
def getTemp(adc: float) -> float:
	rth = (10000) * (3.3 / adc) - 10000
	therm = 1 / ((np.log(rth/10000) / 3977) + (1/298.15))
	return therm - 273.15