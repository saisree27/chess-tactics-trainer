import chess.engine

MATE_SCORE = 1000000
engine = chess.engine.SimpleEngine.popen_uci("../ChessTacticsTrainer/static/assets/stockfish/stockfish_20090216_x64_bmi2.exe")

def puzzle(old, new):
    """
    Identifies if the difference in evaluations of positions in a game 
    could point to a potential tactic.
    """
    if abs(new) >= MATE_SCORE - 100:
        return abs(old) <= 800 or new * old < 0
    if abs(new) >= 1000:
        return abs(old) <= 400 or new * old < 0
    if abs(new) >= 600: 
        return abs(old) <= 200 or new * old < 0
    if abs(new) >= 500:
        return abs(old) <= 150 or new * old < 0
    if abs(new) >= 400:
        return abs(old) <= 100 or new * old < 0
    if abs(new) >= 250:
        return abs(old) <= 50  or new * old < 0
    
    return abs(old) >= 600    and new * old <= 0

def check_for_best_move(board, verbose=False):
    list_evals = []

    for mv in board.legal_moves:
        copy = board.copy()
        copy.push(mv)
        info = engine.analyse(copy, chess.engine.Limit(depth=8))
        evaluation = info["score"].white().score(mate_score=MATE_SCORE)
        list_evals.append(evaluation)

    new_list = list(sorted(list_evals))

    if board.turn == chess.WHITE:
        # greatest value to least value
        new_list = list(reversed(new_list))

    if verbose:
        print(new_list)

    if len(new_list) <= 3:
        # side is in check, which is not the ideal start to a tactic
        return False
    
    diff = abs(new_list[0] - new_list[1]) 

    if new_list[0] * new_list[1] < 0:
        return diff > 300

    if diff >= 10000:
        # mating move
        return True
    if diff >= 800:
        return abs(new_list[1]) <= 300
    if diff >= 600:
        return abs(new_list[1]) <= 200
    if diff >= 500:
        return abs(new_list[1]) <= 150
    if diff >= 400:
        return abs(new_list[1]) <= 100
    if diff >= 250:
        return abs(new_list[1]) <= 50

    return False