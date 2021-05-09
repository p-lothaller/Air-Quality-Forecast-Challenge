import LSTM_model
import numpy as np
import pandas as pd

data = pd.read_csv('1h_1.csv')
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
data.dropna(inplace=True)
data.reset_index(drop=True, inplace=True)
data = data.iloc[:1074,:]

results25, results10, error = LSTM_model.lstm(data, loc=None)

LSTM_model.lstm_plot(results25, results10, location=None)

results25 = np.array(results25)
results10 = np.array(results10)
np.savetxt("results25_1.csv", results25, delimiter=",", fmt="%s", comments='', header='y_true,y_pred')
np.savetxt("results10_1.csv", results10, delimiter=",", fmt="%s", comments='', header='y_true,y_pred')