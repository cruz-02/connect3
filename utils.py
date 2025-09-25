import copy
import socket



# Add these functions to your utils.py file GEMINI GENERATED

def send_move(sock, move_str):
    """Encodes and sends a move string to the server with a newline."""
    if not move_str:
        print("No move to send.")
        return
    try:
        # Append newline as a message delimiter and encode to bytes
        message_bytes = (move_str + '\n').encode('utf-8')
        sock.sendall(message_bytes)
        print(f"Sent: {move_str}")
    except Exception as e:
        print(f"Error sending move: {e}")

def receive_move(sock, buffer_size=1024):
    """Receives data from the server, decodes it, and removes the newline."""
    try:
        data_bytes = sock.recv(buffer_size)
        if not data_bytes:
            return None # Connection closed by server
        
        # Decode from bytes and strip leading/trailing whitespace (like the newline)
        message = data_bytes.decode('utf-8').strip()
        print(f"Received: {message}")
        return message
    except Exception as e:
        print(f"Error receiving move: {e}")
        return None


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


#---------------------------------------------------------------------------------------------------------------------------------------------------------
# Heuristic V2 utils


def count_double_threats(state, player):
    """
    Counts unstoppable threats
    """

    #  TODO: more than 2 force threats in a square?
    pass



def count_forcing_threats(state, player, debug = False):
    """
    modified it so that it uses the same for loop to make the heuristic more efficient. (used to be winning_patterns and forcing_threats different)
    Counts winning patterns and forcing threats. Winning pattern example [1,None,1] [1,1,None]
    """

    if debug:
        print("Board State:")
        for row in state:
            print([c if c is not None else '_' for c in row])

    winning_patterns = 0
    forcing_threats = 0
    
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)] # S, N, E, W

    # Actual forcing threat
    def forcing_threat(winning_coords, piece1_coords, piece2_coords, debug = False):
        """
        Inspired on the concept of Zwugzwang
        """
        wy, wx = winning_coords
        for dx, dy in dirs:
            ny, nx = wy + dy, wx + dx
            if debug:
                print(f"wx:  {wx}, wy: {wy}")
                print(f"dx:  {dx}, dy: {dy}")
                print(f"nx:  {nx}, ny: {ny}")
                breakpoint()
            if (0 <= ny < 4 and 0 <= nx < 5) and state[ny][nx] == player:
                if (ny, nx) != piece1_coords and (ny, nx) != piece2_coords:
                    return True
        return False

    # Horizontal lines
    if debug:
        print("horizontal")
    for y in range(4):
        for x in range(3):
            line = [state[y][x], state[y][x+1], state[y][x+2]]

            # if debug:
            #     print(f"y: {y}  x: {x}")
            #     print(f"winning_patterns {winning_patterns}, forcing threats {forcing_threats} ")
            #     print(line)
            #     breakpoint()

            # if player two times in line and empty square
            if line.count(player) == 2 and line.count(None) == 1:
                empty_idx = line.index(None)
                p1_idx = line.index(player)
                p2_idx = line.index(player, p1_idx + 1) 
                
                winning_square = (y, x + empty_idx)
                piece1_coords = (y, x + p1_idx)
                piece2_coords = (y, x + p2_idx)
                
                #  if is not a forcing threat it is a winning pattern
                if forcing_threat(winning_square, piece1_coords, piece2_coords):
                    forcing_threats += 1
                else:
                    winning_patterns += 1

    # Vertical lines
    if debug:
        print("vertical")
    for y in range(2):
        for x in range(5):
            line = [state[y][x], state[y+1][x], state[y+2][x]]
            if debug:
                print(f"y: {y}  x: {x}")
                print(f"winning_patterns {winning_patterns}, forcing threats {forcing_threats} ")
                print(line)
                breakpoint()

            if line.count(player) == 2 and line.count(None) == 1:
                empty_idx = line.index(None)
                p1_idx = line.index(player)
                p2_idx = line.index(player, p1_idx + 1)
                
                winning_square = (y + empty_idx, x)
                piece1_coords = (y + p1_idx, x)
                piece2_coords = (y + p2_idx, x)

                if forcing_threat(winning_square, piece1_coords, piece2_coords, debug):
                    forcing_threats += 1
                else:
                    winning_patterns += 1

    # Diagonal (down-right)
    if debug:
        print("down-right")
    for y in range(2):
        for x in range(3):
            line = [state[y][x], state[y+1][x+1], state[y+2][x+2]]
            # if debug:
            #     print(f"y: {y}  x: {x}")
            #     print(f"winning_patterns {winning_patterns}, forcing threats {forcing_threats} ")
            #     print(line)
            #     breakpoint()

            if line.count(player) == 2 and line.count(None) == 1:
                empty_idx = line.index(None)
                p1_idx = line.index(player)
                p2_idx = line.index(player, p1_idx + 1)

                winning_square = (y + empty_idx, x + empty_idx)
                piece1_coords = (y + p1_idx, x + p1_idx)
                piece2_coords = (y + p2_idx, x + p2_idx)

                if forcing_threat(winning_square, piece1_coords, piece2_coords):
                    forcing_threats += 1
                else:
                    winning_patterns += 1

    # Diagonal (down-left)
    if debug:
        print("down-left")
    for y in range(2):
        for x in range(2, 5):
            line = [state[y][x], state[y+1][x-1], state[y+2][x-2]]
            # if debug:
            #     print(f"y: {y}  x: {x}")
            #     print(f"winning_patterns {winning_patterns}, forcing threats {forcing_threats} ")
            #     print(line)
            #     breakpoint()
            if line.count(player) == 2 and line.count(None) == 1:
                empty_idx = line.index(None)
                p1_idx = line.index(player)
                p2_idx = line.index(player, p1_idx + 1)
                
                winning_square = (y + empty_idx, x - empty_idx)
                piece1_coords = (y + p1_idx, x - p1_idx)
                piece2_coords = (y + p2_idx, x - p2_idx)

                if forcing_threat(winning_square, piece1_coords, piece2_coords):
                    forcing_threats += 1
                else:
                    winning_patterns += 1

    return winning_patterns, forcing_threats
    

def count_runsoftwo(state, player):
    """
    Naively counts runs of two (which are good not the best) example: [1,1,0] is a run of two even though it is blocked
    """

    score = 0
    # Check horizontal
    for y in range(4):
        for x in range(4):
            if state[y][x] == player and state[y][x+1] == player:
                score += 1

    # Check vertical
    for y in range(3):
        for x in range(5):
            if state[y][x] == player and state[y+1][x] == player:
                score += 1

    # Check diagonal (down-right)
    for y in range(3):
        for x in range(4):
            if state[y][x] == player and state[y+1][x+1] == player:
                score += 1

    # Check diagonal (down-left)
    for y in range(3):
        for x in range(1, 5):
            if state[y][x] == player and state[y+1][x-1] == player:
                score += 1

    return score


def pos_score(state, player):
    """
    Positional value, if on center, higher prob of creating patterns, thus higher prob of controlling flow of game.
    """
    value_map = [
        [1, 3, 7, 3, 1],
        [3, 5, 9, 5, 3], 
        [3, 5, 9, 5, 3],
        [1, 3, 7, 3, 1],
    ]
    
    score = 0
    for y in range(4):
        for x in range(5):
            if state[y][x] == player:
                score += value_map[y][x]
    return score


def order_moves(state, moves, is_max, player):
    move_scores = []
    for move in moves:
        temp_state = make_move(state, move, is_max)
        score = count_runsoftwo(temp_state, player) - count_runsoftwo(temp_state, 1 - player)
        move_scores.append(score)
    
    # Gemini helped me with this one: "How to order a tople based one of its elements. my tuple looks like this (score, (move))" 
    sorted_moves = [move for _, move in sorted(zip(move_scores, moves), key=lambda pair: pair[0], reverse=is_max)]
    return sorted_moves




def find_winning_square(state, player):

    # Horizontal
    for y in range(4):
        for x in range(3):
            line = [state[y][x], state[y][x+1], state[y][x+2]]
            if line.count(player) == 2 and line.count(None) == 1:
                empty_index = line.index(None)
                return (y, x + empty_index)
    # Vertical
    for y in range(2):
        for x in range(5):
            line = [state[y][x], state[y+1][x], state[y+2][x]]
            if line.count(player) == 2 and line.count(None) == 1:
                empty_index = line.index(None)
                return (y + empty_index, x)
    # Diagonal (down-right)
    for y in range(2):
        for x in range(3):
            line = [state[y][x], state[y+1][x+1], state[y+2][x+2]]
            if line.count(player) == 2 and line.count(None) == 1:
                empty_index = line.index(None)
                return (y + empty_index, x + empty_index)
    # Diagonal (down-left)
    for y in range(2):
        for x in range(2, 5):
            line = [state[y][x], state[y+1][x-1], state[y+2][x-2]]
            if line.count(player) == 2 and line.count(None) == 1:
                empty_index = line.index(None)
                return (y + empty_index, x - empty_index)
                
    return None 


def find_move_to_square(board, player, target_square):
    """
    Searches for a piece belonging to the player that can legally move
    to the target_square.
    Returns a move tuple ((start_x, start_y), (end_x, end_y)) or None.
    """
    if target_square is None:
        return None
        
    ty, tx = target_square
    # Directions dict needs to be available to this function
    dirs = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
    
    # Check all 4 adjacent squares to the target
    for dx, dy in dirs.values():
        start_y, start_x = ty - dy, tx - dx
        
        # Check if this adjacent square is on the board and contains the player's piece
        if in_board(start_x, start_y) and board[start_y][start_x] == player:
            # Found a valid blocking move
            return ((start_x, start_y), (tx, ty))
            
    return None # No piece found that can block the threat

