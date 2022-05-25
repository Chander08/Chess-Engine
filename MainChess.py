import chess as chess
import evaluate as ev
import chess.polyglot
import cProfile

class MainChess:
    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.game_info = ev.Evaluate(board, color, {}) #giving an empty dict to form the transp table

    def player_move(self, potential_moves):
        try:
            move = str(input("Enter your move in UCI format: "))
            if move == "undo":
                self.board.pop()
                self.board.pop()
                self.player_move()
                return None
            move = chess.Move.from_uci(move)
            if move in potential_moves:
                self.board.push(move)
            else: 
                self.board.push("ERROR")
        except:
            print("That cannot be accepted, try again")
            self.player_move(potential_moves)

    def iterative_deepening(self, max_depth):
        for depth in range(1, max_depth+1):
            eval, move = self.game_info.minimax_alpha_beta(0, -99999, 99999, True, depth)
            print("selected move is", move)
            print(eval)
            print("Depth = ", depth)
        return move

    def computer_move(self, max_depth):
        #eval, move = self.game_info.minimax(0)
        eval, move = self.game_info.minimax_alpha_beta(0, -99999, 99999, True, max_depth)
        print(eval)
        #self.board.push(move)
        return move

    def white_engine(self):
        potential_moves = list(self.board.legal_moves)
        while len(potential_moves) != 0:
            eval = self.computer_move(3)
            print(self.board)
            print(eval)
            potential_moves = list(self.board.legal_moves)
            if len(potential_moves) == 0:
                break
            self.player_move(potential_moves)
            print(self.board)
            potential_moves = list(self.board.legal_moves)
        print("game done!")

    def black_engine(self):
        potential_moves = list(self.board.legal_moves)
        while len(potential_moves) != 0:
            self.player_move(potential_moves)
            print(self.board)
            potential_moves = list(self.board.legal_moves)
            if len(potential_moves) == 0:
                break
            move = self.computer_move(3)
            self.board.push(move)
            print(self.board)
            potential_moves = list(self.board.legal_moves)
        print("game done!")

    def white_game(self, board):
        eval, move = self.game_info.minimax_alpha_beta(0, -99999, 99999)
        return move


#b1 = MainChess(chess.Board(), chess.WHITE)

#print(MainChess.black_engine(b1))
#board = chess.Board('rnbqkbnr/pppppppp/8/8/8/8/PPPBBPPQ/RNBQKBNR w KQkq - 0 1')
#print(board)
#board = chess.Board()
#print(board)
#board.push(chess.Move.from_uci('h2h3'))
#print(board)
#print(board.color_at(chess.SQUARES[1]))
#print(board.turn)
#board.push(chess.Move.from_uci('h2h3'))
#print(board.color_at(chess.SQUARES[1]))
#print(board.turn)
#print(chess.polyglot.zobrist_hash(board))