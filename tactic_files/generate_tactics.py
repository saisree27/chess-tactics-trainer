import chess.pgn
import chess
import pickle
import random
from stockfish import Stockfish
import logic

sf = Stockfish('../ChessTacticsTrainer/static/assets/stockfish/stockfish_20090216_x64_bmi2.exe')
sf.set_depth(10)

list_of_tactics = dict()

pgn = open("lichess_db_standard_rated_2020-01.pgn/lichess_db_standard_rated_2020-01.pgn")

game = chess.pgn.read_game(pgn)
num_games = 0

while game is not None:
    # print("here")
    num_games += 1
    print("Game %s" % (num_games), end="\r")
    board = game.board()
    running_eval = 30

    for move in game.mainline_moves():
        game = game.next()
        board = game.board()

        try:
            new_eval = game.eval().white().score(mate_score=logic.MATE_SCORE)
        except AttributeError as e:
            break

        if logic.puzzle(running_eval, new_eval):
            # print('got_puzzle')
            best_move, has_best = logic.check_for_best_move(board)
            # print(has_best)
            if has_best:
                temp = game.board()

                variation = []

                temp.push(best_move)
                variation.append(str(best_move))

                for i in range(0, 9):
                    if temp.turn != board.turn:
                        has_best = True
                        sf.set_fen_position(temp.fen())
                        m = sf.get_best_move()
                        move = chess.Move.from_uci(m) if m is not None else None
                    else:
                        move, has_best = logic.check_for_best_move(temp)
                    if has_best:
                        try:
                            temp.push(move)
                        except Exception as e:
                            # game over
                            break
                        variation.append(str(move))
                    else:
                        break
                
                if len(variation) % 2 == 0:
                    variation = variation[:-1]

                if len(variation) > 1:
                    print(board.fen(), running_eval, new_eval, str(best_move), variation)
                    if num_games in list_of_tactics:
                        list_of_tactics[num_games+random.random()] = (board, board.fen(), running_eval, new_eval, str(best_move), variation)
                    else:
                        list_of_tactics[num_games] = (board, board.fen(), running_eval, new_eval, str(best_move), variation)
        running_eval = new_eval
    # num_games += 1
    game = chess.pgn.read_game(pgn)
    # print(num_games)
    # print("NUMBER OF TACTICS GENERATED: %s" % len(list_of_tactics))

    if num_games % 100 == 0:
        # print("Processed %s games." % num_games)
        print("NUMBER OF TACTICS GENERATED: %s" % len(list_of_tactics))
        print("Dumping to pickle")
        handler = open('jan_2020_without_classifications_no_one_movers.obj', 'wb')
        # print(list_of_tactics)
        pickle.dump(list_of_tactics, handler)
        handler.close()
        # print("Done.")