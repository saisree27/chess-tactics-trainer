import numpy as np
import os
import tqdm
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten, BatchNormalization
from tensorflow.keras.models import load_model
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import tree
from tree import MeaningfulSearchTree, Node
import heuristics
from tensorflow.keras import backend as K

def soft_acc(y_true, y_pred):
    return K.mean(K.equal(K.round(y_true), K.round(y_pred)))

def get_ratings(features_file):
    scaler = pickle.load(open('scaler2.pkl', 'rb'))
    features = pickle.load(open(features_file, 'rb'))

    features = np.asarray(features)
    features = features.astype("float32")
    features = scaler.transform(features)

    dependencies = {
        'soft_acc': soft_acc
    }

    model = load_model('best_tactic_model2.h5', custom_objects=dependencies)
    ratings = model.predict(features)

    print(ratings)
    return ratings

def get_features(tactics, savefile):
    all_features = []
    count = 0
    for num in tactics:
        print(count)
        print("------------------------------")
        position, variation, classification, mst = tactics[num]
        
        max_depth = 0
        for node in mst.node_list:
            max_depth = max(max_depth, node.depth)
        
        features = heuristics.get_all_heuristics(mst, max_depth)
        print(features)
        all_features.append(features)

        if count % 25 == 0:
            print("Saving data.")
            pickle.dump(all_features, open(savefile, 'wb'))

        count += 1
    
    pickle.dump(all_features, open(savefile, 'wb'))

def process_tactic_file(filename, features_save, final_save):
    tactics = pickle.load(open(filename, 'rb'))
    tactics_with_ratings = {}

    # removing all tactics with NoneType MSTs (too easy tactics)
    to_be_processed = {}
    for num in tactics:
        if len(tactics[num]) > 4:
            _, position, _, _, _, variation, classification, mst = tactics[num]
        else:
            position, variation, classification, mst = tactics[num]
        
        if mst is None:
            tactics_with_ratings[num] = (position, variation, classification, 600)
        else:
            max_depth = 0
            for node in mst.node_list:
                max_depth = max(max_depth, node.depth)
            if max_depth < 5:
                tactics_with_ratings[num] = (position, variation, classification, 1200)
            else:
                to_be_processed[num] = (position, variation, classification, mst)


    get_features(to_be_processed, features_save)
    ratings = get_ratings(features_save)

    count = 0
    for num in to_be_processed:

        position, variation, classification, mst = to_be_processed[num]
        rating = ratings[count]

        print(position, variation)
        print(rating)

        tactics_with_ratings[num] = (position, variation, classification, rating)
        count += 1

    pickle.dump(tactics_with_ratings, open(final_save, 'wb'))

process_tactic_file('july2016_with_classifications_trees_1600_to_2400', 'J2016f1600_2400_features_30', 'july2016_with_c_r_third_800_2')