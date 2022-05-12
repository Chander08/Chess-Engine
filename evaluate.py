from random import randint
import chess
import chess.polyglot
from chess import Move 
import table_values

class Evaluate:
    ## class to use things like piece value and castling or space to estimate the eval
    def __init__(self, board, max_depth, color):
        self.board = board
        self.max_depth = max_depth
        self.color = color
        self.opening_book1 = "/Users/suhail/Desktop/Side Projects/Chess-Engine/Chess-Engine/gm2600.bin"
        self.opening_book2 = "/Users/suhail/Desktop/Side Projects/Chess-Engine/Chess-Engine/Opening_Collection.bin"

    def opening_database_moves(self):
        selected_move = None
        with chess.polyglot.open_reader(self.opening_book1) as reader:
            highest_weight = 0
            for entry in reader.find_all(self.board):
                #want top entry weight move to be selected every time
                if entry.weight > highest_weight:
                    highest_weight = entry.weight
                    selected_move = entry.move
        return selected_move

    def minimax_alpha_beta(self, depth, alpha, beta): #With added alpha beta pruning
        '''
        function which takes the depth and finds the maximum
        '''
        #if board in opening book: use that
        selected_move = None
        selected_move = self.opening_database_moves()
        eval = 0
        if selected_move != None:
            return eval , selected_move # will just return 0 eval since opening is usually a draw
        else:
            eval = self.move_eval()
            selected_move = None
            potential_moves = list(self.board.legal_moves)
            potential_moves = self.move_ordering(potential_moves)
            #add move ordering for potential_moves here to look at likely best moves first
            if (depth >= self.max_depth) or (len(potential_moves) == 0): #base case if at max depth or no possible moves 
                return eval, selected_move
            elif self.board.turn: #white's turn
                eval = -99999 #white moves should maximize the eval so this is a reference
                for move in potential_moves:
                    self.board.push(move) #make the potential move
                    new_eval = self.minimax_alpha_beta(depth+1, alpha, beta)[0]
                    self.board.pop() #if eval is lower, undo the move 
                    if new_eval > eval: 
                        eval = new_eval 
                        selected_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha: #if we see a move which cannot possibly be beat by another node, end search
                        return eval, selected_move
                return eval, selected_move
            else: #black's turn
                eval = 9999 #trying to minimize this so this is a reference
                for move in potential_moves:
                    self.board.push(move) #make potential move
                    new_eval = self.minimax_alpha_beta(depth+1, alpha, beta)[0]
                    self.board.pop()
                    if new_eval < eval:
                        eval = new_eval
                        selected_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        return eval, selected_move
                return eval, selected_move

    def move_ordering(self, potential_moves):
        #take all potential moves and order it so that likely best moves are given first
        #these moves can be advantageous piece exchanges, promotions, castling, giving checks, making pins, escaping pins etc
        best_moves = []
        #print("calls")
        for move in potential_moves:
            if self.board.gives_check(move):
                potential_moves.remove(move)
                best_moves.append(move)
            elif move.promotion is not None:
                potential_moves.remove(move)
                best_moves.append(move)
            elif self.board.is_castling(move):
                potential_moves.remove(move)
                best_moves.append(move)
            elif self.board.is_en_passant(move): #gotta love en passant
                potential_moves.remove(move)
                best_moves.append(move)
            elif self.board.is_capture(move):
                #if trading low value piece for high value then probably a good move
                captured_value = self.piece_value(self.board.piece_at(move.to_square))
                capturing_value = self.piece_value(self.board.piece_at(move.from_square))
                if capturing_value <= captured_value:
                    potential_moves.remove(move)
                    best_moves.append(move)
        best_moves.extend(potential_moves)
        return best_moves

    def move_eval(self):
        #looks at the state of the current board given by the minimax algorithm and returns an estimate of the eval:
        #eval planned to be positive if white is winning and negative if black is winning
        
        #piece_values first: count number of pieces
        #then add castle bonus
        #check bad, checkmate check
        #add more potential moves bonus
        #add pin bonus or getting pinned minus
        #if board in opening database:
        #use opening
        material_advantage, total_material = self.material_values()
        return material_advantage + self.detect_checkmate() + self.piece_table_values(total_material)

    def material_values(self):
        own_material = 0
        opponent_material = 0
        for i in range(64):
            square = chess.SQUARES[i]
            piece = self.board.piece_type_at(square)
            if self.board.color_at(i) == self.board.turn:
                own_material += self.piece_value(piece)
            elif self.board.color_at(i) != self.board.turn:
                opponent_material += self.piece_value(piece)
            material_advantage = own_material - opponent_material
            total_material = own_material + opponent_material
        return material_advantage, total_material

    def piece_value(self,piece):
        #defined based on general chess considerations
        material = 0
        if piece == chess.PAWN:
            material = 1
        elif piece == chess.KNIGHT:
            material = 3
        elif piece == chess.BISHOP:
            material = 3
        elif piece == chess.ROOK:
            material = 5
        elif piece == chess.QUEEN:
            material = 9
        return material

    def detect_checkmate(self):
        potential_moves = list(self.board.legal_moves)
        if len(potential_moves) == 0 and self.board.is_check():
            if self.board.turn == self.color:
                return -999
            else:
                return 999
        return 0

    def primitive_development(self):
        #tries to maximize number of potential moves so this would encourage making moves like pawns out of the way
        #and pieces to more active squares. Should follow an opening book instead
        #should maximize moves for all pieces individually, not just over all
        available_moves = len(list(self.board.legal_moves))
        if self.board.turn == self.color:
            return available_moves * 0.005
        else:
            return available_moves * -0.005

    def piece_table_values(self, total_material):
        total_material = self.material_values()[1]
        positioning_advantage = 0
        for i in range(64):
            square = chess.SQUARES[i]
            piece = self.board.piece_type_at(square)
            rank = chess.square_rank(square)
            table_y = 7 - rank #since the table values are from white perspective
            table_x = chess.square_file(square)
            if self.board.color_at(i) == chess.WHITE:
                if piece == chess.BISHOP:
                    positioning_advantage += table_values.bishop_eval_white()[table_y][table_x]
                elif piece == chess.KNIGHT:
                    positioning_advantage += table_values.knight_eval_white()[table_y][table_x]
                elif piece == chess.ROOK:
                    positioning_advantage += table_values.rook_eval_white()[table_y][table_x]
                elif piece == chess.QUEEN:
                    positioning_advantage += table_values.queen_eval_white()[table_y][table_x]
                if total_material >= 15: #use opening tables
                    if piece == chess.PAWN:
                        positioning_advantage += table_values.opening_pawn_eval_white()[table_y][table_x]
                    elif piece == chess.KING:
                        positioning_advantage += table_values.opening_king_eval_white()[table_y][table_x]
                else: #using endgame tables for pawn and king since that should change
                    if piece == chess.PAWN:
                        positioning_advantage += table_values.endgame_pawn_eval_white()[table_y][table_x]
                    elif piece == chess.KING:
                        positioning_advantage += table_values.endgame_king_eval_white()[table_y][table_x]
            elif self.board.color_at(i) == chess.WHITE: #if pieces are black
                if piece == chess.BISHOP:
                    positioning_advantage -= table_values.bishop_eval_black()[table_y][table_x]
                elif piece == chess.KNIGHT:
                    positioning_advantage -= table_values.knight_eval_black()[table_y][table_x]
                elif piece == chess.ROOK:
                    positioning_advantage -= table_values.rook_eval_black()[table_y][table_x]
                elif piece == chess.QUEEN:
                    positioning_advantage -= table_values.queen_eval_black()[table_y][table_x]
                if total_material >= 15: #use opening tables
                    if piece == chess.PAWN:
                        positioning_advantage -= table_values.opening_pawn_eval_black()[table_y][table_x]
                    elif piece == chess.KING:
                        positioning_advantage -= table_values.opening_king_eval_black()[table_y][table_x]
                else: #using endgame tables for pawn and king since that should change
                    if piece == chess.PAWN:
                        positioning_advantage -= table_values.endgame_pawn_eval_black()[table_y][table_x]
                    elif piece == chess.KING:
                        positioning_advantage -= table_values.endgame_king_eval_black()[table_y][table_x]
        return 0.1*positioning_advantage
