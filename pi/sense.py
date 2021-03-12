"""
    Senses environment
"""

#Import libraries
import sys
import time
import thingspeak
import datetime
import csv
import Adafruit_DHT
import pandas
from sps30 import SPS30
from time import sleep
from urllib.request import urlopen

#Constants
DHT_PIN = 4
CLEANING_INTERVAL = 0

#Initialize sensors
dht = Adafruit_DHT.DHT22
sps = SPS30(1)

#Turn off auto cleaning
sps.set_auto_cleaning_interval(CLEANING_INTERVAL) 

#Current date
today = datetime.datetime.now().strftime("%Y-%m-%d")
now = datetime.datetime.now().strftime("%H:%M:%S")

#DHT measurements
humidity, temperature = Adafruit_DHT.read_retry(dht, DHT_PIN)

#SPS measurements
sps.start_measurement()

while not sps.read_data_ready_flag():
    sleep(0.25)
    if sps.read_data_ready_flag() == sps.DATA_READY_FLAG_ERROR:
        raise Exception("DATA-READY FLAG CRC ERROR!")

if sps.read_measured_values() == sps.MEASURED_VALUES_ERROR:
    raise Exception("MEASURED VALUES CRC ERROR!")
else:
    print("PM1.0 Value in µg/m3: " + str(sps.dict_values['pm1p0']))
    pm1 = str(sps.dict_values['pm1p0'])
    print("PM2.5 Value in µg/m3: " + str(sps.dict_values['pm2p5']))
    pm25 = str(sps.dict_values['pm2p5'])
    print("PM10.0 Value in µg/m3: " + str(sps.dict_values['pm2p5']))
    pm10 = str(sps.dict_values['pm2p5'])

sps.stop_measurement()


with open('/home/pi/readings.csv', 'a') as readings:
    values = pd.DataFrame( [ [data_now(), time_now(), temperature, humidity, pm1, pm25, pm10] ], col____ )
    write_to_log = values.to_csv('readings.csv', mode='a', index=False, sep=',', header=False)
    


