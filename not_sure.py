import chess as chess

board = chess.Board()

board.push_san('e4') 
board.push_san('e5')
board.push_san('Nf3')
board.push_san('d5')
board.push_san('d3')
board.push_san('h5')
board.push_san('c4')
board.push_san('dxc4')
board.push_san('e5')
print(board)

print(board.legal_moves)

#need min max algorithm for selecting moves
#need to alpha beta prune for runtime
#make classes (OOP)
def piece_eval(piece):
    Pawn = 1
    Knight = 3
    Bishop = 3
    Rook = 5
    Queen = 9
    King = 10000

#plan: start with an evaluation function which returns some number for winning or losing position
#this function uses criteria like pieces more than opponent, possible moves, checkmate possibility, 
#opening book, endgame stuff, castling good, 
#loop through all possible moves, maximizing eval for computer turn, minimizing eval for human turn
#add alpha beta pruning to cut off branches which can lead to losing positions