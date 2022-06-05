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
        '''
        for playing in the command line while testing. Asks for user input and if it is a legal move, plays the move
        '''
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
        '''
        runs minimax algorithm with depth from 1 to max_depth to sort transposition table and provide speed benefits
        '''
        for depth in range(1, max_depth+1):
            eval, move = self.game_info.minimax_alpha_beta(0, -99999, 99999, True, depth)
            print("selected move is", move)
            print(eval)
            print("Depth = ", depth)
        return move

    def computer_move(self, max_depth):
        '''
        given a maximum depth, finds the best computer move for that depth. Alternative to iterative deepening.
        '''
        #eval, move = self.game_info.minimax(0)
        eval, move = self.game_info.minimax_alpha_beta(0, -99999, 99999, True, max_depth)
        print(eval)
        #self.board.push(move)
        return move

    def white_engine(self):
        '''
        CLI version of playing the computer with computer as white. Just for testing
        '''
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
        '''
        CLI version of playing the computer with computer as black. Just used for testing
        '''
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
