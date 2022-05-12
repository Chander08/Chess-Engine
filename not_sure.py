import chess as chess
from chess import Move 
#just using this file to try things before putting it in the other code

board = chess.Board()
print(board.legal_moves)
moves = list(board.legal_moves)
move = str(input("Enter your move in UCI format: "))
move = chess.Move.from_uci(move)
board.push(move)
if board.gives_check(move):
    print("HELLOA")
print(board)
print(move.promotion)
print(move.from_square)
# lister = list(board.legal_moves)
# print(chess.color_at(chess.SQUARES(1)))
# print(board.fullmove_number)
# board.push_san('e4')
# print(board.turn)
# board.push_san('e5')
# print(board.turn)
# board.push_san('Qh5')
# board.push_san('Nc6')
# board.push_san('Bc4')
# print("pls")
# print(board.turn)
# board.push_san('Nf6')
# print(chess.WHITE)
# #
# print(board)

# print(board.legal_moves)
# print((board.legal_moves.count()))

#need min max algorithm for selecting moves
#need to alpha beta prune for runtime
#make classes (OOP)

#plan: start with an evaluation function which returns some number for winning or losing position
#this function uses criteria like pieces more than opponent, possible moves, checkmate possibility, 
#opening book, endgame stuff, castling good, 
#loop through all possible moves, maximizing eval for computer turn, minimizing eval for human turn
#add alpha beta pruning to cut off branches which can lead to losing positions