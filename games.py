import time
import utils
import random
from agents import MiniMaxAgent, MiniMaxAgentD



class Connect3M:
    def __init__(self, model, human_player):
        self.human_player = human_player
        self.ai_player = 1 - human_player
        
        self.board = [
            [0, None, None, None, 1],
            [1, None, None, None, 0],
            [0, None, None, None, 1],
            [1, None, None, None, 0],
        ]
        self.zobrist_table = [[[random.getrandbits(64) for _ in range(5)] for _ in range(4)] for _ in range(2)]
        initial_hash = utils.calculate_initial_hash(self.board, self.zobrist_table)
        self.board_history = {initial_hash: 1}
        
        if model == 'mm':
            self.agent = MiniMaxAgent(player=self.ai_player)
        elif model == 'mmD':
            self.agent = MiniMaxAgentD(player=self.ai_player)
        self.current_player = 0
        self.game_over = False

    def display_board(self):
        print("\nCurrent Board State:")
        for row in self.board:
            display_row = ['0' if c == 0 else '1' if c == 1 else ' ' for c in row]
            print(' , '.join(display_row))
        print("-" * 20)
        
    def play(self):
        print("Welcome to Dynamic Connect-3!")
        print(f"You are Player {self.human_player}. The AI is Player {self.ai_player}.")
        
        while not self.game_over:
            self.display_board()
            player_name = "White (0)" if self.current_player == 0 else "Black (1)"
            move_str = None
            
            if self.current_player == self.ai_player:
                print(f"\nPlayer {player_name} (AI) is thinking...")
                move_str = self.agent.find_best_move(depth=4)
                print(f"AI chose move: {move_str}")
            else:
                move_str = input(f"Player {player_name} (You), enter your move (e.g., '14E'): ")
            
            if not move_str:
                print("The AI has no moves and forfeits. Game over.")
                self.game_over = True
                continue

            # Perform the move
            try:
                start_x, start_y = int(move_str[0]) - 1, int(move_str[1]) - 1
                direction = move_str[2].upper()
                dx, dy = self.agent.dirs[direction] # Use agent's dirs
                end_x, end_y = start_x + dx, start_y + dy
                
                # Basic validation
                if not (utils.in_board(start_x, start_y) and utils.in_board(end_x, end_y) and \
                        self.board[start_y][start_x] == self.current_player and self.board[end_y][end_x] is None):
                    print("!!! Invalid Move !!!")
                    continue
                
                self.board[end_y][end_x] = self.current_player
                self.board[start_y][start_x] = None
                
                # Update human player's board in agent
                if self.current_player == self.human_player:
                    self.agent.update_board_opp(move_str)
            
            except (ValueError, KeyError, IndexError):
                print("!!! Invalid move format. Please use <x><y><direction> (e.g., '14E'). !!!")
                continue

            # Check for win
            if utils.check_win(self.board, self.current_player):
                self.game_over = True
                self.display_board()
                print(f"\nGame Over! Player {player_name} wins!")
                continue

            # Check for draw
            current_hash = utils.calculate_initial_hash(self.board, self.zobrist_table)
            self.board_history[current_hash] = self.board_history.get(current_hash, 0) + 1
            if self.board_history[current_hash] >= 3:
                self.game_over = True
                self.display_board()
                print("\nGame Over! It's a draw by threefold repetition.")
                continue
            
            # Switch player
            self.current_player = 1 - self.current_player

        print("\nThanks for playing!")
