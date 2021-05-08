# Dense layers

def dense(data, loc=0.0):
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
    from tensorflow import keras
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()
    from tensorflow.keras.layers import Dense

    if loc == 0.0: # Aidan
        df = data[data['loc'] == 0.0]
        print('Location A')
    elif loc == 1.0: # Ayoung
        df = data[data['loc'] == 1.0]
        print('Location B')
    else:
        print('Check the location input.')

    df = df.drop('loc',axis=1)

    labels = ['PM2.5_pi', 'PM10_pi']

    # Split train & test
    n = len(df)
    train_df = df[0:int(n*0.8)]
    # val_df = df[int(n*0.7):int(n*0.8)]
    test_df = df[int(n*0.8):]

    n_input = len(train_df)

    X_train = train_df.drop(train_df[labels], axis=1)
    y_train1 = train_df['PM2.5_pi']
    y_train2 = train_df['PM10_pi']

    X_test = test_df.drop(test_df[labels], axis=1)
    y_true1 = test_df['PM2.5_pi']
    y_true2 = test_df['PM10_pi']

    X = X_train

    # Model
    input_layer = Input(shape=(X.shape[1],))
    dropout_layer = Dropout(0.2)(input_layer)
    dense_layer_1 = Dense(100, activation='relu')(dropout_layer)
    dense_layer_2 = Dense(50, activation='relu')(dense_layer_1)
    dense_layer_3 = Dense(25, activation='relu')(dense_layer_2)
    output = Dense(1)(dense_layer_3)

    model = Model(inputs=input_layer, outputs=output)
    model.summary()
    model.compile(loss="mean_squared_error" , optimizer="adam", metrics=["mean_squared_error"])

    # Model - PM2.5
    model25 = model
    print('Dense for PM2.5 starts')

    history25 = model25.fit(X_train, y_train1, batch_size=1, epochs=50, verbose=1, validation_split=0.125)

    pred1 = model25.predict(X_test)
    results25 = pd.DataFrame({'y_true1':test_df['PM2.5_pi'],'y_pred':pred1.ravel()})

    print("PM2.5 MSE: ", mean_squared_error(y_true1,pred1))
    print("PM2.5 MAE: ", mean_absolute_error(y_true1, pred1))

    # Model - PM10
    model10 = model
    print('Dense for PM10 starts')

    history10 = model10.fit(X_train, y_train2, batch_size=1, epochs=50, verbose=1, validation_split=0.125)

    pred2 = model10.predict(X_test)
    results10 = pd.DataFrame({'y_true1':test_df['PM10_pi'],'y_pred':pred2.ravel()})

    print("PM2.5 MSE: ", mean_squared_error(y_true2,pred2))
    print("PM2.5 MAE: ", mean_absolute_error(y_true2, pred2))

    y_pred1 = pred1
    y_pred2 = pred2

    e = {'PM2.5': [mean_squared_error(y_true1, y_pred1), mean_absolute_error(y_true1, y_pred1)], 
        'PM10': [mean_squared_error(y_true2, y_pred2), mean_absolute_error(y_true2, y_pred2)]}
    error_data = pd.DataFrame(data=e)
    error_data = error_data.rename(index = {0:'MSE', 1:'MAE'})

    return results25, results10, error_data

def plot(results25, results10, location=0.0, save=False):
    import matplotlib.pyplot as plt
    pm25 = plt.figure(1)
    plt.plot(results25, label = ['Labels', 'Predictions'])
    plt.xlabel('Count')
    plt.ylabel('PM2.5 [ug/m3]')
    plt.legend()
    if location == 0.0:
        plt.title('Location A PM2.5')
        loc = 'A'
    elif location == 1.0:
        plt.title('Location B PM2.5')
        loc = 'B'
    pm25.show()

    pm10 = plt.figure(2)
    plt.plot(results10, label = ['Labels', 'Predictions'])
    plt.xlabel('Count')
    plt.ylabel('PM10 [ug/m3]')
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
        pm10.savefig('./PM25_loc{}.png'.format(loc))
