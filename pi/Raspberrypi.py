
import sys
import time
import thingspeak
import datetime
import csv
import Adafruit_DHT
from sps30 import sps30
from time import sleep
from urllib.request import urlopen


sensor = Adafruit_DHT.DHT22

# Set to your GPIO pin
pin = 4 #or 7 

sps = SPS30(1)
seconds = 0


humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)


def get_temp():
    temp = round((temperature), 2)
    temp = str(temp)
    return(temp)

def get_hum():
    hum = round( (humidity), 2)
    hum = str(hum)
    return(hum)


print('Temperature in Celcius: ', get_temp() )
print('Humidity in %:', get_hum() )


if sps.read_article_code() == sps.ARTICLE_CODE_ERROR:
    raise Exception("ARTICLE CODE CRC ERROR!")
else:
    print( "ARTICLE CODE: " + str(sps.read_article_code() ) )

if sps.read_device_serial() == sps.SERIAL_NUMBER_ERROR:
    raise Exception("SERIAL NUMBER CRC ERROR!")
else:
    print("DEVICE SERIAL: " + str(sps.read_device_serial() ))

sps.set_auto_cleaning_interval(seconds) # default 604800, set 0 to disable auto-cleaning

sps.device_reset() # device ahs to be powered-down or reset to check new auto-cleaning interval

if sps.read_auto_cleaning_interval() == sps.AUTO_CLN_INTERVAL_ERROR:
    raise Exception("AUTO-CLEANING INTERVAL CRC ERROR!")
else:
    print("AUTO-CLEANING INTERVAL: " + str(sps.read_auto_cleaning_interval() ))


sps.start_measurement()

while not sps.read_data_ready_flag():
    sleep(0.25)
    if sps.read_data_ready_flag() == sps.DATA_READY_FLAG_ERROR:
        raise Exception("DATA-READY FLAG CRC ERROR!")

if sps.read_measured_values() == sps.MEASURED_VALUES_ERROR:
    raise Exception("MEASURED VALUES CRC ERROR!")
else:
    print("PM1.0 Value in µg/m3: " + str(sps.dict_values['pm1p0']))
    print("PM2.5 Value in µg/m3: " + str(sps.dict_values['pm2p5']))
    #print("PM4.0 Value in µg/m3: " + str(sps.dict_values['pm4p0']))
    print("PM10.0 Value in µg/m3: " + str(sps.dict_values['pm10p0']))

sps.stop_measurement()

sps.start_fan_cleaning()


def get_pml():
    variable = "pml"
    unit = "ug/m3"
    data = sps.dict_values['pm1p0']
    data = round( (data), 2)
    return(data)

def get_pm25():
    variable = "pm25"
    unit = "ug/m3"
    data = sps.dict_values['pm2p5']
    data = round( (data), 2)
    return(data)

def get_pm10():
    variable = "pm25"
    unit = "ug/m3"
    data = sps.dict_values['pm2p5']
    data = round( (data), 2)
    return(data)

def date_now():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today = str(today)
    return(today)

def time_now():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    now - str(now)
    return(now)


# Thingspeak connection
# TODO
# myAPI = ''
# baseURL = 'https:'


f = urlopen(baseURL + ) # TODO
f.read()
f.close()


import pandas as pd


def write_to_csv():
    # a is for append, if w for write is used then it overwrites the file
    with open('/home/pi/readings.csv', 'a') as readings:
        values = pd.DataFrame( [ [data_now(), time_now(), get_temp(), get_hum(), get_pm1(), get_pm25(), get_pm10()] ], columns = ('Date', 'Time', 'Temperature', 'Humidity', 'PM1.0', 'PM2.5', 'PM10.0')) 
        write_to_log = values.to_csv('readings.csv', mode='a', index=False, sep=',', header=False)
        return(write_to_log)

write_to_csv()

