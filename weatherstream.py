#!/usr/bin/python
from sense_hat import SenseHat
import time
import sys

sense = SenseHat()
sense.clear()

try:
      while True:
        temp = sense.get_temperature()
        celcius = round(temp, 1)
        fahrenheit = 1.8 * round(temp, 1)  + 32 
        humidity = sense.get_humidity()  
        humidity = round(humidity, 1)  
        pressure = sense.get_pressure()
        pressure = round(pressure, 1)
        time.sleep(1)
        sense.show_message("Temperature C" + str(temp) 
            + "Humidity:" + str(humidity) 
            + "Pressure:" + str(pressure), 
            scroll_speed=(0.08), 
            back_colour= [0,0,200])
except KeyboardInterrupt:
      pass
