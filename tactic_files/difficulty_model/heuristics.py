import chess
import chess.engine
from chess.engine import Limit, SimpleEngine
import tree
from tree import MeaningfulSearchTree, Node
import numpy as np

def meaningful(tree, level):
    '''
    Number of moves in the meaningful search tree at level L
    '''
    total = 0
    for node in tree.node_list:
        if node.depth == level:
            total += 1
    return total

def possible_moves(tree, level):
    '''
    Number of legal moves at level L
    '''
    total = 0
    for node in tree.node_list:
        if node.depth == level:
            board = chess.Board(node.parent.fen)
            total += len(list(board.legal_moves))
    return total

def all_possible_moves(tree, max_depth):
    '''
    Nuumber of all legal moves at all levels
    '''
    total = 0
    for l in range(1, max_depth + 1):
        total += possible_moves(tree, l)
    return total

def branching(tree, level):
    '''
    Branching factor at each level L of the meaningful search tree
    '''
    return meaningful(tree, level) / meaningful(tree, level - 1)

def average_branching(tree, max_depth):
    '''
    Average branching factor for the meaningful search tree
    '''
    total = 0
    for l in range(1, max_depth + 1):
        total += branching(tree, l)
    
    return total / max_depth

def narrow_solution(tree, level):
    '''
    Number of moves that only have one meaningful answer, at level L
    '''
    total = 0
    for node in tree.node_list:
        if node.depth == level:
            if len(node.children) == 1:
                total += 1
    return total    

def all_narrow_solutions(tree, max_depth):
    '''
    Sum of NarrowSolution(L) for all levels L
    '''
    total = 0
    for l in range(1, max_depth + 1):
        total += narrow_solution(tree, l)
    return total
    
def tree_size(tree):
    '''
    Number of nodes in the meaningful search tree
    '''
    return len(tree.node_list)

def move_ratio(tree, level):
    '''
    Ratio between meaningful moves and all possible moves, at level L
    '''
    return meaningful(tree, level) / possible_moves(tree, level)

def seemingly_good(tree):
    '''
    Number of non-winning first moves that only have one good answer
    '''
    count = 0
    engine = SimpleEngine.popen_uci("../../ChessTacticsTrainer/static/assets/stockfish/stockfish_20090216_x64_bmi2.exe")
    for node in tree.node_list:
        if node.depth == 0:
            board = chess.Board(node.fen)                     
            for move in board.legal_moves:
                seemingly_good = True
                board.push(move)

                cur_evaluation = engine.analyse(board, Limit(depth=10))["score"].white().score(mate_score=1000000)

                if abs(cur_evaluation) > 150:
                    seemingly_good = False

                best_reply = engine.play(board, Limit(depth=10)).move
                board.push(best_reply)
                best_evaluation = engine.analyse(board, Limit(depth=10))["score"].white().score(mate_score=1000000)
                board.pop()

                for reply in board.legal_moves:
                    board.push(reply)
                    evaluation = engine.analyse(board, Limit(depth=10))["score"].white().score(mate_score=1000000)

                    if abs(best_evaluation - evaluation) < 50 and str(reply) != str(best_reply):
                        seemingly_good = False
                    
                    board.pop()
                board.pop()

                if seemingly_good:
                    count += 1
    return count

def distance(tree, level):
    '''
    Distance between start and end square for each move at level L
    '''

def sum_distance(tree):
    '''
    Sum of Distance(L) for all levels L
    '''

def average_distance(tree):
    '''
    Average distance of all the moves in the meaningful search tree
    '''

def pieces(tree, level):
    '''
    Number of different pieces that move at level L
    '''

def all_pieces_involved(tree):
    '''
    Number of different pieces that move in the meaningful search tree
    '''

def piece_value_ratio(tree):
    '''
    Ratio of material on the board, player versus opponent
    '''

def winning_no_checkmate(tree):
    '''
    Number first moves that win, but do not lead to checkmate
    '''

def best_move_value(tree):
    '''
    The computer evaluation of the best move
    '''

def average_best_move(tree):
    '''
    Average best-move value of all best moves occurring at level 5
    '''

def get_all_heuristics(tree, depth):
    a = [meaningful(tree, d) for d in range(1, depth + 1)]
    for x in range(depth + 1, 6):
        a.append(0)
    b = [possible_moves(tree, d) for d in range(1, depth + 1)]
    for x in range(depth + 1, 6):
        b.append(0)
    c = [all_possible_moves(tree, depth)]
    d = [branching(tree, d) for d in range(1, depth + 1)]
    for x in range(depth + 1, 6):
        d.append(0)
    e = [average_branching(tree, depth)]
    f = [narrow_solution(tree, d) for d in range(1, depth + 1)]
    for x in range(depth + 1, 6):
        f.append(0)
    g = [all_narrow_solutions(tree, depth)]
    h = [tree_size(tree)]
    i = [move_ratio(tree, d) for d in range(1, depth + 1)]
    for x in range(depth + 1, 6):
        i.append(0)
    j = [seemingly_good(tree)]

    heuristics = a + b + c + d + e + f + g + h + i + j
    
    return np.array(heuristics)