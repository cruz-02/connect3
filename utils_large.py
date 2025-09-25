# utils_large.py
import copy

# --- BOARD-SIZE DEPENDENT FUNCTIONS (MODIFIED) ---

def in_board(x, y):
    """Checks if coordinates are within the 7x6 board."""
    return 0 <= y < 6 and 0 <= x < 7

def check_win(state, curr_player):
    """Checks for a Connect-3 win on the 7x6 board."""
    # Check horizontal
    for y in range(6):
        for x in range(5): # 7 - 2
            if state[y][x] == curr_player and state[y][x+1] == curr_player and state[y][x+2] == curr_player:
                return True
    # Check vertical
    for y in range(4): # 6 - 2
        for x in range(7):
            if state[y][x] == curr_player and state[y+1][x] == curr_player and state[y+2][x] == curr_player:
                return True
    # Check diagonal (down-right)
    for y in range(4):
        for x in range(5):
            if state[y][x] == curr_player and state[y+1][x+1] == curr_player and state[y+2][x+2] == curr_player:
                return True
    # Check diagonal (down-left)
    for y in range(4):
        for x in range(2, 7):
            if state[y][x] == curr_player and state[y+1][x-1] == curr_player and state[y+2][x-2] == curr_player:
                return True
    return False

def calculate_initial_hash(board, zobrist_table):
    h = 0
    for y in range(6):
        for x in range(7):
            piece = board[y][x]
            if piece is not None:
                h ^= zobrist_table[piece][y][x]
    return h

def count_forcing_threats(state, player):
    """Counts winning patterns and forcing threats on the 7x6 board."""
    winning_patterns = 0
    forcing_threats = 0
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def is_forcing_threat(winning_coords, p1_coords, p2_coords):
        wy, wx = winning_coords
        for dx, dy in dirs:
            ny, nx = wy + dy, wx + dx
            if (0 <= ny < 6 and 0 <= nx < 7) and state[ny][nx] == player:
                if (ny, nx) != p1_coords and (ny, nx) != p2_coords:
                    return True
        return False
    # Horizontal
    for y in range(6):
        for x in range(5):
            line = [state[y][x], state[y][x+1], state[y][x+2]]
            if line.count(player) == 2 and line.count(None) == 1:
                empty_idx = line.index(None)
                p1_idx = line.index(player); p2_idx = line.index(player, p1_idx + 1)
                if is_forcing_threat((y, x + empty_idx), (y, x + p1_idx), (y, x + p2_idx)): forcing_threats += 1
                else: winning_patterns += 1
    # Vertical
    for y in range(4):
        for x in range(7):
            line = [state[y][x], state[y+1][x], state[y+2][x]]
            if line.count(player) == 2 and line.count(None) == 1:
                empty_idx = line.index(None)
                p1_idx = line.index(player); p2_idx = line.index(player, p1_idx + 1)
                if is_forcing_threat((y + empty_idx, x), (y + p1_idx, x), (y + p2_idx, x)): forcing_threats += 1
                else: winning_patterns += 1
    # Diagonal (down-right)
    for y in range(4):
        for x in range(5):
            line = [state[y][x], state[y+1][x+1], state[y+2][x+2]]
            if line.count(player) == 2 and line.count(None) == 1:
                empty_idx = line.index(None)
                p1_idx = line.index(player); p2_idx = line.index(player, p1_idx + 1)
                if is_forcing_threat((y + empty_idx, x + empty_idx), (y + p1_idx, x + p1_idx), (y + p2_idx, x + p2_idx)): forcing_threats += 1
                else: winning_patterns += 1
    # Diagonal (down-left)
    for y in range(4):
        for x in range(2, 7):
            line = [state[y][x], state[y+1][x-1], state[y+2][x-2]]
            if line.count(player) == 2 and line.count(None) == 1:
                empty_idx = line.index(None)
                p1_idx = line.index(player); p2_idx = line.index(player, p1_idx + 1)
                if is_forcing_threat((y + empty_idx, x - empty_idx), (y + p1_idx, x - p1_idx), (y + p2_idx, x - p2_idx)): forcing_threats += 1
                else: winning_patterns += 1
    return winning_patterns, forcing_threats

def count_runsoftwo(state, player):
    """Counts runs of two on the 7x6 board."""
    score = 0
    # Horizontal
    for y in range(6):
        for x in range(6):
            if state[y][x] == player and state[y][x+1] == player: score += 1
    # Vertical
    for y in range(5):
        for x in range(7):
            if state[y][x] == player and state[y+1][x] == player: score += 1
    # Diagonal (down-right)
    for y in range(5):
        for x in range(6):
            if state[y][x] == player and state[y+1][x+1] == player: score += 1
    # Diagonal (down-left)
    for y in range(5):
        for x in range(1, 7):
            if state[y][x] == player and state[y+1][x-1] == player: score += 1
    return score

def pos_score(state, player):
    """Positional value map for the 7x6 grid."""
    value_map = [
        [1, 2, 3, 4, 3, 2, 1],
        [2, 4, 6, 8, 6, 4, 2],
        [3, 6, 9, 12, 9, 6, 3],
        [3, 6, 9, 12, 9, 6, 3],
        [2, 4, 6, 8, 6, 4, 2],
        [1, 2, 3, 4, 3, 2, 1],
    ]
    score = 0
    for y in range(6):
        for x in range(7):
            if state[y][x] == player:
                score += value_map[y][x]
    return score

# --- BOARD-SIZE INDEPENDENT FUNCTIONS (COPIED) ---

def make_move(state, move, is_max):
    x, y = move[0]
    new_x, new_y = move[1]
    new_state = copy.deepcopy(state)
    new_state[new_y][new_x] = 0 if is_max else 1
    new_state[y][x] = None
    return new_state

def format_move_to_string(move_tuple):
    dirs = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
    if not move_tuple: return None
    start_pos, end_pos = move_tuple
    start_x, start_y = start_pos
    dx, dy = end_pos[0] - start_x, end_pos[1] - start_y
    direction = [k for k, v in dirs.items() if v == (dx, dy)][0]
    return f"{start_x + 1}{start_y + 1}{direction}"

def game_status(state):
    if check_win(state, 0): return 0
    if check_win(state, 1): return 1
    return None

def calculate_new_hash(state, move, curr_hash, zobrist_table):
    x, y = move[0]
    new_x, new_y = move[1]
    player_token = state[y][x]
    new_hash = curr_hash
    new_hash ^= zobrist_table[player_token][y][x]
    new_hash ^= zobrist_table[player_token][new_y][new_x]
    return new_hash