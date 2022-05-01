from random import randint
import chess
from chess import BaseBoard as bb
import table_values

class Evaluate:
    ## class to use things like piece value and castling or space to estimate the eval
    def __init__(self, board, max_depth, color):
        self.board = board
        self.max_depth = max_depth
        self.color = color

    def minimax(self, depth): #plan to add alpha beta after basic evaluations
        '''
        function which takes the depth and finds the maximum
        '''
        eval = self.move_eval()
        if self.color == chess.BLACK:
            eval *= -1
        selected_move = None
        potential_moves = list(self.board.legal_moves)
        if (depth >= self.max_depth) or (len(potential_moves) == 0): #base case if at max depth or no possible moves 
            return eval, selected_move
        elif self.board.turn: #white's turn
            eval = -99999 #white moves should maximize the eval so this is a reference
            for move in potential_moves:
                self.board.push(move) #make the potential move
                new_eval = self.minimax(depth+1)[0]
                self.board.pop() #if eval is lower, undo the move
                if new_eval > eval: 
                    eval = new_eval 
                    selected_move = move
            return eval, selected_move
        else: #black's turn
            eval = 99999 #trying to minimize this so this is a reference
            for move in potential_moves:
                self.board.push(move) #make potential move
                new_eval = self.minimax(depth+1)[0]
                self.board.pop()
                if new_eval < eval:
                    eval = new_eval
                    selected_move = move
            return eval, selected_move

    def minimax_alpha_beta(self, depth, alpha, beta): #With added alpha beta pruning
        '''
        function which takes the depth and finds the maximum
        '''
        eval = self.move_eval()
        selected_move = None
        potential_moves = list(self.board.legal_moves)
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
        white_material_advantage, total_material = self.material_values()
        return white_material_advantage + self.detect_checkmate() + self.piece_table_values(total_material)

    def material_values(self):
        white_material = 0
        black_material = 0
        for i in range(64):
            square = chess.SQUARES[i]
            piece = self.board.piece_type_at(square)
            if self.board.color_at(i) == chess.WHITE:
                if piece == chess.PAWN:
                    white_material += 1
                if piece == chess.KNIGHT:
                    white_material += 3
                if piece == chess.BISHOP:
                    white_material += 3
                if piece == chess.ROOK:
                    white_material += 5
                if piece == chess.QUEEN:
                    white_material += 9
            elif self.board.color_at(i) == chess.BLACK:
                if piece == chess.PAWN:
                    black_material += 1
                if piece == chess.KNIGHT:
                    black_material += 3
                if piece == chess.BISHOP:
                    black_material += 3
                if piece == chess.ROOK:
                    black_material += 5
                if piece == chess.QUEEN:
                    black_material += 9
            white_material_advantage = white_material - black_material
            total_material = white_material + black_material
        return white_material_advantage, total_material

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
                
b1 = chess.Board()
initial = Evaluate(b1, 3, chess.WHITE)
#print(Evaluate.minimax(initial, 0))

