import copy



def in_board(x, y):
    return 0 <= y < 4 and 0 <= x < 5

def get_board_state_tuple(state):
    """
    Converts board to tuple so we can keep track of it in a dict
    """
    return tuple(tuple(row) for row in state)

def make_move(state, move, is_max):
    """
    simulates new board given a state and action
    """
    x, y =  move[0]
    new_x, new_y = move[1]
    
    new_state = copy.deepcopy(state)
    new_state[new_y][new_x] = 0 if is_max else 1
    new_state[y][x] = None
    
    return new_state

def format_move_to_string(move_tuple):
    # Made by gemini
    # This dictionary maps direction characters to their (dx, dy) coordinate changes
    dirs = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

    if not move_tuple: 
        return None
        
    start_pos, end_pos = move_tuple
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    
    # Calculate the change in x and y
    dx, dy = end_x - start_x, end_y - start_y
    
    # Find the key (direction) where the value matches the (dx, dy) tuple
    direction = [k for k, v in dirs.items() if v == (dx, dy)][0]
    
    # Return the 1-indexed coordinate string
    return f"{start_x + 1}{start_y + 1}{direction}"



# CHECK WIN, DRAW, GAME STATUS ---------------------------------------------------------------------------------------
def check_win(state, curr_player):
        """
        Checks if the current curr_player has won by getting three pieces in a row.
        """
        # Check horizontal
        for y in range(4):
            for x in range(3):
                if state[y][x] == curr_player and state[y][x+1] == curr_player and state[y][x+2] == curr_player:
                    return True

        # Check vertical
        for y in range(2):
            for x in range(5):
                if state[y][x] == curr_player and state[y+1][x] == curr_player and state[y+2][x] == curr_player:
                    return True

        # Check diagonal (down-right)
        for y in range(2):
            for x in range(3):
                if state[y][x] == curr_player and state[y+1][x+1] == curr_player and state[y+2][x+2] == curr_player:
                    return True

        # Check diagonal (down-left)
        for y in range(2):
            for x in range(2, 5):
                if state[y][x] == curr_player and state[y+1][x-1] == curr_player and state[y+2][x-2] == curr_player:
                    return True
        
        return False



def game_status(state):
    if check_win(state, 0):
        return 0
    elif check_win(state, 1):
        return 1
    
    return None

#---------------------------------------------------------------------------------------------------------------------------------------------------------


#  ZOBRIST HASH
def calculate_initial_hash(board, zobrist_table):
    h = 0
    for y in range(4):
        for x in range(5):
            piece = board[y][x]
            if piece is not None: # piece will be 0 or 1
                h ^= zobrist_table[piece][y][x]
    return h

def calculate_new_hash(state, move, curr_hash, zobrist_table):
    x,y = move[0]
    new_x, new_y = move[1]
    player_token = state[y][x]
    new_hash = curr_hash
    #update hash with move
    new_hash ^= zobrist_table[player_token][y][x]
    new_hash ^= zobrist_table[player_token][new_y][new_x]

    return new_hash