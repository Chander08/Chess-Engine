import chess
import chess.polyglot
from chess import Move 
import table_values

class Evaluate:
    '''
    class which given a board position determines evaluation and the best move to play
    '''
    def __init__(self, board, color, transposition_table):
        self.board = board
        self.color = color
        self.opening_book1 = "/Users/suhail/Desktop/Side Projects/Chess-Engine/WeirdChessBot/StarterLichessBot/gm2600.bin"
        self.opening_book2 = "/Users/suhail/Desktop/Side Projects/Chess-Engine/WeirdChessBot/StarterLichessBot/Opening_Collection.bin"
        self.transposition_table = transposition_table
        #transposition table is a dict of {board_zobrist_key: [eval, move, depth]}

    def opening_database_moves(self):
        '''
        checks the two opening databases to see if the current board position is stored in the books. If it is, returns
        the best move according to the opening book. Otherwise returns None. 
        '''
        selected_move = None
        with chess.polyglot.open_reader(self.opening_book2) as reader:
            highest_weight = 0
            for entry in reader.find_all(self.board):
                #want top entry weight move to be selected every time
                if entry.weight > highest_weight:
                    highest_weight = entry.weight
                    selected_move = entry.move
        if selected_move != None: 
            with chess.polyglot.open_reader(self.opening_book1) as reader:
                highest_weight = 0
                for entry in reader.find_all(self.board):
                    #want top entry weight move to be selected every time
                    if entry.weight > highest_weight:
                        highest_weight = entry.weight
                        selected_move = entry.move
        return selected_move

    def minimax_alpha_beta(self, depth, alpha, beta, ownturn, max_depth): #With added alpha beta pruning
        '''
        function which finds the move which maximizes the evaluation for the given player turn. Uses the minimax algorithm 
        with alpha beta pruning. 

        Minimax is an algorithm which looks at all possible moves for each side until the max depth is reached,
        assuming that the engine and opponent play their best possible move. 

        Alpha beta pruning works so if a certain move causes the evaluation to be good enough that no other move can beat
        it or bad enough that it loses to a previously found move, that branch will be pruned and not searched faster,
        improving search efficiency

        This algorithm stores all search results in a transposition table so if the same position is reached with a 
        different move order it will not have to re-evaluate. Uses zobrist keys to have a unique identifier for the position. 
        This allows the search tree to be ordered to search the best evaluated positions first, improving efficiency.

        ownturn is boolean true if own turn
        '''
        #if board in opening book: use that
        selected_move = None
        selected_move = self.opening_database_moves()
        eval = 0
        if selected_move != None: #if found in opening book
            return eval , selected_move # will just return 0 eval since opening is usually a draw
        else:
            eval = self.move_eval()
            #selected_move = None
            potential_moves = list(self.board.legal_moves)
            #added move ordering for potential_moves here to look at likely best moves first
            potential_moves.sort(reverse = True, key = lambda x: self.order_transposition_table(x, depth))
            if (depth >= max_depth): #base case if at max depth
                #if at base of search tree for that depth then store and return the result
                zobrist_key = chess.polyglot.zobrist_hash(self.board)
                self.transposition_table[zobrist_key] = [eval, selected_move, depth]
                return eval, selected_move
            elif len(potential_moves) == 0: #base case at no possible moves
                return eval, selected_move
            elif ownturn: #own turn
                potential_moves.sort(reverse = True, key = lambda x: self.order_transposition_table(x, depth))
                eval = -99999 #own moves should maximize the eval so this is a reference
                for move in potential_moves:
                    self.board.push(move) #make the potential move
                    new_eval = self.minimax_alpha_beta(depth+1, alpha, beta, False, max_depth)[0]
                    #store the eval result
                    zobrist_key = chess.polyglot.zobrist_hash(self.board)
                    self.transposition_table[zobrist_key] = [new_eval, move, depth+1]
                    self.board.pop() #undo the move 
                    if new_eval > eval: 
                        eval = new_eval 
                        selected_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha: #if we see a move which cannot possibly be beat by another node, end search
                        return eval, selected_move
                return eval, selected_move
            else: #opponent's turn
                eval = 99999 #trying to minimize this so this is a reference
                potential_moves.sort(reverse = False, key = lambda x: self.order_transposition_table(x, depth))
                for move in potential_moves:
                    self.board.push(move) #make potential move
                    new_eval = self.minimax_alpha_beta(depth+1, alpha, beta, True, max_depth)[0]
                    #store the eval result
                    zobrist_key = chess.polyglot.zobrist_hash(self.board)
                    self.transposition_table[zobrist_key] = [new_eval, move, depth+1]
                    self.board.pop()
                    if new_eval < eval:
                        eval = new_eval
                        selected_move = move
                    beta = min(beta, eval)
                    if beta <= alpha: 
                        return eval, selected_move
                return eval, selected_move

    def order_transposition_table(self, move, depth):
        '''
        helper for the sort function which takes a given move in zobrist form and if playing that move results in a 
        transposition previously stored then it returns the prior eval if the depth is same or deeper, and if not then 
        it returns 0 eval 
        '''
        self.board.push(move)
        zobrist_key = chess.polyglot.zobrist_hash(self.board)
        self.board.pop()
        if zobrist_key in self.transposition_table:
            stored_board_calc = self.transposition_table[zobrist_key]
            stored_eval = stored_board_calc[0]
            stored_depth = stored_board_calc[2]
            if stored_depth >= depth:
                return stored_eval
        return 0 #just to make it order somewhere near the middle if not priorly stored

    def move_ordering(self, potential_moves):
        '''
        obsolete move ordering attempt prior to the transposition table. This method uses a manual attempt to order the moves
        by likely good moves rather than the transposition table method of searching the prior found best eval moves first. 
        '''
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
        '''
        looks at the state of the current board and returns an estimate of the eval. Takes into account the piece material for 
        each side, potential checkmate threats, and the piece positioning using a piece table to determine ideal placement
        
        '''
        material_advantage, total_material = self.material_values()
        return material_advantage + self.detect_checkmate() + self.piece_table_values(total_material)

    def material_values(self):
        '''
        given a board state it returns the material advantage of the given side and the total material left on the board
        '''
        own_material = 0
        opponent_material = 0
        for i in range(64):
            square = chess.SQUARES[i]
            piece = self.board.piece_type_at(square)
            if piece != None:
                if self.board.color_at(i) == self.board.turn:
                    own_material += self.piece_value(piece)
                elif self.board.color_at(i) != self.board.turn:
                    opponent_material += self.piece_value(piece)
        material_advantage = opponent_material - own_material
        total_material = own_material + opponent_material
        return material_advantage, total_material

    def piece_value(self,piece):
        '''
        given a piece, returns the material value based off of general chess considerations. 
        Can be improved by changing the material value based on amount of material remaining
        e.g. bishops worth more in endgame due to mobility
        '''
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
        '''
        detects any potential checkmates within the max depth
        '''
        potential_moves = list(self.board.legal_moves)
        if len(potential_moves) == 0 and self.board.is_check():
            if self.board.turn == self.color:
                return -999
            else:
                return 999
        return 0

    def primitive_development(self):
        '''
        obsolete method used to get the pieces to develop prior to implementing piece square tables and opening book

        tries to maximize number of potential moves so this would encourage making moves like pawns out of the way
        and pieces to more active squares. Should follow an opening book instead
        '''
        available_moves = len(list(self.board.legal_moves))
        if self.board.turn == self.color:
            return available_moves * 0.005
        else:
            return available_moves * -0.005

    def piece_table_values(self, total_material):
        '''
        given a board state, determines the positional evaluation by consulting the piece square tables
        '''
        total_material = self.material_values()[1]
        positioning_advantage = 0
        for i in range(64):
            square = chess.SQUARES[i]
            piece = self.board.piece_type_at(square)
            rank = chess.square_rank(square)
            table_y = 7 - rank #since the table values are from white perspective
            table_x = chess.square_file(square)
            if self.board.color_at(i): #for white pieces
                if piece != None:
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
            else: #if black pieces
                if piece != None:
                    if piece == chess.BISHOP:
                        positioning_advantage += table_values.bishop_eval_black()[table_y][table_x]
                    elif piece == chess.KNIGHT:
                        positioning_advantage += table_values.knight_eval_black()[table_y][table_x]
                    elif piece == chess.ROOK:
                        positioning_advantage += table_values.rook_eval_black()[table_y][table_x]
                    elif piece == chess.QUEEN:
                        positioning_advantage += table_values.queen_eval_black()[table_y][table_x]
                    if total_material >= 15: #use opening tables
                        if piece == chess.PAWN:
                            positioning_advantage += table_values.opening_pawn_eval_black()[table_y][table_x]
                        elif piece == chess.KING:
                            positioning_advantage += table_values.opening_king_eval_black()[table_y][table_x]
                    else: #using endgame tables for pawn and king since that should change
                        if piece == chess.PAWN:
                            positioning_advantage += table_values.endgame_pawn_eval_black()[table_y][table_x]
                        elif piece == chess.KING:
                            positioning_advantage += table_values.endgame_king_eval_black()[table_y][table_x]
        return 0.05*positioning_advantage
