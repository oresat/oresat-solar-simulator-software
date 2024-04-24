<p style="color: red; font-weight: bold">>>>>>  gd2md-html alert:  ERRORs: 0; WARNINGs: 2; ALERTS: 3.</p>
<ul style="color: red; font-weight: bold"><li>See top comment block for details on ERRORs and WARNINGs. <li>In the converted Markdown or HTML, search for inline alerts that start with >>>>>  gd2md-html alert:  for specific instances that need correction.</ul>

<p style="color: red; font-weight: bold">Links to alert messages:</p><a href="#gdcalert1">alert1</a>
<a href="#gdcalert2">alert2</a>
<a href="#gdcalert3">alert3</a>

<p style="color: red; font-weight: bold">>>>>> PLEASE check and correct alert issues and delete this message and the inline alerts.<hr></p>



# Thermistor Temperature Measurement

The OreSat live / DxWiFi Card has an NTC thermistor on it. How do we use that?


# The Sensor

We’re using the [Murata NXFT15XV103FEAB050](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5339/NXFT15XV103FEAB050_DS.pdf) (Digi-Key 490-NXFT15XV103FEAB050-ND) 10 kΩ ± 1% leaded bead Negative Temperature Coefficient (NTC) thermistor rated -40 to 125 °C. ꞵ , or just “B” value is  B25/85 = 3977 K ± 1%. Digi-Key also has B25/50 = 3936 K, but not sure where that came from and we can ignore it.


# The Schematic



<p id="gdcalert1" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image1.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert2">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image1.png "image_tooltip")


That’s just a voltage divider with our thermistor in the “R1” spot, so:

V<sub>OUT</sub> = (R<sub>2</sub> / (R<sub>TH</sub> + R<sub>2</sub>))V<sub>IN</sub>

V<sub>OUT</sub> = (10k/(R<sub>TH<sup> </sup></sub>+ 10k)) * 3.3 V

The reference to the ADC is the 3.3V analog supply.


# First, Find the Thermistor’s Resistance

First take the ADC reading. This gives a voltage. From that voltage, we can calculate R<sub>TH</sub>.

V<sub>OUT</sub> = (R<sub>2</sub> / (R<sub>TH</sub> + R<sub>2</sub>))V<sub>IN</sub>

V<sub>OUT</sub> = (10k/(R<sub>TH<sup> </sup></sub>+ 10k)) * 3.3 V

Solving for R<sub>TH</sub>, 

R<sub>TH</sub> = V<sub>OUT</sub> * R / (V<sub>IN</sub> - V<sub>OUT</sub>)

**R<sub>TH</sub> = V<sub>ADC</sub> * 10000 Ω / (1.8V - V<sub>ADC</sub>)                        [1]**

That last equation is all we really need, and implementing it should be pretty straight forward. The outcome is the resistance in ohms.


# Second, Find the Temperature

Now we convert R<sub>TH</sub> to a temperature, which is a bit trickier. Taken from [NTC Thermistors: General technical information](https://www.tdk-electronics.tdk.com/download/531116/19643b7ea798d7c4670141a88cd993f9/pdf-general-technical-information.pdf): 



<p id="gdcalert2" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: equation: use MathJax/LaTeX if your publishing platform supports it. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert3">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>



Here:



* R<sub>T</sub> = Resistance in Ω at current Temperature in K ( Kelvin!)
* R<sub>R</sub> = Resistance in Ω at rated temperature T<sub>R</sub> in K, in our case, 10 kΩ
* T = current temperature in K
* T<sub>R</sub> = rated temperature in K, in our case 25 °C = 298.15 K
* B = B value in K, Datasheet says “B25/85 = 3435K”, so that’s at T1 = 25 C and T2 = 85 C

So in our case:

R<sub>T</sub> = 10 kΩ * e^(3435 K * (1 / T - 1 / 298.15 K))

Well calculating R<sub>T</sub> based on T is exactly the opposite of what we want, so now solve that equation for T. That’s handily done on [this website](https://www.giangrandi.org/electronics/ntc/ntc.shtml), including calculators to check your work.



<p id="gdcalert3" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: equation: use MathJax/LaTeX if your publishing platform supports it. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert4">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>



Plugging in our standard values and using R<sub>TH</sub> calculated from [1] above:

**T = 1 / ( (ln (R<sub>TH</sub> / 10000 Ω) / 3435 K ) + (1 / 298.15 K)                [2]**

That’s in Kelvin, so subtract 273.15 to get that in ° C.
