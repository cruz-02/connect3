# large.py
import random
import utils_large  # Use the new utility file for the large grid

class AlphaBetaV2DLarge:
    def __init__(self, player):
        self.player = player # 0/white/max or 1/black/min
        self.board = [
            [None, None, None, None, None, None, None],
            [None, 0,    None, None, None, 1,    None],
            [None, 1,    None, None, None, 0,    None],
            [None, 0,    None, None, None, 1,    None],
            [None, 1,    None, None, None, 0,    None],
            [None, None, None, None, None, None, None]
        ]
        self.dirs = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
        self.board_history = {}
        # Zobrist table adapted for a 6-row, 7-column grid for 2 players
        self.zobrist_table = [[[random.getrandbits(64) for _ in range(7)] for _ in range(6)] for _ in range(2)]

    def heuristic(self, state, status):
        """
        Calculates the V2 heuristic for the 7x6 board.
        This function now calls the adapted utility functions from utils_large.
        """
        if status == self.player:
            return float('inf')
        elif status == (1 - self.player):
            return float('-inf')
        
        def_factor = 1.5
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils_large.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils_large.count_forcing_threats(state, opp_player)

        my_double = 100 if my_threats > 1 else 0
        opp_double = 100 if opp_threats > 1 else 0

        double_score = my_double - opp_double * def_factor
        threat_score = 10 * (my_threats - opp_threats * def_factor)
        pattern_score = 4 * (my_patterns - opp_patterns * def_factor)

        my_runsoftwo = utils_large.count_runsoftwo(state, curr_player)
        opp_runsoftwo = utils_large.count_runsoftwo(state, opp_player)
        runsoftwo_score = 1 * (my_runsoftwo - opp_runsoftwo * def_factor)

        my_pos = utils_large.pos_score(state, curr_player)
        opp_pos = utils_large.pos_score(state, opp_player)
        pos_score = 2 * (my_pos - opp_pos * def_factor)
        
        return double_score + threat_score + pattern_score + runsoftwo_score + pos_score
    
    def gen_actions(self, state, is_max):
        """
        Generates all possible actions for the 7x6 board.
        """
        moves = []
        player = 0 if is_max else 1
        # Loop over 6 rows and 7 columns
        for y in range(6):
            for x in range(7):
                if state[y][x] == player:
                    for dx, dy in self.dirs.values():
                        new_x, new_y = x + dx, y + dy
                        if utils_large.in_board(new_x, new_y) and state[new_y][new_x] is None:
                            moves.append(((x, y), (new_x, new_y)))
        return moves

    def minimax(self, state, depth, is_max, curr_hash, history, alpha, beta):
        status = utils_large.game_status(state)
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)

        if is_max:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                new_hash = utils_large.calculate_new_hash(state, move, curr_hash, self.zobrist_table)
                new_history = history.copy()
                new_history[new_hash] = new_history.get(new_hash, 0) + 1

                eval = 0 if new_history[new_hash] >= 3 else self.minimax(utils_large.make_move(state, move, True), depth-1, False, new_hash, new_history, alpha, beta)[0]
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else: # Min player
            min_eval = float('inf')
            best_move = None
            for move in moves:
                new_hash = utils_large.calculate_new_hash(state, move, curr_hash, self.zobrist_table)
                new_history = history.copy()
                new_history[new_hash] = new_history.get(new_hash, 0) + 1

                eval = 0 if new_history[new_hash] >= 3 else self.minimax(utils_large.make_move(state, move, False), depth-1, True, new_hash, new_history, alpha, beta)[0]
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def find_best_move(self, depth):
        is_max = True if self.player == 0 else False
        init_history = self.board_history.copy()
        init_hash = utils_large.calculate_initial_hash(self.board, self.zobrist_table)
        init_history[init_hash] = init_history.get(init_hash, 0) + 1

        score, best_move = self.minimax(self.board, depth, is_max, init_hash, init_history, float('-inf'), float('inf'))
        print(f"Agent {self.player} found best move: {best_move} with score: {score}")

        if best_move is None:
            print("Agent sees terminal state or no moves")
            return None

        self.board = utils_large.make_move(self.board, best_move, is_max)
        update_hash = utils_large.calculate_initial_hash(self.board, self.zobrist_table)
        self.board_history[update_hash] = self.board_history.get(update_hash, 0) + 1
        return utils_large.format_move_to_string(best_move)
    
    def update_board_opp(self, input_str):
        is_max = True if self.player == 0 else False
        opponent_is_max = not is_max

        x = int(input_str[0]) - 1
        y = int(input_str[1]) - 1
        direction = input_str[2].upper()
        
        dx, dy = self.dirs[direction]
        new_x, new_y = x + dx, y + dy
        move = ((x, y), (new_x, new_y))

        self.board = utils_large.make_move(self.board, move, opponent_is_max)
        print(f"Opponent moved: {input_str}")