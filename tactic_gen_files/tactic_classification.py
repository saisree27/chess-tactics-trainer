import pickle
import chess


def total_pieces(board):
    white = 0
    black = 0
    for square in chess.SQUARES:
        if(board.color_at(square)==chess.BLACK):
            black = black + 1
        elif(board.color_at(square)==chess.WHITE):
            white = white + 1
    return white+black 


def checkmate(board, fen, eval_before_move, eval_after_move, best_move, variation):
    return abs(eval_after_move) >= 90000

def discovered_check(board, fen, eval_before_move, eval_after_move, best_move, variation):
    temp = board.copy()
    discovered_check_counter = 0
    for index, move in enumerate(variation):
        piece_moved = temp.piece_at(chess.Move.from_uci(move).from_square)
        temp.push(chess.Move.from_uci(move))
        for x in temp.checkers():
            checking_piece = temp.piece_at(x)
            if checking_piece.symbol() != piece_moved.symbol():
                return True
    return False

def windmill(board, fen, eval_before_move, eval_after_move, best_move, variation):
    temp = board.copy()
    discovered_check_counter = 0
    for index, move in enumerate(variation):
        piece_moved = temp.piece_at(chess.Move.from_uci(move).from_square)
        temp.push(chess.Move.from_uci(move))
        for x in temp.checkers():
            checking_piece = temp.piece_at(x)
            if checking_piece.symbol() != piece_moved.symbol():
                discovered_check_counter += 1
    if discovered_check_counter >= 2:
        return True
    return False

def sacrifice(board, fen, eval_before_move, eval_after_move, best_move, variation):
    temp = board.copy()
    symbol_to_value = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 900000}    
    for index, move in enumerate(variation):
        piece_moved = temp.piece_at(chess.Move.from_uci(move).from_square)
        if temp.piece_at(chess.Move.from_uci(move).to_square) and index % 2 == 0:
            # this is a capture, check if material is higher in the piece_moved (this is a sacrifice)
            # also check that it is the player's move
            piece_captured = temp.piece_at(chess.Move.from_uci(move).to_square)
            print(piece_captured)
            print(piece_moved)
            print(move)
            diff = symbol_to_value[piece_captured.symbol().lower()] - symbol_to_value[piece_moved.symbol().lower()]
            if diff < 0:
                # taking a piece of lower value
                # check if defended
                color_to_check = not piece_moved.symbol().isupper()
                if temp.is_attacked_by(color_to_check, chess.Move.from_uci(move).to_square):
                    return True
        if temp.piece_at(chess.Move.from_uci(move).to_square) and index % 2 == 1:
            # check if opponent is taking a free piece
            piece_captured = temp.piece_at(chess.Move.from_uci(move).to_square)
            diff = symbol_to_value[piece_captured.symbol().lower()] - symbol_to_value[piece_moved.symbol().lower()]
            if diff > 0:
                # my opponent is taking a piece which is valued higher than the piece which is moving
                return True
            else:
                # my piece has to be undefended (e.g. my opponent takes a free pawn with bishop)
                color_to_check = not piece_moved.symbol().isupper()
                if not temp.is_attacked_by(color_to_check, chess.Move.from_uci(move).to_square):
                    return True
        temp.push(chess.Move.from_uci(move))
    return False

def hanging_piece(board, fen, eval_before_move, eval_after_move, best_move, variation):
    temp = board.copy()
    symbol_to_value = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 900000}    
    for index, move in enumerate(variation):
        piece_moved = temp.piece_at(chess.Move.from_uci(move).from_square)
        if temp.piece_at(chess.Move.from_uci(move).to_square) and index % 2 == 0:
            # this is a capture, check if material is higher in the piece_moved (this is a sacrifice)
            # also check that it is the player's move
            piece_captured = temp.piece_at(chess.Move.from_uci(move).to_square)
            print(piece_captured)
            print(piece_moved)
            print(move)
            # diff = symbol_to_value[piece_captured.symbol().lower()] - symbol_to_value[piece_moved.symbol().lower()]
            # if diff < 0:
            #     # taking a piece of lower value
            #     # check if defended
            color_to_check = not piece_moved.symbol().isupper()
            if not temp.is_attacked_by(color_to_check, chess.Move.from_uci(move).to_square):
                if symbol_to_value[piece_captured.symbol().lower()] >= 3:
                    return True
        temp.push(chess.Move.from_uci(move))
    
    return False

def endgame_tactic(board, fen, eval_before_move, eval_after_move, best_move, variation):
    return total_pieces(board) < 13

def perpetual_check(board, fen, eval_before_move, eval_after_move, best_move, variation):
    temp = board.copy()
    if abs(eval_after_move) >= 30:
        return False
    for move in variation:
        temp.push(chess.Move.from_uci(move))
    if temp.can_claim_threefold_repetition():
        return True
    return False

def defense(board, fen, eval_before_move, eval_after_move, best_move, variation):
    return abs(eval_after_move) <= 30

def stalemate(board, fen, eval_before_move, eval_after_move, best_move, variation):
    temp = board.copy()   
    if abs(eval_after_move) >= 30:
        return False
    for index, move in enumerate(variation):
        temp.push(chess.Move.from_uci(move))
        if len(list(temp.legal_moves)) < 4 or temp.checkers():
            stalemate_check = temp.copy()
            for move in list(stalemate_check.legal_moves):
                stalemate_check.push(move)
                if not stalemate_check.checkers() and len(list(stalemate_check.legal_moves)) == 0:
                    return True
                stalemate_check.pop()
    return False

def attacking_f2f7(board, fen, eval_before_move, eval_after_move, best_move, variation):
    pieces = ''
    if board.turn == chess.WHITE:
        # check attack of square f7
        pieces = board.attackers(chess.WHITE, chess.F7)
    else:
        pieces = board.attackers(chess.BLACK, chess.F2)
    if len(pieces) >= 2 and total_pieces(board) >= 13:
        return True
    return False


def get_classification(board, fen, eval_before_move, eval_after_move, best_move, variation):
    classifications = set()
    print(board)
    print(fen)
    print(variation)

    if checkmate(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('CHECKMATE')
    
    if discovered_check(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('DISCOVERED CHECK')
    
    if windmill(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('WINDMILL')
    
    if sacrifice(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('SACRIFICE')
    
    if hanging_piece(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('HANGING PIECE')
    
    if endgame_tactic(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('ENDGAME TACTIC')
    
    if perpetual_check(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('PERPETUAL_CHECK')
    
    if defense(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('DEFENSE')
    
    if stalemate(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('STALEMATE')
    
    if attacking_f2f7(board, fen, eval_before_move, eval_after_move, best_move, variation):
        classifications.add('ATTACKING F2/F7')
    
    return classifications

# def get_classification(board, fen, eval_before_move, eval_after_move, best_move, variation):
#     print(board)
#     print(fen)
#     print(variation)
#     classifications = set()
#     # checkmate
#     if abs(eval_after_move) >= 90000:
#         classifications.add('CHECKMATE')
#         temp = board.copy()
#         checkmating_piece = ''
#         for index, move in enumerate(variation):
#             if index == len(variation) - 1:
#                 checkmating_piece = temp.piece_at(chess.Move.from_uci(move).from_square)
#             temp.push(chess.Move.from_uci(move))
#         if temp.is_checkmate():
#             print(checkmating_piece)
#             checking_piece = ''
#             for x in temp.checkers():
#                 checking_piece = temp.piece_at(x)
#                 print(checking_piece)
#                 if checking_piece.symbol().lower() == 'n':
#                     # this is wrong
#                     classifications.add('SMOTHERED MATE')
#                 if checking_piece.symbol() != checkmating_piece.symbol():
#                     classifications.add('DISCOVERED CHECK')
#                     print(fen)
#     # general discovered check
#     temp = board.copy()
#     discovered_check_counter = 0
#     for index, move in enumerate(variation):
#         piece_moved = temp.piece_at(chess.Move.from_uci(move).from_square)
#         temp.push(chess.Move.from_uci(move))
#         for x in temp.checkers():
#             checking_piece = temp.piece_at(x)
#             if checking_piece.symbol() != piece_moved.symbol():
#                 classifications.add('DISCOVERED CHECK')
#                 discovered_check_counter += 1
#     if discovered_check_counter >= 2:
#         classifications.add('WINDMILL')
    
#     temp = board.copy()
#     symbol_to_value = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 900000}    
#     for index, move in enumerate(variation):
#         piece_moved = temp.piece_at(chess.Move.from_uci(move).from_square)
#         if temp.piece_at(chess.Move.from_uci(move).to_square) and index % 2 == 0:
#             # this is a capture, check if material is higher in the piece_moved (this is a sacrifice)
#             # also check that it is the player's move
#             piece_captured = temp.piece_at(chess.Move.from_uci(move).to_square)
#             print(piece_captured)
#             print(piece_moved)
#             print(move)
#             diff = symbol_to_value[piece_captured.symbol().lower()] - symbol_to_value[piece_moved.symbol().lower()]
#             if diff < 0:
#                 # taking a piece of lower value
#                 # check if defended
#                 color_to_check = not piece_moved.symbol().isupper()
#                 if temp.is_attacked_by(color_to_check, chess.Move.from_uci(move).to_square):
#                     classifications.add('SACRIFICE')
#                     print("SACRIFICE")
#                 else:
#                     if symbol_to_value[piece_captured.symbol().lower()] >= 3:
#                         classifcatioons.add('HANGING PIECE')
#         temp.push(chess.Move.from_uci(move))

#     if total_pieces(board) < 13:
#         classifications.add('ENDGAME TACTIC')


#     # perpetual check
#     if abs(eval_after_move) <= 30:
#         temp = board.copy()
#         for move in variation:
#             temp.push(chess.Move.from_uci(move))
#         if temp.can_claim_threefold_repetition():
#             classifications.add('PERPETUAL CHECK')
#         else:
#             classifications.add('DEFENSE')
#         # print(classifications)
#         # print(variation)

#     temp = board.copy()   
#     for index, move in enumerate(variation):
#         temp.push(chess.Move.from_uci(move))
#         if len(list(temp.legal_moves)) < 4 or temp.checkers():
#             temp2 = temp.copy()
#             for move in list(temp2.legal_moves):
#                 temp2.push(move)
#                 if not temp2.checkers() and len(list(temp2.legal_moves)) == 0:
#                     classifications.add('STALEMATE')
#                 temp2.pop()

#     pieces = ''
#     if board.turn == chess.WHITE:
#         # check attack of square f7
#         pieces = board.attackers(chess.WHITE, chess.F7)
#     else:
#         pieces = board.attackers(chess.BLACK, chess.F2)
#     if len(pieces) >= 2:
#         classifications.add('ATTACKING F2/F7')


#     return classifications
    

with open('windmill_example.obj', 'rb') as f:
    x = pickle.load(f)
    y = x.copy()
    for num in x:
        tactic = x[num]
        board = tactic[0]
        fen = tactic[1]
        eval_before_move = tactic[2]
        eval_after_move = tactic[3]
        best_move = tactic[4]
        variation = tactic[5]
        classification = get_classification(board, fen, eval_after_move, eval_after_move, best_move, variation)
        print(classification)
        # print(classification)