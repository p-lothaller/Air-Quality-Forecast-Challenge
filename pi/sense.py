"""
    Script to gather data from the environment and write to csv file
"""

#Import libraries
import sys
import thingspeak
import datetime
import csv
import Adafruit_DHT
import board
import pandas as pd
from sps30 import SPS30
from time import sleep
from urllib.request import urlopen
import requests

#Constants
DHT_PIN = 4
CLEANING_INTERVAL = 86401

# Insert ThingSpeak credentials
CHANNEL_ID = 1325943
baseURL = 'https://api.thingspeak.com/update?api_key=HOIPBDMHZBJSNUGY&field1=0'
READ_KEY = "B29JUCAR7UY5WYY6"
WRITE_KEY = "H0IPBDMHZBJSNUGY"

#Current date
date = datetime.datetime.now().strftime("%Y-%m-%d")
time = datetime.datetime.now().strftime("%H:%M:%S")

#Initialize sensors
dht = Adafruit_DHT.DHT22
sps = SPS30(1)

#DHT measurements
humidity, temperature = Adafruit_DHT.read_retry(dht, DHT_PIN)
print("Temperature: {}".format(temperature))
print("Humidity: {}".format(humidity))

#Check SPS status
if sps.read_article_code() == sps.ARTICLE_CODE_ERROR:
    raise Exception("ARTICLE CODE CRC ERROR!")
else:
    print( "ARTICLE CODE: " + str(sps.read_article_code()))

if sps.read_device_serial() == sps.SERIAL_NUMBER_ERROR:
    raise Exception("SERIAL NUMBER CRC ERROR!")
else:
    print("DEVICE SERIAL: " + str(sps.read_device_serial()))

#Turn off auto cleaning
sps.set_auto_cleaning_interval(CLEANING_INTERVAL)
sps.device_reset()

if sps.read_auto_cleaning_interval() == sps.AUTO_CLN_INTERVAL_ERROR:
    raise Exception("AUTO-CLEANING INTERVAL CRC ERROR!")
else:
    print("AUTO-CLEANING INTERVAL: " + str(sps.read_auto_cleaning_interval()))

#SPS measurements
sleep(2)
sps.start_measurement()
sleep(2)

while not sps.read_data_ready_flag():
    print("New Measurement is not available!")
    if sps.read_data_ready_flag() == sps.DATA_READY_FLAG_ERROR:
        raise Exception("DATA-READY FLAG CRC ERROR!")

#if sps.dict_values['pm1p0'] == None or sps.read_measured_values() == sps.MEASURED_VALUES_ERROR:
if sps.read_measured_values() == sps.MEASURED_VALUES_ERROR:
    raise Exception("MEASURED VALUES CRC ERROR!")
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
sps.start_fan_cleaning()

#Write to csv file
with open('/home/pi/readings.csv', 'a') as readings:
    values = pd.DataFrame( [ [date, time, temperature, humidity, pm1, pm25, pm10] ], columns = ('Date', 'Time', 'Temperature', 'Humidity', 'PM1.0', 'PM2.5', 'PM10.0') )
    write_to_log = values.to_csv('readings.csv', mode='a', index=False, sep=',', header=False)


# Prepare data for ThingSpeak
def get_temp():
    temp = round((temperature),2)
    temp = str(temp)
    return(temp)

def get_hum():
    hum = round((humidity),2)
    hum = str(hum)
    return (hum)

def get_pm1():
    variable = "pm1"
    unit = "ug/m3"
    data = sps.dict_values['pm1p0']
    data = round((data),2)
    return(data)

def get_pm25():
    variable = "pm25"
    unit = "ug/m3"
    data = sps.dict_values['pm2p5']
    data = round((data),2)
    return(data)

def get_pm10():
    variable = "pm10"
    unit = "ug/m3"
    data = sps.dict_values['pm10p0']
    data = round((data),2)
    return(data)

def date_now():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today = str(today)
    return(today)

def time_now():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    now = str(now)
    return(now)

f = urlopen(baseURL + '&field1=%s&field2=%s&field3=%s&field4=%s&field5=%s' % (get_temp(), get_hum(), get_pm1(), get_pm25(), get_pm10()))
f.read()
f.close()
