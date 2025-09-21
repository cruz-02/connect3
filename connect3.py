import time


# ocupo dos funciones, 'move' simula como si fuera a hacer el movimiento. 'actions' genera las posibles acciones conforme al state

class MiniMaxAgent:
    def __init__(self, player):
        self.player = player # 0/white or 1/black
        # list/dict tracking pieces?
        if player == 0:
            self.my_pieces = [(1,1),(1,3),(5,2),(5,4)] # X Y
            self.op_pieces =  [(1,2),(1,4),(5,1),(5,3)] # X Y
        else:
            self.op_pieces = [(1,1),(1,3),(5,2),(5,4)] # X Y
            self.my_pieces =  [(1,2),(1,4),(5,1),(5,3)] # X Y
        self.dirs = ['N','S','E','W']

    def heuristic(self, state):
        """
        calculates (naive )heuristic
        """
        pass

    # will it be faster if i combine gen and val in single func
    def val_actions(self, state, action):
        """
        Validates that action is legal
        
        """



        # Validate new position
        if not self._is_valid_coordinate(new_y, new_x):
            return False, "Move is off the board."

        if self.board[new_y][new_x] is not None:
            return False, "The destination square is not empty."


        pass

    def in_board(self, x, y):
        return 0 <= y < 4 and 0 <= x < 5



    def gen_actions(self, state, coords):
        """
        generates all possible actions given a state
        """

        actions = []

        # find/fromlist of pieces gen possible actions
        for x,y in coords:
            for dir in self.dirs:

                new_x, new_y = x, y
                if dir == 'N':
                    new_y -= 1
                elif dir == 'S':
                    new_y += 1
                elif dir == 'E':
                    new_x += 1
                elif dir == 'W':
                    new_x -= 1
                
                if self.in_board(new_x, new_y) and state[new_y][new_x] is not None:
                    actions.append((new_x,new_y))
        
        return actions

    def make_move(self, state, action):
        """
        simulates new board given a state and action
        """

        x, y = action
        state[y][x] = self.current_player
        state[y][x] = None
        
        return True, f"Move {move_str} successful."



    def is_terminal(self, state):
        pass
    


    def minimax(self, state, depth, max_player):
        #TODO: double ckeck min max logic
        #terminal state or depth cutoff
        if self.is_terminal(state) or depth == 0: 
            return self.heuristic(state)
        
        # we gen actions?

        if max_player:
            max_eval = float('-inf')
            for action in self.actions(state):
                eval = self.minimax(self.make_move(state, action), depth-1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for action in self.actions(state):
                eval = self.minimax(self.make_move(state, action), depth-1, True)
                min_eval= min(min_eval, eval)
            return min_eval

    def find_best_move(self, state, depth):
        """
        logic to find best action
        """



        # gen moves
        # minimax
        # update my self.pieces only here wiht the best action
        # return best action

        pass

    #TODO: func update board that updates self.board and op_pieces when oponent moves


class DynamicConnect3:
    """
    A class to represent and play the Dynamic Connect-3 game.

    The game is played on a 4x5 grid (4 rows, 5 columns).
    Player 0: White ('O')
    Player 1: Black ('X')
    """

    def __init__(self):
        """
        Initializes the game state, including the board, current player,
        and history for draw detection.
        """
        # Board setup: None represents an empty square
        self.board = [
            [0, None, None, None, 1],
            [1, None, None, None, 0],
            [0, None, None, None, 1],
            [1, None, None, None, 0],
        ]
        self.current_player = 0  # White starts
        self.board_history = {} # For checking threefold repetition draw
        self.game_over = False
        self.winner = None

    def _get_board_state_tuple(self):
        """Converts the current board state to a hashable tuple."""
        return tuple(tuple(row) for row in self.board)

    def display_board(self):
        """
        Prints the current state of the board to the console, formatted
        as a comma-separated matrix.
        """
        print("\nCurrent Board State:")
        for row in self.board:
            # Format each cell for display
            display_row = []
            for cell in row:
                if cell == 0:
                    display_row.append('0')
                elif cell == 1:
                    display_row.append('1')
                else:
                    display_row.append(' ') # Whitespace for empty cells
            print(' , '.join(display_row))
        print("-" * 20)

    def _is_valid_coordinate(self, y, x):
        """Checks if a given 0-indexed coordinate is within the board bounds."""
        return 0 <= y < 4 and 0 <= x < 5

    def make_move(self, move_str):
        """
        Parses a move string, validates it, and updates the board state.
        Args:
            move_str (str): The move in the format '<x><y><direction>', e.g., '14E'.
        Returns:
            bool: True if the move was successful, False otherwise.
            str: A message describing the outcome or error.
        """
        if len(move_str) != 3:
            return False, "Invalid move format. Please use <x><y><direction> (e.g., '14E')."

        try:
            x = int(move_str[0]) - 1
            y = int(move_str[1]) - 1
            direction = move_str[2].upper()
        except ValueError:
            return False, "Invalid coordinates. x and y must be numbers."

        # Validate start position
        if not self._is_valid_coordinate(y, x):
            return False, "Starting position is off the board."
        
        if self.board[y][x] is None:
            return False, "The selected square is empty."
            
        if self.board[y][x] != self.current_player:
            return False, "That is not your piece to move."

        # Calculate new position
        new_y, new_x = y, x
        if direction == 'N':
            new_y -= 1
        elif direction == 'S':
            new_y += 1
        elif direction == 'E':
            new_x += 1
        elif direction == 'W':
            new_x -= 1
        else:
            return False, "Invalid direction. Use N, S, E, or W."

        # Validate new position
        if not self._is_valid_coordinate(new_y, new_x):
            return False, "Move is off the board."

        if self.board[new_y][new_x] is not None:
            return False, "The destination square is not empty."

        # If all checks pass, perform the move
        self.board[new_y][new_x] = self.current_player
        self.board[y][x] = None
        
        return True, f"Move {move_str} successful."

    def check_win(self):
        """
        Checks if the current player has won by getting three pieces in a row.
        """
        player = self.current_player
        # Check horizontal
        for y in range(4):
            for x in range(3):
                if self.board[y][x] == player and self.board[y][x+1] == player and self.board[y][x+2] == player:
                    return True

        # Check vertical
        for y in range(2):
            for x in range(5):
                if self.board[y][x] == player and self.board[y+1][x] == player and self.board[y+2][x] == player:
                    return True

        # Check diagonal (down-right)
        for y in range(2):
            for x in range(3):
                if self.board[y][x] == player and self.board[y+1][x+1] == player and self.board[y+2][x+2] == player:
                    return True

        # Check diagonal (down-left)
        for y in range(2):
            for x in range(2, 5):
                if self.board[y][x] == player and self.board[y+1][x-1] == player and self.board[y+2][x-2] == player:
                    return True
        
        return False

    def check_draw(self):
        """
        Checks for a draw by threefold repetition.
        """

        # TODO: REPLACE FOR ZOBRIST HASHING
        board_state = self._get_board_state_tuple()
        count = self.board_history.get(board_state, 0)
        self.board_history[board_state] = count + 1
        
        if self.board_history[board_state] >= 3:
            return True
        return False

    def switch_player(self):
        """Switches the turn to the other player."""
        self.current_player = 1 if self.current_player == 0 else 0

    def play(self):
        """
        The main game loop that controls the flow of the game.
        """
        print("Welcome to Dynamic Connect-3!")
        print("Player 0 is White, Player 1 is Black.")
        print("Moves are entered as <x><y><direction>, e.g., '14E' to move piece at col 1, row 4 East.")

        while not self.game_over:
            self.display_board()
            player_name = "White (0)" if self.current_player == 0 else "Black (1)"

            if self.current_player == ai_player:
                print(f"Player {player_name} (AI) is thinking...")
                move = agent.find_best_move(copy.deepcopy(self), depth=4)
                print(f"AI chose move: {move}")
            else:
                move = input(f"Player {player_name}, enter your move: ")

            
            success, message = self.make_move(move)
            print(message)

            if success:
                # Check for win condition
                if self.check_win():
                    self.game_over = True
                    self.winner = self.current_player
                    self.display_board()
                    print(f"\nGame Over! Player {player_name} wins!")
                    continue # End loop

                # Check for draw condition
                if self.check_draw():
                    self.game_over = True
                    self.display_board()
                    print("\nGame Over! It's a draw by threefold repetition.")
                    continue # End loop
                
                self.switch_player()

        print("\nThanks for playing!")







if __name__ == '__main__':
    game = DynamicConnect3()
    game.play()
