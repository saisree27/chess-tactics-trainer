import chess.pgn
import chess
import pickle
import random
from stockfish import Stockfish
import logic

sf = Stockfish('../ChessTacticsTrainer/static/assets/stockfish/stockfish_20090216_x64_bmi2.exe')
sf.set_depth(10)

list_of_tactics = dict()

pgn = open("lichess_db_standard_rated_2019-07.pgn")
game = chess.pgn.read_game(pgn)

num_games = 1

while game is not None:
    # print("Game %s" % (num_games))
    game = chess.pgn.read_game(pgn)
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
            has_best = logic.check_for_best_move(board)

            if has_best:
                temp = game.board()

                best_move = ''
                variation = []
                sf.set_fen_position(temp.fen())

                best_move = sf.get_best_move()
                temp.push(chess.Move.from_uci(best_move))
                variation.append(best_move)

                for i in range(0, 8):
                    if temp.turn != board.turn:
                        has_best = True
                    else:
                        has_best = logic.check_for_best_move(temp)
                    if has_best:
                        sf.set_fen_position(temp.fen())
                        m = sf.get_best_move()
                        try:
                            temp.push(chess.Move.from_uci(m))
                        except TypeError as e:
                            # game over
                            break
                        variation.append(m)
                    else:
                        break
                
                if len(variation) % 2 == 0:
                    variation = variation[:-1]

                if len(variation) > 1:
                    if num_games in list_of_tactics:
                        list_of_tactics[num_games+random.random()] = (board, board.fen(), running_eval, new_eval, best_move, variation)
                    else:
                        list_of_tactics[num_games] = (board, board.fen(), running_eval, new_eval, best_move, variation)
        running_eval = new_eval
    num_games += 1
    # print(num_games)
    # print("NUMBER OF TACTICS GENERATED: %s" % len(list_of_tactics))

    if num_games % 1000 == 0:
        print("Processed %s games." % num_games)
        print("NUMBER OF TACTICS GENERATED: %s" % len(list_of_tactics))
        print("Dumping to pickle")
        handler = open('best_so_far_gen_july_2019.obj', 'wb')
        pickle.dump(list_of_tactics, handler)
        handler.close()
        print("Done.")




