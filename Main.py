import chess as chess
import evaluate as ev

class Main:
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
        eval, move = self.game_info.minimax_alpha_beta(0, -99999, 99999)
        self.board.push(move)
        return eval

    def game(self):
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

b1 = Main(chess.Board(), 4, chess.WHITE)

print(Main.game(b1))