#!/usr/bin/python
from sense_hat import SenseHat
import time
import sys
import csv
from datetime import datetime

sense = SenseHat()
sense.clear()
thetimestamp = datetime.now()
delay = 60

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
        sense.show_message("Temperature:  " + str(fahrenheit - 3) 
            + "Humidity:  " + str(humidity), 
            scroll_speed=(0.08), 
            back_colour= [0,0,200])
except KeyboardInterrupt:
      pass

def get_sense_data():
    sense_data = []
    sense_data.append(fahrenheit)
    sense_data.append(humidity)
    sense_data.append(pressure)
    sense_data.append(datetime.now())
    return sense_data

with open('temp.csv', 'w', newline='') as f:
    dwriter = csv.writer(f)
    dwriter.writerow(['temp', 'humidity', 'pressure', 'time'])
    while True:
        data = get_sense_data()
        dt = data[-1] - thetimestamp
        if dt.seconds > delay:
            dwriter.writerow(data)
            thetimestamp = datetime.now()


