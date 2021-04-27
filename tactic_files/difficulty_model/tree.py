import chess
import chess.engine
from chess.engine import Limit, SimpleEngine
import networkx as nx
import matplotlib.pyplot as plt
import pickle


class Node():
    def __init__(self, fen, move=None, evaluation=None, depth=0, root=False):
        self.evaluation = evaluation
        self.fen = fen
        self.move = move
        self.children = []
        self.parent = None
        self.leaf = True
        self.depth = depth
        self.root = root

    def add_child(self, node):
        self.children.append(node)
        self.leaf = False
    
    def remove_child(self, node):
        self.children.remove(node)
        self.leaf = True if len(self.children) == 0 else False

    def add_parent(self, node):
        self.parent = node

    def __str__(self):
        if self.parent:
            return f"Node(fen:{self.fen} evaluation:{self.evaluation} move_from_parent:{self.move} depth:{self.depth} parent:{self.parent.fen})" 
        else:
            return f"Node(fen:{self.root} ROOT:true)"
class MeaningfulSearchTree():
    def __init__(self, fen, variation):
        self.position = fen        
        self.move_list = variation
        self.w = 300
        self.m = 50
        self.MAX_MST_DEPTH = 5
        self.MAX_ENGINE_DEPTH = 10
        self.node_list = []
        self.tree = self.build_tree(fen, variation)

    def get_evaluation(self, engine, board):
        return engine.analyse(board, Limit(depth=self.MAX_ENGINE_DEPTH))["score"].white().score(mate_score=1000000)
    
    def get_best_move(self, engine, board):
        return engine.play(board, Limit(depth=self.MAX_ENGINE_DEPTH)).move

    def build_tree(self, fen, variation):
        print("-------------------------------")
        print("Building tree...")
        print("FEN: %s" % fen)
        print("Variation: " + str(variation))
        final_tree = Node(fen, root=True)
        self.node_list.append(final_tree)

        board = chess.Board(fen)
        engine = SimpleEngine.popen_uci("../../ChessTacticsTrainer/static/assets/stockfish/stockfish_20090216_x64_bmi2.exe")

        board.push_uci(variation[0])
        evaluation = self.get_evaluation(engine, board)

        first_layer_node = Node(board.fen(), move=variation[0], evaluation=evaluation, depth=1)
        final_tree.add_child(first_layer_node)
        first_layer_node.add_parent(final_tree)
        self.node_list.append(first_layer_node)

        for d in range(1, self.MAX_MST_DEPTH, 2):
            print("Depth %s" % d)
            for node in self.node_list:
                if node.leaf and node.depth == d:
                    # print(node)
                    
                    board = chess.Board(node.fen)
                    best_move = self.get_best_move(engine, board)
                    if best_move is None:
                        if abs(self.get_evaluation(engine, board)) >= 100000:
                            return final_tree
                    # print(best_move)
                    # print(board)
                    board.push(best_move)
                    best_evaluation = self.get_evaluation(engine, board)
                    moves_to_consider = [Node(board.fen(), move=str(best_move), evaluation=best_evaluation, depth=d+1)]
                    board.pop()

                    for x in board.legal_moves:
                        if str(x) != str(best_move):
                            board.push(x)
                            evaluation = self.get_evaluation(engine, board)
                            if abs(evaluation - best_evaluation) <= self.m:
                                # print("Found another possible opponent move")
                                moves_to_consider.append( Node(board.fen(), move=str(x), evaluation=evaluation, depth=d+1) )
                            board.pop()
                    
                    for child in moves_to_consider:
                        node.add_child(child)
                        self.node_list.append(child)
                        child.add_parent(node)

                        my_moves_to_consider = []

                        board = chess.Board(child.fen)
                        # print(child.fen)

                        best_player_move = self.get_best_move(engine, board)
                        
                        board.push(best_player_move)
                        best_evaluation = self.get_evaluation(engine, board)
                        my_moves_to_consider = [Node(board.fen(), move=str(best_player_move), evaluation=best_evaluation, depth=d+2)]
                        board.pop()

                        for x in board.legal_moves:
                            if str(x) != str(best_player_move):
                                
                                board.push(x)
                                evaluation = self.get_evaluation(engine, board)
                                if abs(evaluation) >= self.w and not (abs(best_evaluation) > 100000 and abs(evaluation) < abs(best_evaluation)) \
                                        and not evaluation * best_evaluation < 0 and not abs(evaluation) > abs(best_evaluation):
                                    # print("found another possible move for me")
                                    # print(str(x))
                                    # print(evaluation)
                                    my_moves_to_consider.append( Node(board.fen(), move=str(x), evaluation=evaluation, depth=d+2) )
                                board.pop()

                        for new_node in my_moves_to_consider:
                            self.node_list.append(new_node)
                            child.add_child(new_node)
                            new_node.add_parent(child)
        return final_tree

def generate_search_tree(tactic):
    '''
    tactic: Array of objects -> [0]: FEN, [1]: variation (list) 
    Method will use Stockfish (10-ply) to construct meaningful search tree
    (https://ailab.si/matej/doc/A_Computational_Model_for_Estimating_the_Difficulty_of_Chess_Problems.pdf)
    '''
    return MeaningfulSearchTree(tactic[0], tactic[1])


def process_tactics(filename):
    tactics_dict = {}
    with open(filename, 'rb') as f:
        tactics_dict = pickle.load(f)

    tactics_with_trees = {}
    counter = 1

    for num in tactics_dict:
        if counter > 1600 and counter < 2400:
            print("---------------------")
            print(f"Tactic {counter}")
            tactic = tactics_dict[num]
            position = tactic[1]
            variation = tactic[5]
            classifications = tactic[6]

            tree = None
            if len(variation) == 1 and 'HANGING PIECE' in classifications:
                print("Found one-move, simple tactic")
            else:
                tree = generate_search_tree( (position, variation) )
                print("TREE FINISHED.")
            
            tactics_with_trees[num] = (tactic[1], tactic[5], tactic[6], tree)

            
            if counter % 50 == 0:
                print("Saving current trees")
                pickle.dump( tactics_with_trees, open("july2016_with_classifications_trees_1600_to_2400", 'wb') )

        counter += 1

if __name__ == '__main__':
    process_tactics('../../ChessTacticsTrainer/static/assets/JULY 2016 FINAL WITH CLASSIFICATIONS.obj')