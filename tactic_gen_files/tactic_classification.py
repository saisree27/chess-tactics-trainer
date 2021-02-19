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
            # print(piece_captured)
            # print(piece_moved)
            # print(move)
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
            # print(piece_captured)
            # print(piece_moved)
            # print(move)
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

def opening_tactic(board, fen, eval_before_move, eval_after_move, best_move, variation):
    return total_pieces(board) > 13

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

def check_back_rank_possibility(board, turn):
    # returns a set
    # contains  1 if white has a weak back rank (king is on g1/h1/b1/a1 and kingside/queenside pawns 2nd rank)
    # contains -1 if black has a weak back rank (king g8/h8/b8/a8 and kingside/queenside pawns 2nd rank)
    # empty set if neither

    results = set()
    g1 = board.piece_at(chess.G1).symbol() if board.piece_at(chess.G1) else 'X'
    h1 = board.piece_at(chess.H1).symbol() if board.piece_at(chess.H1) else 'X'
    f2 = board.piece_at(chess.F2).symbol() if board.piece_at(chess.F2) else 'X'
    g2 = board.piece_at(chess.G2).symbol() if board.piece_at(chess.G2) else 'X'
    h2 = board.piece_at(chess.H2).symbol() if board.piece_at(chess.H2) else 'X'

    b1 = board.piece_at(chess.B1).symbol() if board.piece_at(chess.B1) else 'X'
    a1 = board.piece_at(chess.A1).symbol() if board.piece_at(chess.A1) else 'X'
    a2 = board.piece_at(chess.A2).symbol() if board.piece_at(chess.A2) else 'X'
    b2 = board.piece_at(chess.B2).symbol() if board.piece_at(chess.B2) else 'X'
    c2 = board.piece_at(chess.C2).symbol() if board.piece_at(chess.C2) else 'X'

    g8 = board.piece_at(chess.G8).symbol() if board.piece_at(chess.G8) else 'X'
    h8 = board.piece_at(chess.H8).symbol() if board.piece_at(chess.H8) else 'X'
    f7 = board.piece_at(chess.F7).symbol() if board.piece_at(chess.F7) else 'X'
    g7 = board.piece_at(chess.G7).symbol() if board.piece_at(chess.G7) else 'X'
    h7 = board.piece_at(chess.H7).symbol() if board.piece_at(chess.H7) else 'X'

    b8 = board.piece_at(chess.B8).symbol() if board.piece_at(chess.B8) else 'X'
    a8 = board.piece_at(chess.A8).symbol() if board.piece_at(chess.A8) else 'X'
    a7 = board.piece_at(chess.A7).symbol() if board.piece_at(chess.A7) else 'X'
    b7 = board.piece_at(chess.B7).symbol() if board.piece_at(chess.B7) else 'X'
    c7 = board.piece_at(chess.C7).symbol() if board.piece_at(chess.C7) else 'X'

    # checking white's kingside
    if g1 == "K":
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.F2) or f2 == "P"
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.G2) or g2 == "P"
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.H2) or h2 == "P"
        if squares_controlled:
            results.add(1)
    if h1 == "K":
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.G2) or g2 == "P"
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.H2) or h2 == "P"
        if squares_controlled:
            results.add(1)
    # checking white's queenside
    if b1 == "K":
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.A2) or a2 == "P"
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.B2) or b2 == "P"
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.C2) or c2 == "P"
        if squares_controlled:
            results.add(1)
    if a1 == "K":
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.A2) or a2 == "P"
        squares_controlled = board.is_attacked_by(chess.BLACK, chess.B2) or b2 == "P"
        if squares_controlled:
            results.add(1)
    # checking black's kingside
    if g8 == "k":
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.F7) or f7 == "p"
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.G7) or g7 == "p"
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.H7) or h7 == "p"
        if squares_controlled:
            results.add(-1)
    if h8 == "k":
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.G7) or g7 == "p"
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.H7) or h7 == "p"
        if squares_controlled:
            results.add(-1)
    # checking black's queenside
    if b8 == "k":
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.A7) or a7 == "p"
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.B7) or b7 == "p"
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.C7) or c7 == "p"
        if squares_controlled:
            results.add(-1)
    if a8 == "k":
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.A7) or a7 == "p"
        squares_controlled = board.is_attacked_by(chess.WHITE, chess.B7) or b7 == "p"
        if squares_controlled:
            results.add(-1)

    if turn == chess.WHITE:
        return -1 in results
    elif turn == chess.BLACK:
        return 1 in results
    else:
        # print(turn)
        return -99

def back_rank_search(board, depth, perspective):
    back_rank_valid = check_back_rank_possibility(board, perspective)
    terminal = board.is_checkmate()
    if terminal and back_rank_valid:
        return True
    if terminal or not back_rank_valid:
        return False    
    if depth <= 0:
        return False
    result = False
    for move in board.legal_moves:
        board.push(move)
        result = back_rank_search(board, depth - 1, perspective)
        board.pop()
        if result:
            return True
    return False

def back_rank(board, fen, eval_before_move, eval_after_move, best_move, variation):
    temp = board.copy()
    for move in variation:
        temp.push(chess.Move.from_uci(move))
    if temp.is_checkmate() and check_back_rank_possibility(temp, board.turn):
        return True
    else:
        # tree search from end of variation
        return back_rank_search(board, 3, board.turn)

    

def get_classification(board, fen, eval_before_move, eval_after_move, best_move, variation):
    classifications = set()
    # print(board)
    # print(fen)
    # print(variation)

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
    
    if check_back_rank_possibility(board, board.turn):
        # search for back rank
        if back_rank(board, fen, eval_before_move, eval_after_move, best_move, variation):
            classifications.add('BACK RANK')

    return classifications

def classify_tactics(filename):
    tactics_with_classifications = dict()
    with open(filename, 'rb') as f:
        x = pickle.load(f)
        counter = 0
        for num in x:
            counter += 1
            print(counter, end='\r')
            tactic = x[num]
            board = tactic[0]
            fen = tactic[1]
            eval_before_move = tactic[2]
            eval_after_move = tactic[3]
            best_move = tactic[4]
            variation = tactic[5]
            classification = get_classification(board, fen, eval_after_move, eval_after_move, best_move, variation)
            # print(classification)
            tactics_with_classifications[num] = (board, fen, eval_before_move, eval_after_move, best_move, variation, classification)
            
            # print(classification)
    handler = open('JULY 2019 FINAL WITH CLASSIFICATIONS.obj', 'wb')
    pickle.dump(tactics_with_classifications, handler)
    handler.close()
# board = chess.Board("r1bq1rk1/ppppbpp1/2n2n1p/4p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 7")
# print(check_back_rank_possibility(board, board.turn))

classify_tactics("JULY 2019 FINAL (TO BE CLASSIFIED).obj")