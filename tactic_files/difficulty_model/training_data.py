import pandas
import csv
import random
import chess
import pickle
import tree
import heuristics
from multiprocessing import Pool


df = pandas.read_csv("lichess_db_puzzle.csv", header=None, usecols=[1,2,3])


def training_data_job(df, features_filename, ratings_filename):
    samples = df.sample(n=10000)
    records = samples.to_records(index=False)
    result = list(records)

    training_data = []

    for tactic in result:
        board = chess.Board(tactic[0])
        variation = tactic[1].split(" ")
        rating = tactic[2]
        board.push_uci(variation[0])

        training_data.append( (board.fen(), variation[1:], rating) )


    X = []
    y = []

    N_START = 0

    for index, tactic in enumerate(training_data):
        if index >= N_START:
            position = tactic[0]
            variation = tactic[1]
            rating = tactic[2]

            mst = tree.generate_search_tree( (position, variation) )
            
            max_depth = 0
            for node in mst.node_list:
                max_depth = max(max_depth, node.depth)
            
            if max_depth < 5:
                pass
            else:
                features = heuristics.get_all_heuristics(mst, max_depth)
                print(f"{index} position {position} variation {variation} max_depth {max_depth} rating {rating}")
                print(features)

                X.append(features)
                y.append(rating)

            if index % 15 == 0:
                print("Saving data.")
                pickle.dump(X, open(features_filename, "wb"))
                pickle.dump(y, open(ratings_filename, "wb"))

    print("Saving data.")
    pickle.dump(X, open(features_filename, "wb"))
    pickle.dump(y, open(ratings_filename, "wb"))



training_data_job(df, 'more_features7.obj', 'more_ratings7.obj')

# if __name__ == '__main__':
#     pool = Pool()
#     result1 = pool.apply_async(training_data_job, [df, 'more_features4.obj', 'more_ratings4.obj'])
#     result2 = pool.apply_async(training_data_job, [df, 'more_features5.obj', 'more_ratings5.obj'])

#     answer1 = result1.get()
#     answer2 = result2.get()
