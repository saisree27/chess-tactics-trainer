import numpy as np
import os
import tqdm
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten, BatchNormalization
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle


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

fone = pickle.load(open("more_features1.obj", 'rb'))
ftwo = pickle.load(open("more_features2.obj", 'rb'))
fthree = pickle.load(open("more_features3.obj", 'rb'))
ffour = pickle.load(open("more_features4.obj", 'rb'))
ffive = pickle.load(open("more_features5.obj", 'rb'))
fsix = pickle.load(open("more_features6.obj", 'rb'))
fseven = pickle.load(open("more_features7.obj", 'rb'))


rone = pickle.load(open("more_ratings1.obj", 'rb'))
rtwo = pickle.load(open("more_ratings2.obj", 'rb'))
rthree = pickle.load(open("more_ratings3.obj", 'rb'))
rfour = pickle.load(open("more_ratings4.obj", 'rb'))
rfive = pickle.load(open("more_ratings5.obj", 'rb'))
rsix = pickle.load(open("more_ratings6.obj", 'rb'))
rseven = pickle.load(open("more_ratings7.obj", 'rb'))


# print(features_part_one)


features = np.concatenate([fone, ftwo, fthree, ffour, ffive, fsix, fseven])
ratings = np.concatenate([rone, rtwo, rthree, rfour, rfive, rsix, rseven])

print(features.shape)
print(features[0].shape)
print(ratings.shape)
print(ratings[0].shape)

print(features)
print(ratings)

X = features.astype("float32")
y = ratings.astype("float32")

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=30)


scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

pickle.dump(scaler, open('scaler2.pkl', 'wb'))


def build_model():
    model = Sequential()

    model.add(Dense(50, input_shape=x_train[0].shape))
    model.add(Activation("relu"))
    model.add(Dense(125))
    model.add(Activation("relu"))
    model.add(Dense(100))
    model.add(Activation("relu"))
    model.add(Dense(50))
    model.add(Activation("relu"))
    model.add(Dense(25))
    model.add(Activation("relu"))
    model.add(Dense(1))

    model.compile(loss="mean_squared_error", optimizer="adam", metrics=[])

    return model

model = build_model()
model.fit(x_train, y_train, batch_size=1, epochs=10, verbose=True, validation_split=0.1)

metrics = model.evaluate(x_test, y_test)
print(metrics)

prediction = model.predict(x_test)
print(prediction[:10])
print(y_test[:10])

model.save("best_tactic_model2.h5")