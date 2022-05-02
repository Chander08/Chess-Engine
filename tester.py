import chess
import table_values

# cobj = chess.Board()
# for i in range(64):
#     square = chess.SQUARES[i]
#     piece = cobj.piece_type_at(square)
#     rank = 7 - chess.square_rank(square)
#     file = chess.square_file(square)

#     if cobj.color_at(i) == chess.WHITE:
#         if piece == chess.PAWN:
#             print(i)
#             print("rank, file = ", rank, file)
#             print(table_values.opening_pawn_eval_black()[rank][file])
    
import chess.polyglot

board = chess.Board()
move = chess.Move.from_uci("h2h4")
board.push(move)

book1 = "/Users/suhail/Desktop/Side Projects/Chess-Engine/Chess-Engine/gm2600.bin"
book2 = "/Users/suhail/Desktop/Side Projects/Chess-Engine/Chess-Engine/Opening_Collection.bin"

def opening_move():
    with chess.polyglot.open_reader(book1) as reader:
        highest_weight = 0
        selected_move = "boo"
        for entry in reader.find_all(board):
            #want top entry weight move to be selected every time
            print(entry.move, entry.weight, entry.learn)
            if entry.weight > highest_weight:
                highest_weight = entry.weight
                selected_move = entry.move
        return selected_move
        
print(opening_move())


