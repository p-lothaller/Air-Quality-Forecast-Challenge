# LSTM learning model

def lstm(data, loc=0.0, dropout=0.1):
    import tensorflow as tf
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.layers import Input, Dense, Activation,Dropout
    from tensorflow.keras.models import Model
    from tensorflow.keras import preprocessing
    from tensorflow import keras
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()
    from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense
    from tensorflow.keras.layers import LSTM
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

    col_use = ['time', 'hour', 'location', 'temp_pi', 
        'hum_pi', 'PM1_pi', 'PM2.5_pi',
        'PM10_pi']
    data = data[col_use]
    data.dropna(inplace=True)
    data.reset_index(drop=True, inplace=True)


    # designate columns
    labels = ['PM2.5_pi', 'PM10_pi']
    x_pi = ['hour', 'temp_pi', 'hum_pi', 'PM1_pi']
    x_ext = ['hour', 'temp_blue', 'hum_blue']

    y_pi = ['PM2.5_pi', 'PM10_pi']
    y_ext = ['PM2.5', 'PM10']

    df = data[x_pi+y_pi]

    # Split train & test
    n = len(df)
    train_df = df[0:int(n*0.8)]
    # val_df = df[int(n*0.7):int(n*0.8)]
    test_df = df[int(n*0.8):]

    X_train = train_df.drop(train_df[labels], axis=1)
    y_train1 = train_df['PM2.5_pi']
    y_train2 = train_df['PM10_pi']
    y_train1 = y_train1.to_frame()
    y_train2 = y_train2.to_frame()

    X_test = test_df.drop(test_df[labels], axis=1)
    X_test

    # Scaling of train set
    Xscaler = MinMaxScaler(feature_range=(0, 1)) # scale so that all the X data will range from 0 to 1
    Xscaler.fit(X_train)
    scaled_X_train = Xscaler.transform(X_train)
    print(X_train.shape)

    Yscaler1 = MinMaxScaler(feature_range=(0, 1))
    Yscaler1.fit(y_train1)
    scaled_y_train1 = Yscaler1.transform(y_train1)
    print(scaled_y_train1.shape)
    scaled_y_train1 = scaled_y_train1.reshape(-1) # remove the second dimention from y so the shape changes from (n,1) to (n,)
    print(scaled_y_train1.shape)

    Yscaler2 = MinMaxScaler(feature_range=(0, 1))
    Yscaler2.fit(y_train2)
    scaled_y_train2 = Yscaler2.transform(y_train2)
    print(scaled_y_train2.shape)
    scaled_y_train2 = scaled_y_train2.reshape(-1) # remove the second dimention from y so the shape changes from (n,1) to (n,)
    print(scaled_y_train2.shape)

    scaled_y_train1 = np.insert(scaled_y_train1, 0, 0)
    scaled_y_train1 = np.delete(scaled_y_train1, -1)

    scaled_y_train2 = np.insert(scaled_y_train2, 0, 0)
    scaled_y_train2 = np.delete(scaled_y_train2, -1)

    # Scaling of test set
    # Only X required
    scaled_X_test = Xscaler.transform(X_test)
    test_generator = TimeseriesGenerator(scaled_X_test, np.zeros(len(X_test)), length=6, batch_size=1)
    print(test_generator[0][0].shape)

    # Designate time series & batch size
    n_input = 6 #how many samples/rows/timesteps to look in the past in order to forecast the next sample 
    n_features= X_train.shape[1] # how many predictors/Xs/features we have to predict y
    b_size = 1 # Number of timeseries samples in each batch
    generator1 = TimeseriesGenerator(scaled_X_train, scaled_y_train1, length=n_input, batch_size=b_size) #PM2.5
    generator2 = TimeseriesGenerator(scaled_X_train, scaled_y_train2, length=n_input, batch_size=b_size) #PM10 

    print('PM2.5 input shape:', generator1[0][0].shape)
    print('PM10 input shape:', generator2[0][0].shape)

    # Model
    d = dropout

    model = Sequential()
    model.add(LSTM(256, activation='relu', input_shape=(n_input, n_features), dropout=d))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.summary()

    # Model - PM2.5
    model25 = model
    early_stopping = EarlyStopping(monitor='loss', patience=5)
    model_checkpoint = ModelCheckpoint(filepath = './PM25-{epoch}-{loss:.2f}.h5', monitor='loss', save_best_only=True, verbose=1)

    print('LSTM for PM2.5 starts')
    model25.fit(generator1,epochs=15) # ,callbacks=[early_stopping, model_checkpoint]

    y_pred_scaled1 = model25.predict(test_generator)
    y_pred1 = Yscaler1.inverse_transform(y_pred_scaled1)
    results25 = pd.DataFrame({'y_true':test_df['PM2.5_pi'].values[n_input:],'y_pred':y_pred1.ravel()})

    y_true1= test_df['PM2.5_pi'].values[n_input:]
    y_pred1 = y_pred1.ravel()
    print("PM2.5 MSE: ", mean_squared_error(y_true1, y_pred1))
    print("PM2.5 MAE: ", mean_absolute_error(y_true1, y_pred1))

    # Model - PM10
    model10 = model
    early_stopping = EarlyStopping(monitor='loss', patience=5)
    model_checkpoint = ModelCheckpoint(filepath = './PM10-{epoch}-{loss:.2f}.h5', monitor='loss', save_best_only=True, verbose=1)

    print('LSTM for PM10 starts')
    model10.fit(generator2,epochs=15)  # ,callbacks=[early_stopping, model_checkpoint]
    y_pred_scaled2 = model10.predict(test_generator)
    y_pred2 = Yscaler2.inverse_transform(y_pred_scaled2)
    results10 = pd.DataFrame({'y_true1':test_df['PM10_pi'].values[n_input:],'y_pred':y_pred2.ravel()})

    y_true2= test_df['PM10_pi'].values[n_input:]
    y_pred2 = y_pred2.ravel()
    print("PM2.5 MSE: ", mean_squared_error(y_true2, y_pred2))
    print("PM2.5 MAE: ", mean_absolute_error(y_true2, y_pred2))

    e = {'Dropout': [dropout, dropout],
        'PM2.5': [mean_squared_error(y_true1, y_pred1), mean_absolute_error(y_true1, y_pred1)], 
        'PM10': [mean_squared_error(y_true2, y_pred2), mean_absolute_error(y_true2, y_pred2)]}
    error_data = pd.DataFrame(data=e)
    error_data = error_data.rename(index = {0:'MSE', 1:'MAE'})

    return results25, results10, error_data

def lstm_plot(results25, results10, location=0.0, save=False):
    import matplotlib.pyplot as plt
    pm25 = plt.figure(1)
    plt.plot(results25, label = ['True', 'LSTM'])
    plt.xlabel('Hour (h)')
    plt.ylabel('PM2.5 [µg/m3]')
    plt.legend()
    if location == 0.0:
        plt.title('Location A PM2.5')
        loc = 'A'
    elif location == 1.0:
        plt.title('Location B PM2.5')
        loc = 'B'
    pm25.show()

    pm10 = plt.figure(2)
    plt.plot(results10, label = ['True', 'LSTM'])
    plt.xlabel('Hour (h)')
    plt.ylabel('PM10 [µg/m3]')
    plt.legend()
    if location == 0.0:
        plt.title('Location A PM10')
        loc = 'A'
    elif location == 1.0:
        plt.title('Location B PM10')
        loc = 'B'
    pm10.show()

    if save==True:
        pm25.savefig('./PM25_loc{}.png'.format(loc))
        pm10.savefig('./PM10_loc{}.png'.format(loc))
