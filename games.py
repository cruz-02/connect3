import time
import utils
import random
from agents import MiniMaxAgent, MiniMaxAgentD, AlphaBeta, AlphaBetaD, MiniMaxAgentV2, AlphaBetaV2, MiniMaxv2D, AlphaBetav2D



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
        elif model == 'mm2':
            self.agent = MiniMaxAgentV2(player=self.ai_player)
        elif model == 'mm2D':
            self.agent = MiniMaxv2D(player=self.ai_player)
        elif model == 'ab':
            self.agent = AlphaBeta(player=self.ai_player)
        elif model == 'abD':
            self.agent = AlphaBetaD(player=self.ai_player)
        elif model == 'ab2':
            self.agent = AlphaBetaV2(player=self.ai_player)
        elif model == 'ab2D':
            self.agent = AlphaBetav2D(player=self.ai_player)
        
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
                move_str = self.agent.find_best_move(depth=15)
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
                
                # in board check, free space etc
                if not (utils.in_board(start_x, start_y) and utils.in_board(end_x, end_y) and \
                        self.board[start_y][start_x] == self.current_player and self.board[end_y][end_x] is None):
                    print("!!! Invalid Move !!!")
                    continue
                
                self.board[end_y][end_x] = self.current_player
                self.board[start_y][start_x] = None
                
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


# In games.py --  GEMINI GENERATED

class Connect3MServer(Connect3M):
    """
    Manages a game instance that communicates moves through a server.
    This version is robustly designed to ignore non-move echo messages.
    """
    def __init__(self, model, my_player_id, sock):
        super().__init__(model, human_player=my_player_id)
        self.sock = sock
        self.agent.player = my_player_id
        # Keep track of the last move we sent to ignore its echo
        self.last_move_sent = None
        print(f"Initialized server game. This client is Player {my_player_id}.")

    def _apply_local_move(self, move_str, player_id):
        """
        Applies a move string to the local board.
        Returns True on success, False on failure (invalid format).
        """
        try:
            # A valid move must be a 3-character string
            if not isinstance(move_str, str) or len(move_str) != 3:
                return False
            start_x, start_y = int(move_str[0]) - 1, int(move_str[1]) - 1
            direction = move_str[2].upper()
            dx, dy = self.agent.dirs[direction]
            end_x, end_y = start_x + dx, start_y + dy
            
            # Additional validation can be added here if needed
            self.board[end_y][end_x] = player_id
            self.board[start_y][start_x] = None
            return True
        except (ValueError, KeyError, IndexError, TypeError):
            # This will catch errors from non-move strings like "game01 black"
            return False

    def play(self):
        """
        The main game loop for a server-based game. The server dictates the flow.
        """
        print("Starting network game...")
        
        # If we are Player 0, we make the first move.
        if self.agent.player == 0:
            print("We are Player 0. Calculating the first move.")
            move_to_send = self.agent.find_best_move(depth=5)
            self._apply_local_move(move_to_send, self.agent.player)
            self.last_move_sent = move_to_send
            utils.send_move(self.sock, move_to_send)
        
        while not self.game_over:
            self.display_board()
            
            # 1. Loop until we receive a valid move from our opponent.
            print("Waiting for opponent's move...")
            while True:
                message = utils.receive_move(self.sock)

                if not message or "wins" in message.lower() or "draw" in message.lower():
                    self.game_over = True
                    print(f"Game Over. Final message: {message}")
                    break
                
                # Ignore the echo of our own last move
                if message == self.last_move_sent:
                    print(f"Ignoring echo of our own move: {message}")
                    continue

                # Try to apply the message as a move. If it works, it was the opponent's move.
                if self._apply_local_move(message, self.ai_player):
                    print(f"Successfully applied opponent's move: {message}")
                    self.agent.update_board_opp(message)
                    break # Break the inner loop and proceed to our turn
                else:
                    print(f"Ignoring non-move message from server: '{message}'")
            
            if self.game_over:
                continue

            self.display_board()

            # 2. Now it's our turn. Calculate and send our move.
            print("Opponent has moved. Calculating our response...")
            move_to_send = self.agent.find_best_move(depth=5)
            if not move_to_send:
                print("Agent has no moves. Game might be over.")
                self.game_over = True
                continue
            
            self._apply_local_move(move_to_send, self.agent.player)
            self.last_move_sent = move_to_send # Remember the move we are sending
            utils.send_move(self.sock, move_to_send)

        print("\nNetwork game has ended.")

# ----------------------------------------------------------------------
# --- NEW: Large 7x6 Grid Game Class --- Gemini Generated
# ----------------------------------------------------------------------

# python main.py --grid large
class Connect3L:
    """
    Manages the 7x6 version of the game.
    """
    def __init__(self, model, human_player):
        self.human_player = human_player
        self.ai_player = 1 - human_player
        
        # Create the 7x6 board with a centered starting configuration
        self.board = [
            [None, None, None, None, None, None, None],
            [None,0, None, None, None, 1, None],
            [None, 1, None, None, None, 0, None],
            [None, 0, None, None, None, 1, None],
            [None, 1, None, None, None, 0, None],
            [None, None, None, None, None, None, None]
        ]

        # Zobrist table must match the 7x6 grid dimensions
        self.zobrist_table = [[[random.getrandbits(64) for _ in range(6)] for _ in range(7)] for _ in range(2)]
        initial_hash = utils.calculate_initial_hashL(self.board, self.zobrist_table)
        self.board_history = {initial_hash: 1}
        
        # Instantiate the correct LARGE GRID ("L") agent
        # Note: You will need to create these "L" agent classes in agents.py

        if model == 'mmv2':
            self.agent = MiniMaxAgentV2L(player=self.ai_player, zobrist_table=self.zobrist_table)
        elif model == 'abpv2':
            self.agent = AlphaBetaV2L(player=self.ai_player, zobrist_table=self.zobrist_table)

        
        self.current_player = 0
        self.game_over = False

    def display_board(self):
        """Displays the current state of the 7x6 board."""
        print("\nCurrent Board State (7x6):")
        for row in self.board:
            display_row = ['0' if c == 0 else '1' if c == 1 else ' ' for c in row]
            print(' , '.join(display_row))
        print("-" * 25)
        
    def play(self):
        """The main game loop for the large grid version."""
        print("Welcome to Dynamic Connect-3 (Large 7x6 Grid)!")
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
                move_str = input(f"Player {player_name} (You), enter your move (e.g., '22E'): ")
            
            if not move_str:
                print("The AI has no moves and forfeits. Game over.")
                self.game_over = True
                continue

            # Perform the move
            try:
                start_x, start_y = int(move_str[0]) - 1, int(move_str[1]) - 1
                direction = move_str[2].upper()
                dx, dy = self.agent.dirs[direction]
                end_x, end_y = start_x + dx, start_y + dy
                
                # Validation using the large-grid in_boardL function
                if not (utils.in_boardL(start_x, start_y) and utils.in_boardL(end_x, end_y) and \
                        self.board[start_y][start_x] == self.current_player and self.board[end_y][end_x] is None):
                    print("!!! Invalid Move !!!")
                    continue
                
                self.board[end_y][end_x] = self.current_player
                self.board[start_y][start_x] = None
                
                # Update agent's internal board if it was a human move
                if self.current_player == self.human_player:
                    self.agent.update_board_opp(move_str)
            
            except (ValueError, KeyError, IndexError):
                print("!!! Invalid move format. Please use <x><y><direction> (e.g., '22E'). !!!")
                continue

            # Check for win using the large-grid check_winL function
            if utils.check_winL(self.board, self.current_player):
                self.game_over = True
                self.display_board()
                print(f"\nGame Over! Player {player_name} wins!")
                continue

            # Check for draw using the large-grid hash function
            current_hash = utils.calculate_initial_hashL(self.board, self.zobrist_table)
            self.board_history[current_hash] = self.board_history.get(current_hash, 0) + 1
            if self.board_history[current_hash] >= 3:
                self.game_over = True
                self.display_board()
                print("\nGame Over! It's a draw by threefold repetition.")
                continue
            
            # Switch player
            self.current_player = 1 - self.current_player

        print("\nThanks for playing!")