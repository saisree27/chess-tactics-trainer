import pickle
import chess

with open('best_so_far_gen_july_2019.obj', 'rb') as f:
    x = pickle.load(f)
    for num in x:
        print("--------------------------------------")
        print("Tactic generated from Game #%s" % num)
        tactic = x[num]
        print("Board: ")
        print(tactic[0])
        print(tactic[1])
        print("Evaluation before move: %s" % tactic[2])
        print("Evaluation after move: %s" % tactic[3])
        print("Best move is %s" % tactic[4])
        print("Variation %s" % tactic[5])
        input()