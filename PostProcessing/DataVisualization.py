import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def remove_entry(x_vector,y_vector):

    for k in range(len(y_vector)):
        if y_vector[k] == 'N/A':
            y_vector.pop(k)
            x_vector.pop(k)

    return x_vector, y_vector

# def plotting(x_vector_raw, y_vector_raw, x_vector, y_vector):
#
#     plt.plot(x_vector_raw, y_vector_raw)
#     plt.plot(x_vector, y_vector)
#     return plt





#edit heading names of WeatherData file to match those of the airdata_raw file

col_names = ['location',
             'date',
             'time',
             'weather',
             'temp',
             'hum',
             'wind',
             'pressure',
             'PM2.5',
             'PM10',
             'AQI']

#Read in csv files

raw_data = pd.read_csv('airdata_raw.csv',  index_col=False)
scraped_data = pd.read_csv('WeatherData.csv', names=col_names, skiprows=[0],  index_col=False)

#Adjust date and time formats from airdata_raw CSV

raw_adj_time = []
raw_time_array = raw_data['time'].to_numpy()

for i in range(len(raw_time_array)):
    date_input = raw_time_array[i]
    raw_date_time_str = date_input[0:19]
    raw_adj_time.append(datetime.strptime(raw_date_time_str, '%Y-%m-%d %H:%M:%S'))

# Add to raw_data dataframe
raw_data['raw_time_adjust'] = raw_adj_time

#Adjust date and time formats from WeatherData CSV

adj_time = []
date_array = scraped_data['date'].to_numpy()
time_array = scraped_data['time'].to_numpy()

for j in range(len(date_array)):
    date_input = date_array[j]
    datetimeobject = datetime.strptime(date_input, '%d/%m/%Y')
    new_format = datetimeobject.strftime('%Y-%m-%d')
    date_time_str = new_format + ' ' + time_array[j]
    adj_time.append(datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S'))

#Add to scraped_data dataframe
scraped_data['time_adjust'] = adj_time

#-----------------------------------------
#Plotting
#-----------------------------------------

#Plotting humidity values
x_raw_hum = raw_data['raw_time_adjust']
hum_raw = raw_data['hum']

x_scrape_hum = scraped_data['time_adjust']
hum_scrape = scraped_data['hum']

#Remove N/A data points from web scrapped data
x_scrape_hum, hum_scrape = remove_entry(x_scrape_hum, hum_scrape)

plt.plot(x_raw_hum, hum_raw)
plt.plot(x_scrape_hum, hum_scrape)
plt.show()

#Plotting PM2.5 values
x_raw_pm25 = raw_data['raw_time_adjust']
pm25_raw = raw_data['PM2.5']

x_scrape_pm25 = scraped_data['time_adjust']
pm25_scrape = scraped_data['PM2.5']

#Remove N/A data points from web scrapped data
x_scrape_pm25, pm25_scrape = remove_entry(x_scrape_pm25, pm25_scrape)

plt.plot(x_raw_pm25, pm25_raw)
plt.plot(x_scrape_pm25, pm25_scrape)
plt.show()

#Plotting PM10 values
x_raw_pm10 = raw_data['raw_time_adjust']
pm10_raw = raw_data['PM10']

x_scrape_pm10 = scraped_data['time_adjust']
pm10_scrape = scraped_data['PM10']

#Remove N/A data points from web scrapped data
x_scrape_pm10, pm10_scrape = remove_entry(x_scrape_pm10, pm10_scrape)

plt.plot(x_raw_pm10, pm10_raw)
plt.plot(x_scrape_pm10, pm10_scrape)
plt.show()

