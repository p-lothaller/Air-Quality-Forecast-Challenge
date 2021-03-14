"""
    Script to gather data from the environment and write to csv file
"""

#Import libraries
import sys
import time
import thingspeak
import datetime
#import csv
import Adafruit_DHT
import board
import pandas as pd
from sps30 import SPS30
from time import sleep
#from urllib.request import urlopen
import requests

#Constants
DHT_PIN = 4
CLEANING_INTERVAL = 0
#TODO: Insert credentials
CHANNEL_ID = 1325943
READ_KEY = "B29JUCAR7UY5WYY6"
WRITE_KEY = "H0IPBDMHZBJSNUGY"

#Initialize sensors
dht = Adafruit_DHT.DHT22
sps = SPS30(1)

#Turn off auto cleaning
sps.set_auto_cleaning_interval(CLEANING_INTERVAL) 

#Current date
date = datetime.datetime.now().strftime("%Y-%m-%d")
time = datetime.datetime.now().strftime("%H:%M:%S")

#DHT measurements
humidity, temperature = Adafruit_DHT.read_retry(dht, DHT_PIN)
print("Humidity: {}".format(humidity))
print("Temperature: {}".format(temperature))

#Check SPS status
if sps.read_article_code() == sps.ARTICLE_CODE_ERROR:
    raise Exception("ARTICLE CODE CRC ERROR!")
else:
    print( "ARTICLE CODE: " + str(sps.read_article_code() ) )

if sps.read_device_serial() == sps.SERIAL_NUMBER_ERROR:
    raise Exception("SERIAL NUMBER CRC ERROR!")
else:
    print("DEVICE SERIAL: " + str(sps.read_device_serial() ))

#SPS measurements
sps.device_reset()
sleep(0.25)
sps.start_measurement()

while not sps.read_data_ready_flag():
    sleep(0.25)
    if sps.read_data_ready_flag() == sps.DATA_READY_FLAG_ERROR:
        raise Exception("DATA-READY FLAG CRC ERROR!")

if sps.dict_values['pm1p0'] == None or sps.read_measured_values() == sps.MEASURED_VALUES_ERROR:
    sps.stop_measurement()
    pm1 = 0
    pm25 = 0
    pm10 = 0
    print(sps.dict_values)
else:
	print("PM1.0 Value in µg/m3: " + str(sps.dict_values['pm1p0']))
	pm1 = str(sps.dict_values['pm1p0'])
	print("PM2.5 Value in µg/m3: " + str(sps.dict_values['pm2p5']))
	pm25 = str(sps.dict_values['pm2p5'])
	print("PM10.0 Value in µg/m3: " + str(sps.dict_values['pm2p5']))
	pm10 = str(sps.dict_values['pm2p5'])
	print(sps.dict_values)

sps.stop_measurement()

#Write to csv file
with open('/home/pi/readings.csv', 'a') as readings:
    values = pd.DataFrame( [ [date, time, temperature, humidity, pm1, pm25, pm10] ], columns = ('Date', 'Time', 'Temperature', 'Humidity', 'PM1.0', 'PM2.5', 'PM10.0') )
    write_to_log = values.to_csv('readings.csv', mode='a', index=False, sep=',', header=False)
    

#Send data to Thingspeak
#r = requests.get('https://api.thinkspeak.com/update?api_key=' + WRITE_KEY + '&field1=' + str(temperature) + '&field2=' + str(humidity) + '&field3=' + str(pm1) + '&field4' + str(pm25) + '&field5' + str(pm10) )
#channel = thingspeak.Channel(id=CHANNEL_ID, api_key=WRITE_KEY)
#channel.update({'field1': temperature, 'field2': humidity, 'field3': pm1, 'field4': pm25, 'field5': pm10})

#print("Could not send data")
