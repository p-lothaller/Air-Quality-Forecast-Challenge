import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.cluster import DBSCAN
import numpy as np

#Read in csv file

raw_data = pd.read_csv('airdata_raw.csv',  index_col=False)
raw_data = raw_data.dropna()

#add data that needs to be analysed
analyse_data = ['PM2.5', 'PM10', 'hum']

#Print Statistical Data about selected data to analyse

# for data in analyse_data:
#     print(raw_data[data].describe())

#Time series visualization

# for data in analyse_data:
#    raw_data.plot(x='time', y=data, figsize=(12,6))
#    plt.xlabel('Date time')
#    plt.ylabel(data)
#    plt.title('Time Series of' + data)
#    plt.show()


clustering1 = DBSCAN(eps=0.5, min_samples=4).fit(np.array(raw_data['PM2.5']).reshape(-1,1))
labels = clustering1.labels_
outlier_pos = np.where(labels == -1)[0]

x = []
y = []
for pos in outlier_pos:
    x.append(np.array(raw_data['PM2.5'])[pos])
    y.append(raw_data['PM2.5'].index[pos])

raw_data.plot(x='time', y='PM2.5', figsize=(12,6))
plt.plot(y,x,'r*', markersize=8)
plt.xlabel('Date time')

#plt.title('Time Series of' + data)
plt.show()