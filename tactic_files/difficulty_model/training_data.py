import pandas
import csv
import random
import chess
import pickle
import tree
import heuristics

df = pandas.read_csv("lichess_db_puzzle.csv", header=None, usecols=[1,2,3])

samples = df.sample(n=1000)
records = samples.to_records(index=False)
result = list(records)

training_data = []

try:
    training_data = pickle.load(open("training_data_1000_samples.obj", "rb"))
except Exception as e:
    training_data = []

    for tactic in result:
        board = chess.Board(tactic[0])
        variation = tactic[1].split(" ")
        rating = tactic[2]
        board.push_uci(variation[0])

        training_data.append( (board.fen(), variation[1:], rating) )

    pickle.dump(training_data, open("training_data_1000_samples.obj", "wb"))


X = []
y = []

for index, tactic in enumerate(training_data):
    if index > 475:
        position = tactic[0]
        variation = tactic[1]
        rating = tactic[2]

        mst = tree.generate_search_tree( (position, variation) )
        
        max_depth = 0
        for node in mst.node_list:
            max_depth = max(max_depth, node.depth)
        
        features = heuristics.get_all_heuristics(mst, max_depth)
        print(f"{index} position {position} variation {variation} max_depth {max_depth} rating {rating}")
        print(features)

        X.append(features)
        y.append(rating)

        if index % 25 == 0:
            print("Saving data.")
            pickle.dump(X, open("featuresfrom475.obj", "wb"))
            pickle.dump(y, open("ratingsfrom475.obj", "wb"))

print("Saving data.")
pickle.dump(X, open("featuresfrom475.obj", "wb"))
pickle.dump(y, open("ratingsfrom475.obj", "wb"))