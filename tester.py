import chess
import table_values

cobj = chess.Board()
for i in range(64):
    square = chess.SQUARES[i]
    piece = cobj.piece_type_at(square)
    rank = 7 - chess.square_rank(square)
    file = chess.square_file(square)

    if cobj.color_at(i) == chess.WHITE:
        if piece == chess.PAWN:
            print(i)
            print("rank, file = ", rank, file)
            print(table_values.opening_pawn_eval_white()[rank][file])
    
