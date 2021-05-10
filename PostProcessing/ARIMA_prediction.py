import pandas as pd
from pandas.plotting import autocorrelation_plot
import matplotlib.pyplot as plt
from pandas import DataFrame
from statsmodels.tsa.arima.model import ARIMA
import matplotlib as mpl
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.stattools import adfuller
mpl.use('TkAgg')

raw_data = pd.read_csv('airdata_all.csv',  index_col=False)
raw_data = raw_data.dropna()
series = raw_data['PM2.5']

#Determine if time series is stationary
X = series.values
# result = adfuller(X)
# print('ADF Statistic: %f' % result[0])
# print('p-value: %f' % result[1])
# print('Critical Values:')
# for key, value in result[4].items():
# 	print('\t%s: %.3f' % (key, value))

#Use autocorrelation to determine lag value of the ARIMA model
# autocorrelation_plot(series)
# plt.show()

#Fit ARIMA model

# model = ARIMA(series, order=(5,0,0))
# model_fit = model.fit()
# print(model_fit.summary())
# # line plot of residuals
# residuals = DataFrame(model_fit.resid)
# residuals.plot()
# plt.show()
# # density plot of residuals
# residuals.plot(kind='kde')
# plt.show()
# # summary stats of residuals
# print(residuals.describe())
counter = 325
data = series[0:counter]
X = data.values
size = int(counter * 0.8)
train, test = X[0:size], X[size:counter]
model = ARIMA(X, order=(5,0,1))
model_fit = model.fit()
forecast = model_fit.forecast()[0]
print('Forecast: %f' % forecast)
print(series[324])
print(series[325])
print(series[326])
# history = [x for x in train]
# predictions = list()
# # walk-forward validation
# for t in range(len(test)):
# 	model = ARIMA(history, order=(5,0,0))
# 	model_fit = model.fit()
# 	output = model_fit.forecast()
# 	yhat = output[0]
# 	predictions.append(yhat)
# 	obs = test[t]
# 	history.append(obs)
# 	print('predicted=%f, expected=%f' % (yhat, obs))
# # evaluate forecasts
# rmse = sqrt(mean_squared_error(test, predictions))
# print('Test RMSE: %.3f' % rmse)
# # plot forecasts against actual outcomes
# plt.plot(test)
# plt.plot(predictions, color='red')
# plt.show()
