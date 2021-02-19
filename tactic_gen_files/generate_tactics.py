import chess.pgn
import chess
import pickle
import random
from stockfish import Stockfish
import logic

sf = Stockfish('../ChessTacticsTrainer/static/assets/stockfish/stockfish_20090216_x64_bmi2.exe')
sf.set_depth(11)

list_of_tactics = dict()

# pgn = open("lichess_pgn_2021.01.26_Alexander_Beliavsky_( )_vs_Larry_Mark_Christiansen_( ).5FAgK5A7.pgn")
# pgn = open("lichess_pgn_2018.05.24_Garry_Kasparov_( )_vs_Neil_R_McDonald_( ).DLS8u6IJ.pgn")
# pgn = open("lichess_pgn_2017.09.01_Donald_Byrne_( )_vs_Robert_James_Fischer_( ).ZAMs9lOM.pgn")
# pgn = open("lichess_pgn_2015.07.14_Carlos_Torre_Repetto_( )_vs_Emanuel_Lasker_( ).RVXmQ4Y5.pgn")
# pgn = open("lichess_pgn_2019.06.22_Bogdan_Sliwa_( )_vs_Gosta_Stoltz_( ).nrf1xS9a.pgn")
# pgn = open("lichess_pgn_2021.02.09_Peter_Leko_vs_Evgeny_Ilgizovich_Bareev.pMR6AX07.pgn")
# pgn = open("lichess_pgn_2021.02.11_Svetozar_Gligoric_vs_Fridrik_Olafsson.igdANJU7.pgn")
pgn = open("lichess_db_standard_rated_2019-07.pgn")


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
            has_best = logic.check_for_best_move(board)
            # print(has_best)
            if has_best:
                temp = game.board()

                best_move = ''
                variation = []
                sf.set_fen_position(temp.fen())

                best_move = sf.get_best_move()
                temp.push(chess.Move.from_uci(best_move))
                variation.append(best_move)

                for i in range(0, 9):
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

                if len(variation) > 1 or not temp.is_checkmate():
                    if num_games in list_of_tactics:
                        list_of_tactics[num_games+random.random()] = (board, board.fen(), running_eval, new_eval, best_move, variation)
                    else:
                        list_of_tactics[num_games] = (board, board.fen(), running_eval, new_eval, best_move, variation)
        running_eval = new_eval
    num_games += 1
    game = chess.pgn.read_game(pgn)
    # print(num_games)
    # print("NUMBER OF TACTICS GENERATED: %s" % len(list_of_tactics))

    if num_games % 100 == 0:
        # print("Processed %s games." % num_games)
        print("NUMBER OF TACTICS GENERATED: %s" % len(list_of_tactics), end="\r")
        # print("Dumping to pickle")
        handler = open('JULY 2019 FINAL (TO BE CLASSIFIED).obj', 'wb')
        # print(list_of_tactics)
        pickle.dump(list_of_tactics, handler)
        handler.close()
        # print("Done.")