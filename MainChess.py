import chess as chess
import evaluate as ev

class MainChess:
    def __init__(self, board, max_depth, color):
        self.board = board
        self.depth = max_depth
        self.color = color
        self.game_info = ev.Evaluate(board, max_depth, color)

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

    def computer_move(self):
        #eval, move = self.game_info.minimax(0)
        eval, move = self.game_info.minimax_alpha_beta(0, -99999, 99999, True)
        print(eval)
        #self.board.push(move)
        return move

    def white_engine(self):
        potential_moves = list(self.board.legal_moves)
        while len(potential_moves) != 0:
            eval = self.computer_move()
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
            eval = self.computer_move()
            print(self.board)
            print(eval*-1)
            potential_moves = list(self.board.legal_moves)
        print("game done!")

    def white_game(self, board):
        eval, move = self.game_info.minimax_alpha_beta(0, -99999, 99999)
        return move


#b1 = MainChess(chess.Board(), 4, chess.WHITE)

#print(MainChess.white_engine(b1))
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
