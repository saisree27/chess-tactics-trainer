import numpy as np
import os
import tqdm
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten, BatchNormalization
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)

data_part_one = pickle.load(open("training_x_y_9_features.obj", 'rb'))
data_part_two = pickle.load(open("training_x_y_9_features_from_500.obj", 'rb'))
data_part_three = pickle.load(open("training_x_y_9_features_from_950.obj", 'rb'))

data_complete = np.concatenate([data_part_one, data_part_two, data_part_three])

# print(data_complete)

# def build_model():
#     model = Sequential()

#     model.add(Dense(100, input_shape=X_train[0].shape))
#     model.add(Activation("relu"))
#     model.add(Dense(50))
#     model.add(Activation("relu"))
#     model.add(Dense(100))
#     model.add(Activation("relu"))
#     model.add(Dense(25))
#     model.add(Activation("relu"))
#     model.add(Dense(1))

#     model.compile(loss="mean_squared_error", optimizer="adam", metrics=["accuracy"])

#     return model

# model = build_model()
# model.fit(X_train, y_train, batch_size=15, epochs=25, verbose=True, validation_split=0.1)

# metrics = model.evaluate(X_test, y_test)
# print(metrics)