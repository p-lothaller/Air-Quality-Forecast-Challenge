import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import numpy as np
from kneed import KneeLocator
import matplotlib as mpl
from sklearn.metrics import mean_absolute_error
mpl.use('TkAgg')


#Read in csv file

location = 'Location1' #For saving the processed data

raw_data = pd.read_csv('airdata_raw.csv',  index_col=False)
raw_data = raw_data.dropna()


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

#add data that needs to be analysed
analyse_data = ['PM1', 'PM2.5', 'PM10', 'hum']

for data in analyse_data:

        # raw_data.plot(x='time', y=data, figsize=(12,6))
        # plt.xlabel('Date time')
        # plt.ylabel(data)
        # plt.title('Time Series of' + data)

        #create upper and lower bounds using a exponetial moving average and confidence intervals

        raw_data['EMA_0.1-'+data] = raw_data[data].ewm(alpha=0.1, adjust=False).mean()

        mae = mean_absolute_error(raw_data[data], raw_data['EMA_0.1-'+data])
        deviation = np.std(raw_data[data] - raw_data['EMA_0.1-'+data])
        raw_data['upper_bound'] = raw_data['EMA_0.1-'+data] + (mae +1.96*deviation)
        raw_data['lower_bound'] = raw_data['EMA_0.1-'+data] - (mae +1.96*deviation)

        #identifying outliers:

        upper_outliers = np.array(raw_data[data]>raw_data['upper_bound'])
        lower_outliers = np.array(raw_data[data]<raw_data['lower_bound'])

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

        raw_data[[data, 'EMA_0.1-'+data]].plot(linewidth=2, figsize=(12,6), alpha=0.8, ax=ax)
        raw_data[['upper_bound', 'lower_bound']].plot(linewidth=1, color='red', alpha=0.8, ax=ax, label = 'Upper/Lower bound')
        plt.plot(y_ema,x_ema,'r*', markersize=8, label = 'Outliers')
        plt.legend()

        #Identifying outliers using unsupervised machine learning
        #Calculating eps --> this changes depending on the data

        minPts = 4 #For 2D data the default value is a good approximation for the minimum sample points in a cluster (Ester et al., 1996)

        neighbors = NearestNeighbors(n_neighbors=minPts)
        neighbors_fit = neighbors.fit(np.array(raw_data[data]).reshape(-1,1))
        distances, indices = neighbors_fit.kneighbors(np.array(raw_data[data]).reshape(-1,1))
        distances = np.sort(distances, axis=0)

        distances = distances[:,1]
        x = np.linspace(0,len(distances),len(distances))

        kn = KneeLocator(x, distances, curve='convex', direction='increasing')


        epsilon = kn.elbow_y
        minPts = 4 #For 2D data the default value is a good approximation for the minimum sample points in a cluster (Ester et al., 1996)


        clustering1 = DBSCAN(eps=epsilon, min_samples=minPts).fit(np.array(raw_data[data]).reshape(-1,1))
        labels = clustering1.labels_
        outlier_pos_DBSCAN = np.where(labels == -1)[0]

        #Creating new entry for outlier tracking
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

        raw_data[[data]].plot(linewidth=2, figsize=(12,6), alpha=0.8)
        plt.plot(y_DBSCAN,x_DBSCAN,'r*', markersize=8)


        outlier_pos = sorted(set(outlier_pos_ema).intersection(outlier_pos_DBSCAN))
        x = []
        y = []
        for pos in outlier_pos:
            x.append(np.array(raw_data[data])[pos])
            y.append(raw_data[data].index[pos])

        raw_data[[data]].plot(linewidth=2, figsize=(12,6), alpha=0.8)
        plt.plot(y, x,'r*', markersize=8)


        #Updating values in raw file
        raw_data[data+'_updated'] = raw_data[data]

        for index in outlier_pos:
            raw_data.at[index+1, data+'_updated'] = (raw_data[data][index]+raw_data[data][index+2])/2

        raw_data[data+'_updated'].plot(linewidth=2, figsize=(12, 6), alpha=0.8)
        plt.show()


raw_data.to_csv(location+'_processedRawData.csv')



