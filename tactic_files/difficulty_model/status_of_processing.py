
import tree
import pickle
from tree import MeaningfulSearchTree, Node

trees = {}

with open('july2016_with_c_r_third_800_2', 'rb') as f:
    trees = pickle.load(f)

# for num in trees:
#     print(num)


print(len(trees))
