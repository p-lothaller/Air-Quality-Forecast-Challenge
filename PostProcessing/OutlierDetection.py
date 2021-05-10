import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import numpy as np
from kneed import KneeLocator
import matplotlib as mpl
from sklearn.metrics import mean_absolute_error
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
#import plottools

from matplotlib.dates import DateFormatter
from pandas.plotting import autocorrelation_plot
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.tsa.stattools import adfuller

sns.set()
sns.set_style("whitegrid")
mpl.use('TkAgg')

def difference(dataset, interval=1):
	diff = list()
	for i in range(interval, len(dataset)):
		value = dataset[i] - dataset[i - interval]
		diff.append(value)
	return diff

# Read in csv file


raw_data = pd.read_csv('airdata_all.csv', index_col=False)
raw_data = raw_data.dropna()

# Print Statistical Data about selected data to analyse

# for data in analyse_data:
#     print(raw_data[data].describe())


# add data that needs to be analysed
analyse_data = ['PM2.5']
# analyse_data = ['PM1', 'PM2.5', 'PM10', 'hum']

for data in analyse_data:


    # ax = raw_data[[data]].plot(linewidth=2, figsize=(12, 6), alpha=0.8)
    # plt.xlabel('Data points')
    # plt.ylabel(data + ' concentration (µg/m³)')
    # plt.title('Raw ' + data + ' Data')
    # plt.show()

    # create upper and lower bounds using a exponetial moving average and confidence intervals

    raw_data['EMA_0.1-' + data] = raw_data[data].ewm(alpha=0.1, adjust=False).mean()

    mae = mean_absolute_error(raw_data[data], raw_data['EMA_0.1-' + data])
    deviation = np.std(raw_data[data] - raw_data['EMA_0.1-' + data])
    raw_data['upper_bound'] = raw_data['EMA_0.1-' + data] + (mae + 1.96 * deviation)
    raw_data['lower_bound'] = raw_data['EMA_0.1-' + data] - (mae + 1.96 * deviation)

    # identifying outliers:

    upper_outliers = np.array(raw_data[data] > raw_data['upper_bound'])
    lower_outliers = np.array(raw_data[data] < raw_data['lower_bound'])

    outlier_pos_ema = []
    for counter in range(len(upper_outliers)):
        if upper_outliers[counter] == True or lower_outliers[counter] == True:
            raw_data['outlier_ema'] = True
            outlier_pos_ema.append(counter)
        else:
            raw_data['outlier_ema'] = False

    x_ema = []
    y_ema = []

    for pos in outlier_pos_ema:
        x_ema.append(np.array(raw_data[data])[pos])
        y_ema.append(raw_data[data].index[pos])

    ax = plt.gca()

    # raw_data[[data, 'EMA_0.1-' + data]].plot(linewidth=2, figsize=(12, 6), alpha=0.8, ax=ax, label='EMA')
    # raw_data[['upper_bound']].plot(linewidth=1, color='red', alpha=0.8, ax=ax, label='Upper bound')
    # raw_data[['lower_bound']].plot(linewidth=1, color='green', alpha=0.8, ax=ax, label='Lower bound')
    # plt.plot(y_ema, x_ema, 'ro', markersize=4, label='Outliers')
    # plt.title('Statistical Outliers')
    # plt.xlabel('Data points')
    # plt.ylabel(data + ' concentration (µg/m³)')
    # plt.legend()
    # plt.show()

    # Identifying outliers using unsupervised machine learning
    # Calculating eps --> this changes depending on the data

    minPts = 4  # For 2D data the default value is a good approximation for the minimum sample points in a cluster (Ester et al., 1996)

    neighbors = NearestNeighbors(n_neighbors=minPts)
    neighbors_fit = neighbors.fit(np.array(raw_data[data]).reshape(-1, 1))
    distances, indices = neighbors_fit.kneighbors(np.array(raw_data[data]).reshape(-1, 1))
    distances = np.sort(distances, axis=0)

    distances = distances[:, 1]
    x = np.linspace(0, len(distances), len(distances))

    # plt.plot(x, distances)
    # plt.xlabel('Data points')
    # plt.ylabel('k-distance')
    # plt.show()
    kn = KneeLocator(x, distances, curve='convex', direction='increasing')
    # kn.plot_knee()
    # plt.show()

    epsilon = kn.elbow_y
    minPts = 4  # For 2D data the default value is a good approximation for the minimum sample points in a cluster (Ester et al., 1996)

    clustering1 = DBSCAN(eps=epsilon, min_samples=minPts).fit(np.array(raw_data[data]).reshape(-1, 1))
    labels = clustering1.labels_
    outlier_pos_DBSCAN = np.where(labels == -1)[0]

    # Creating new entry for outlier tracking
    for counter in range(len(raw_data[data])):
        if counter in outlier_pos_DBSCAN:
            raw_data['outlier_DBSCAN'] = True
        else:
            raw_data['outlier_DBSCAN'] = False

    x_DBSCAN = []
    y_DBSCAN = []
    for pos in outlier_pos_DBSCAN:
        x_DBSCAN.append(np.array(raw_data[data])[pos])
        y_DBSCAN.append(raw_data[data].index[pos])

    # raw_data[[data]].plot(linewidth=2, figsize=(12, 6), alpha=0.8)
    # plt.plot(y_DBSCAN, x_DBSCAN, 'ro', markersize=4, label='Outliers')
    # plt.title('DBSCAN Outliers')
    # plt.xlabel('Data points')
    # plt.ylabel(data + ' concentration (µg/m³)')
    # plt.legend()
    # plt.show()

    outlier_pos = sorted(set(outlier_pos_ema).intersection(outlier_pos_DBSCAN))
    x = []
    y = []
    for pos in outlier_pos:
        x.append(np.array(raw_data[data])[pos])
        y.append(raw_data[data].index[pos])

    # raw_data[[data]].plot(linewidth=2, figsize=(12, 6), alpha=0.8)
    # plt.plot(y, x, 'r*', markersize=8, label='Outliers')
    # plt.title('Detected Outliers')
    # plt.xlabel('Data points')
    # plt.ylabel(data + ' concentration (µg/m³)')
    # plt.legend()
    # plt.show()

    # Updating values in raw file and adding outlier locations to csv file
    raw_data[data + '_updated'] = raw_data[data]
    raw_data[data + '_outlier'] = False

    for index in outlier_pos:
        raw_data.at[index + 1, data + '_updated'] = (raw_data[data][index - 1] + raw_data[data][index + 3]) / 2
        raw_data.at[index + 1, data + '_outlier'] = True


    # Using ARIMA to update outlier values

    raw_data[data + '_updatedARIMA'] = raw_data[data]
    X = raw_data[data].values
    diff = difference(X,1) #Differntiate to make data stationary
    # plt.title('Differentiated data')
    # plt.plot(diff) #Is data stationary?
    # plt.show()

    #Determine ARIMA values based of these plots
    # autocorrelation_plot(diff)
    # plt.show()
    # plot_pacf(diff, lags = 50)
    # plt.show()


    for outlier_position in outlier_pos:
        time_series = raw_data[data + '_updatedARIMA']
        series = time_series[0:outlier_position]
        X = series.values
        model = ARIMA(X, order=(0, 1, 2))
        model_fit = model.fit()
        forecast = model_fit.forecast()[0]
        raw_data.at[outlier_position + 1, data + '_updatedARIMA'] = forecast
        # print('Forecast: %f' % forecast)

    #ax = raw_data[[data]].plot(linewidth=2, figsize=(12, 6), alpha=0.8)
    raw_data[data + '_updatedARIMA'].plot(linewidth=2, figsize=(12, 6), alpha=0.8, label = 'Updated')
    plt.title('Updated PM2.5 Time series')
    plt.xlabel('Data points')
    plt.ylabel(data + ' concentration (µg/m³)')
    plt.legend()
    plt.show()

    frame = 25
    for i in outlier_pos:
        x_zoom = []
        y_zoomUpdate = []
        y_zoomOld = []
        x_outlier = []
        y_new = []
        y_old = []
        for j in range(i - frame, i + frame):
            y_zoomUpdate.append(raw_data[data + '_updatedARIMA'][j])
            y_zoomOld.append(raw_data[data][j])
            x_zoom.append(j)
            if j in outlier_pos:
                x_outlier.append(j+1)
                y_new.append(raw_data[data + '_updatedARIMA'][j+1])
                y_old.append(raw_data[data][j+1])
        plt.plot(x_zoom, y_zoomOld)
        plt.plot(x_zoom, y_zoomUpdate)
        plt.plot(x_outlier, y_new, 'go', markersize=6, label = 'Update using ARIMA')
        plt.plot(x_outlier, y_old, 'ro', markersize=6, label = 'Outlier')
        plt.xlabel('Data points')
        plt.ylabel(data + ' concentration (µg/m³)')
        plt.legend()
        plt.show()

raw_data.to_csv('processedData.csv')
