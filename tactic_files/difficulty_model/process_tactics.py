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


def create_tree(position, variation):
    return tree.generate_search_tree( (position, variation) )

def get_features(tree):
    return heuristics.get_all_heuristics(tree, 5)

def get_rating(features):
    scaler = pickle.load(open('scaler2.pkl', 'rb'))

    features = np.array(features).reshape(1, -1)
    features = features.astype("float32")
    features = scaler.transform(features)

    model = load_model('best_tactic_model2.h5')
    rating = model.predict(features)

    print(rating)
    return rating[0]


def process_tactic_file(filename, savefile):
    tactics = pickle.load(open(filename, 'rb'))
    tactics_with_ratings = {}

    counter = 0
    for num in tactics:
        if counter >= 385:
            print("-----------------------")
            print(f"Tactic {counter}")
            tactic = tactics[num]
            if len(tactics[num]) > 4:
                _, position, _, _, _, variation, classification = tactics[num]
            else:
                position, variation, classification = tactics[num]
            
            mst = None
            if len(variation) == 1 and 'HANGING PIECE' in classification:
                print("Found one-move, hanging piece tactic")
            else:
                mst = create_tree( position, variation )
                print("Finished tree.")
            
            if mst is None:
                tactics_with_ratings[num] = (position, variation, classification, 600)
            else:
                max_depth = 0
                for node in mst.node_list:
                    max_depth = max(max_depth, node.depth)
                if max_depth < 5:
                    tactics_with_ratings[num] = (position, variation, classification, 1200)
                else:
                    print("Getting features. . .")
                    features = get_features(mst)
                    print("Got features.")
                    rating = get_rating(features)
                    print("Got rating.")
                    tactics_with_ratings[num] = (position, variation, classification, rating)

            pickle.dump(tactics_with_ratings, open(savefile, 'wb'))
            print("Saved.")

        counter += 1

process_tactic_file('../JULY 2019 FINAL WITH CLASSIFICATIONS.obj', 'J2019_c_r_from_385')