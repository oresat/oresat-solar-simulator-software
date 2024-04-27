# Thermistor Temperature Measurement

The OreSat live / DxWiFi Card has an NTC thermistor on it. How do we use that? In this guide, you'll learn the math behind reading temperature from thermocouples.

## The Sensor

We’re using the [Murata NXFT15XV103FEAB050 thermistor](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5339/NXFT15XV103FEAB050_DS.pdf) rated -40 to 125 °C. ꞵ, or just “B” value is  B25/85 = 3977 K ± 1%. Digi-Key also has B25/50 = 3936 K, but not sure where that came from and we can ignore it.

## The Schematic

![circuit schematic](images/image1.png)

That’s just a voltage divider with our thermistor in the “R1” spot, so:

$V_{OUT} = (R_2 / (R_{TH} + R_2))V_{IN}$

$V_{OUT} = (10000/(R_{TH} + 10000)) * 3.3V$

The reference to the ADC is the 3.3V analog supply.

## Find the Thermistor’s Resistance

First take the ADC reading. This gives a voltage. From that voltage, we can calculate $R_{TH}$.

$V_{OUT} = (R_2 / (R_{TH} + R_2)) * V_{IN}$

$V_{OUT} = (10000{\Omega} / (R_{TH} + 10000{\Omega})) * 3.3V$

### Solving for $R_{TH}$

$R_{TH} = V_{OUT} * R / (V_{IN} - V_{OUT})$

$R_{TH} = V_{ADC} * 10000{\Omega} / (1.8V - V_{ADC}) [1]$

That last equation is all we really need, and implementing it should be pretty straight forward. The outcome is the resistance in ohms.

# Second, Find the Temperature

Now we convert $R_{TH}$ to a temperature, which is a bit trickier. Taken from [NTC Thermistors: General technical information](https://www.tdk-electronics.tdk.com/download/531116/19643b7ea798d7c4670141a88cd993f9/pdf-general-technical-information.pdf):

Here:

* $R_T$ = Resistance in ${\Omega}$ at current Temperature in K ( Kelvin!)
* $R_R$ = Resistance in ${\Omega}$ at rated temperature $T_R$ in K, in our case, 10k${\Omega}$
* $T$ = current temperature in K
* $T_R$ = rated temperature in K, in our case 25°C = 298.15 K
* $B$ = B value in K, Datasheet says “B25/85 = 3435K”, so that’s at $T_1$ = 25°C and $T_2$ = 85°C

So in our case:

$R_T = 10000{\Omega} * e^{(3435 K * (1 / T - 1 / 298.15 K))}$

Well calculating $R_T$ based on $T$ is exactly the opposite of what we want, so now solve that equation for $T$. That’s handily done on [this website](https://www.giangrandi.org/electronics/ntc/ntc.shtml), including calculators to check your work.

Plugging in our standard values and using $R_{TH}$ calculated from [1] above:

$T = 1 / (({\log}(R_{TH} / 10000{\Omega}) / 3435K) + (1 / 298.15 K)) [2]$

That’s in Kelvin, so subtract 273.15 to get that in °C.
