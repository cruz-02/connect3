import utils
import random

class MiniMaxAgent:
    def __init__(self, player):
        self.player = player # 0/white/max or 1/black/min
        self.board = [
            [0, None, None, None, 1],
            [1, None, None, None, 0],
            [0, None, None, None, 1],
            [1, None, None, None, 0],
        ]
        # TODO: may change it so that it tracks a list of pieces... these are wrong tho (should do -1)
        # if player == 0:
        #     self.my_pieces = [(1,1),(1,3),(5,2),(5,4)] # X Y
        #     self.op_pieces =  [(1,2),(1,4),(5,1),(5,3)] # X Y
        # else:
        #     self.op_pieces = [(1,1),(1,3),(5,2),(5,4)] # X Y
        #     self.my_pieces =  [(1,2),(1,4),(5,1),(5,3)] # X Y
        self.dirs = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

    def heuristic(self, state, status):
        """
        calculates naive heuristic (runs of two) 
        """
        if status == self.player:
            return float('inf')
        elif status == (1 - self.player):
            return float('-inf')
        curr_player = self.player
        opp_player = 1 - self.player
        my_score = 0
        opp_score = 0

        # Check horizontal
        for y in range(4):
            for x in range(4):
                if state[y][x] == curr_player and state[y][x+1] == curr_player:
                    my_score += 1
                elif state[y][x] == opp_player and state[y][x+1] == opp_player:
                    opp_score += 1 

        # Check vertical
        for y in range(3):
            for x in range(5):
                if state[y][x] == curr_player and state[y+1][x] == curr_player:
                    my_score += 1
                elif state[y][x] == opp_player and state[y+1][x] == opp_player:
                    opp_score += 1

        # Check diagonal (down-right)
        for y in range(3):
            for x in range(4):
                if state[y][x] == curr_player and state[y+1][x+1] == curr_player:
                    my_score += 1
                elif state[y][x] == opp_player and state[y+1][x+1] == opp_player:
                    opp_score += 1

        # Check diagonal (down-left)
        for y in range(3):
            for x in range(1, 5):
                if state[y][x] == curr_player and state[y+1][x-1] == curr_player:
                    my_score += 1
                elif state[y][x] == opp_player and state[y+1][x-1] == opp_player:
                    opp_score += 1
        
        return my_score - opp_score



    def gen_actions(self, state, is_max):
        """
        generates all possible actions given a state

        input
        state: board matrix
        coords: (x,y) tuple
        
        output:
        list of tulples ((og xy), (new xy))
        """

        moves = []
        player = 0 if is_max else 1
        for y in range(4):
            for x in range(5):
                if state[y][x] == player:
                    for dx, dy in self.dirs.values():
                        new_x, new_y = x + dx, y + dy
                        if utils.in_board(new_x, new_y) and state[new_y][new_x] is None:
                            moves.append(((x, y), (new_x, new_y)))
        return moves


    def minimax(self, state, depth, is_max):

        status = utils.game_status(state)
        #terminal state or depth cutoff
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)

        if is_max:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                eval, _ = self.minimax(utils.make_move(state, move, True), depth-1, False)        
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in moves:
                eval, _= self.minimax(utils.make_move(state, move, False), depth-1, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def find_best_move(self, depth):
        """
        logic to find best action
        """
        is_max = True if self.player == 0 else False

        score, best_move = self.minimax(self.board, depth, is_max,)

        print(f"Agent {self.player} found best move: {best_move} with score: {score}")

        if best_move is None:
            print("Agent sees terminal state or no moves")
            return None

        # Update Board
        self.board = utils.make_move(self.board, best_move, is_max)

        return utils.format_move_to_string(best_move)
    
    def update_board_opp(self, input):
        """
        update board with received values
        input shaped as 14E
        """
        is_max = True if self.player == 0 else False
        opponent_is = not is_max

        x = int(input[0])-1
        y = int(input[1])-1
        dir = input[2].upper()

        new_x, new_y = x, y
        if dir == 'N':
            new_y -= 1
        elif dir == 'S':
            new_y += 1
        elif dir == 'E':
            new_x += 1
        elif dir == 'W':
            new_x -= 1

        move = ((x, y), (new_x, new_y))


        self.board = utils.make_move(self.board, move, opponent_is)
        print(f"opponent moved: {input}")

class MiniMaxAgentD(MiniMaxAgent):
    def __init__(self, player):
        super().__init__(player)
        self.board_history = {}
        self.zobrist_table = [[[random.getrandbits(64) for _ in range(5)] for _ in range(4)] for _ in range(2)]

    def minimax(self, state, depth, is_max, curr_hash, history):

        status = utils.game_status(state)
        #terminal state or depth cutoff
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)

        if is_max:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                new_hash = utils.calculate_new_hash(state, move, curr_hash, self.zobrist_table)
                new_history = history.copy()
                new_history[new_hash] = new_history.get(new_hash, 0) + 1

                if new_history[new_hash] >= 3:
                    eval = 0
                else:
                    eval, _ = self.minimax(utils.make_move(state, move, True), depth-1, False, new_hash, new_history)
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in moves:

                new_hash = utils.calculate_new_hash(state, move, curr_hash, self.zobrist_table)
                new_history = history.copy()
                new_history[new_hash] = new_history.get(new_hash, 0) + 1

                if new_history[new_hash] >= 3:
                    eval = 0
                else:
                    eval, _= self.minimax(utils.make_move(state, move, False), depth-1, True, new_hash, new_history)
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def find_best_move(self, depth):
        """
        logic to find best action
        """
        is_max = True if self.player == 0 else False

        init_history = self.board_history.copy()
        init_hash = utils.calculate_initial_hash(self.board, self.zobrist_table)
        init_history[init_hash] = init_history.get(init_hash, 0) + 1


        score, best_move = self.minimax(self.board, depth, is_max, init_hash, init_history)

        print(f"Agent {self.player} found best move: {best_move} with score: {score}")

        if best_move is None:
            print("Agent sees terminal state or no moves")
            return None

        # Update Board
        self.board = utils.make_move(self.board, best_move, is_max)
        # update game history with new board
        update_hash = utils.calculate_initial_hash(self.board, self.zobrist_table)
        self.board_history[update_hash] = self.board_history.get(update_hash, 0) + 1

        return utils.format_move_to_string(best_move)

class AlphaBeta(MiniMaxAgent):
    def __init__(self, player):
        super().__init__(player)

    def minimax(self, state, depth, is_max, alpha, beta):

        status = utils.game_status(state)
        #terminal state or depth cutoff
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)

        if is_max:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                eval, _ = self.minimax(utils.make_move(state, move, True), depth-1, False, alpha, beta)        
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in moves:
                eval, _= self.minimax(utils.make_move(state, move, False), depth-1, True, alpha, beta)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                
                beta = min(beta, min_eval)
                if beta<= alpha:
                    break
            return min_eval, best_move

    def find_best_move(self, depth):
        """
        logic to find best action
        """
        is_max = True if self.player == 0 else False

        score, best_move = self.minimax(self.board, depth, is_max, float('-inf'), float('inf'))

        print(f"Agent {self.player} found best move: {best_move} with score: {score}")

        if best_move is None:
            print("Agent sees terminal state or no moves")
            return None

        # Update Board
        self.board = utils.make_move(self.board, best_move, is_max)

        return utils.format_move_to_string(best_move)

class AlphaBetaD(MiniMaxAgentD):
    def __init__(self, player):
        super().__init__(player)

    def minimax(self, state, depth, is_max, curr_hash, history, alpha, beta):

        status = utils.game_status(state)
        #terminal state or depth cutoff
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)

        if is_max:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                new_hash = utils.calculate_new_hash(state, move, curr_hash, self.zobrist_table)
                new_history = history.copy()
                new_history[new_hash] = new_history.get(new_hash, 0) + 1

                if new_history[new_hash] >= 3:
                    eval = 0
                else:
                    eval, _ = self.minimax(utils.make_move(state, move, True), depth-1, False, new_hash, new_history)
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in moves:

                new_hash = utils.calculate_new_hash(state, move, curr_hash, self.zobrist_table)
                new_history = history.copy()
                new_history[new_hash] = new_history.get(new_hash, 0) + 1

                if new_history[new_hash] >= 3:
                    eval = 0
                else:
                    eval, _= self.minimax(utils.make_move(state, move, False), depth-1, True, new_hash, new_history)
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, min_eval)
            return min_eval, best_move

    def find_best_move(self, depth):
        """
        logic to find best action
        """
        is_max = True if self.player == 0 else False

        init_history = self.board_history.copy()
        init_hash = utils.calculate_initial_hash(self.board, self.zobrist_table)
        init_history[init_hash] = init_history.get(init_hash, 0) + 1


        score, best_move = self.minimax(self.board, depth, is_max, init_hash, init_history, float('-inf'), float('inf'))

        print(f"Agent {self.player} found best move: {best_move} with score: {score}")

        if best_move is None:
            print("Agent sees terminal state or no moves")
            return None

        # Update Board
        self.board = utils.make_move(self.board, best_move, is_max)
        # update game history with new board
        update_hash = utils.calculate_initial_hash(self.board, self.zobrist_table)
        self.board_history[update_hash] = self.board_history.get(update_hash, 0) + 1

        return utils.format_move_to_string(best_move)

class MiniMaxAgentV2(MiniMaxAgent):
    """
    Changed Heuristic, so that it is not naive.
    Inspired from Victor Aliss Connect 4 work. (winning / threat pattern recognition, positional value, Zugzwang )
    And some of my own intuition.
    """
    def __init__(self, player):
        super().__init__(player)

    def heuristic(self, state, status):
        """
        calculates heuristic v2
        winning setups = 9999
        forcing setups * 10
        winning patterns * 4
        runs of two * 1
        pos/grouping score * 1
        """
        if status == self.player:
            return float('inf')
        elif status == (1 - self.player):
            return float('-inf')
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils.count_forcing_threats(state, opp_player)

        if my_threats >=2:
            return 9999
        if opp_threats >=2:
            return -9999

        threat_score = 10 * (my_threats - opp_threats)
        pattern_score = 2 * (my_patterns - opp_patterns)

        my_runsoftwo = utils.count_runsoftwo(state, curr_player)
        opp_runsoftwo = utils.count_runsoftwo(state, opp_player)

        runsoftwo_score = my_runsoftwo - opp_runsoftwo

        my_pos = utils.pos_score(state, curr_player)
        opp_pos = utils.pos_score(state, opp_player)

        pos_score = my_pos - opp_pos

        
        return threat_score + pattern_score + runsoftwo_score + pos_score
    
class AlphaBetaV2(AlphaBeta):
    def __init__(self, player):
        super().__init__(player)

    def heuristic(self, state, status):
        """
        calculates heuristic v2
        winning setups = 9999
        forcing setups * 10
        winning patterns * 4
        runs of two * 1
        pos/grouping score * 1
        """
        if status == self.player:
            return float('inf')
        elif status == (1 - self.player):
            return float('-inf')
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils.count_forcing_threats(state, opp_player)

        #  kind of implemented it
        if my_threats >=2:
            return 9999
        if opp_threats >=2:
            return -9999

        threat_score = 10 * (my_threats - opp_threats)
        pattern_score = 2 * (my_patterns - opp_patterns)

        my_runsoftwo = utils.count_runsoftwo(state, curr_player)
        opp_runsoftwo = utils.count_runsoftwo(state, opp_player)

        runsoftwo_score = my_runsoftwo - opp_runsoftwo

        my_pos = utils.pos_score(state, curr_player)
        opp_pos = utils.pos_score(state, opp_player)

        pos_score = my_pos - opp_pos

        
        return threat_score + pattern_score + runsoftwo_score + pos_score
    

class MiniMaxAgentV3(MiniMaxAgentV2):
    """
    States were going crazy when applying the new heuristic on abp. in theory it was supposed to reduce them or at least keep tthem to the same level
    So im ordering the moves now.
    Afet test, it did not work as intented
    """
    def __init__(self, player):
        super().__init__(player)


    def minimax(self, state, depth, is_max):

        status = utils.game_status(state)
        #terminal state or depth cutoff
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)

        moves = utils.order_moves(state, moves, is_max, self.player)

        best_move = moves[0] if moves else None

        if is_max:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                eval, _ = self.minimax(utils.make_move(state, move, True), depth-1, False)        
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in moves:
                eval, _= self.minimax(utils.make_move(state, move, False), depth-1, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def heuristic(self, state, status):
        """
        calculates heuristic v2
        winning setups = 9999
        forcing setups * 10
        winning patterns * 4
        runs of two * 1
        pos/grouping score * 1
        """
        if status == self.player:
            return float('inf')
        elif status == (1 - self.player):
            return float('-inf')
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils.count_forcing_threats(state, opp_player)

        if my_threats >=2:
            return 9999
        if opp_threats >=2:
            return -9999

        threat_score = 10 * (my_threats - opp_threats)
        pattern_score = 2 * (my_patterns - opp_patterns)

        my_pos = utils.pos_score(state, curr_player)
        opp_pos = utils.pos_score(state, opp_player)

        pos_score = my_pos - opp_pos

        
        return threat_score + pattern_score + pos_score

class AlphaBetaV3(AlphaBetaV2):

    def __init__(self, player):
        super().__init__(player)

    def heuristic(self, state, status):
        """
        calculates heuristic v2
        winning setups = 9999
        forcing setups * 10
        winning patterns * 4
        runs of two * 1
        pos/grouping score * 1
        """
        if status == self.player:
            return float('inf')
        elif status == (1 - self.player):
            return float('-inf')
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils.count_forcing_threats(state, opp_player)

        #  kind of implemented it
        if my_threats >=2:
            return 9999
        if opp_threats >=2:
            return -9999

        threat_score = 10 * (my_threats - opp_threats)
        pattern_score = 2 * (my_patterns - opp_patterns)

        my_pos = utils.pos_score(state, curr_player)
        opp_pos = utils.pos_score(state, opp_player)

        pos_score = my_pos - opp_pos

        
        return threat_score + pattern_score + pos_score
    
    def minimax(self, state, depth, is_max, alpha, beta):

        status = utils.game_status(state)
        #terminal state or depth cutoff
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)

        moves = utils.order_moves(state, moves, is_max, self.player)

        best_move = moves[0] if moves else None

        if is_max:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                eval, _ = self.minimax(utils.make_move(state, move, True), depth-1, False, alpha, beta)        
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in moves:
                eval, _= self.minimax(utils.make_move(state, move, False), depth-1, True, alpha, beta)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                
                beta = min(beta, min_eval)
                if beta<= alpha:
                    break
            return min_eval, best_move
        

# ----------------------------------------------------------------------
# --- NEW: Large 7x6 Grid Agent Classes --- Gemini Generated
# ----------------------------------------------------------------------

class MiniMaxAgentV2L(MiniMaxAgentV2):
    """
    An agent using the V2 heuristic on the large 7x6 grid.
    """
    def __init__(self, player, zobrist_table):
        super().__init__(player)
        self.zobrist_table = zobrist_table
        # New 7x6 board with centered starting configuration
        self.board = [[None for _ in range(6)] for _ in range(7)]
        # White (0)
        self.board[2][1], self.board[2][4] = 0, 0
        self.board[4][1], self.board[4][4] = 0, 0
        # Black (1)
        self.board[2][2], self.board[2][3] = 1, 1
        self.board[4][2], self.board[4][3] = 1, 1

        # Agent's history of the REAL game
        initial_hash = utils.calculate_initial_hashL(self.board, self.zobrist_table)
        self.board_history = {initial_hash: 1}

    def gen_actions(self, state, is_max):
        """Generates actions for the 7x6 grid."""
        moves = []
        player = 0 if is_max else 1
        for y in range(7):
            for x in range(6):
                if state[y][x] == player:
                    for dx, dy in self.dirs.values():
                        new_x, new_y = x + dx, y + dy
                        if utils.in_boardL(new_x, new_y) and state[new_y][new_x] is None:
                            moves.append(((x, y), (new_x, new_y)))
        return moves
    
    def heuristic(self, state, status):
        """Calculates the V2 heuristic using large-grid utility functions."""
        if status == self.player:
            return float('inf')
        elif status == (1 - self.player):
            return float('-inf')
        if status == "DRAW": # Assumes you might add draw detection to game_statusL
             return 0

        my_patterns, my_threats = utils.count_forcing_threatsL(state, self.player)
        opp_patterns, opp_threats = utils.count_forcing_threatsL(state, 1 - self.player)

        threat_score = 10 * (my_threats - opp_threats)
        pattern_score = 3 * (my_patterns - opp_patterns)
        pos_score_val = utils.pos_scoreL(state, self.player) - utils.pos_scoreL(state, 1 - self.player)
        
        return threat_score + pattern_score + pos_score_val

    def minimax(self, state, depth, is_max):
        """Minimax search using large-grid utility functions."""
        status = utils.game_statusL(state)
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)
        best_move = moves[0] if moves else None

        if is_max:
            max_eval = float('-inf')
            for move in moves:
                eval, _ = self.minimax(utils.make_moveL(state, move, True), depth - 1, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                eval, _ = self.minimax(utils.make_moveL(state, move, False), depth - 1, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def find_best_move(self, depth):
        """Finds the best move on the 7x6 grid."""
        is_max = (self.player == 0)
        score, best_move = self.minimax(self.board, depth, is_max)
        print(f"Agent {self.player} found best move: {best_move} with score: {score}")

        if best_move is None:
            print("Agent sees a terminal state or has no moves.")
            return None

        self.board = utils.make_moveL(self.board, best_move, is_max)
        new_hash = utils.calculate_initial_hashL(self.board, self.zobrist_table)
        self.board_history[new_hash] = self.board_history.get(new_hash, 0) + 1

        return utils.format_move_to_stringL(best_move)

    def update_board_opp(self, move_str):
        """Updates the agent's internal 7x6 board with the opponent's move."""
        opponent_is_max = not (self.player == 0)
        
        start_x, start_y = int(move_str[0]) - 1, int(move_str[1]) - 1
        direction = move_str[2].upper()
        dx, dy = self.dirs[direction]
        end_x, end_y = start_x + dx, start_y + dy
        move_tuple = ((start_x, start_y), (end_x, end_y))

        self.board = utils.make_moveL(self.board, move_tuple, opponent_is_max)
        new_hash = utils.calculate_initial_hashL(self.board, self.zobrist_table)
        self.board_history[new_hash] = self.board_history.get(new_hash, 0) + 1
        print(f"Agent {self.player} acknowledged opponent move: {move_str}")


class AlphaBetaV2L(MiniMaxAgentV2L): # Inherits all the L-grid methods
    """
    An agent using the V2 heuristic with Alpha-Beta Pruning on the large 7x6 grid.
    """
    def minimax(self, state, depth, is_max, alpha, beta):
        """Alpha-Beta search using large-grid utility functions."""
        status = utils.game_statusL(state)
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)
        best_move = moves[0] if moves else None

        if is_max:
            max_eval = float('-inf')
            for move in moves:
                eval, _ = self.minimax(utils.make_moveL(state, move, True), depth - 1, False, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                eval, _ = self.minimax(utils.make_moveL(state, move, False), depth - 1, True, alpha, beta)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def find_best_move(self, depth):
        """Finds the best move on the 7x6 grid using Alpha-Beta Pruning."""
        is_max = (self.player == 0)
        score, best_move = self.minimax(self.board, depth, is_max, float('-inf'), float('inf'))
        print(f"Agent {self.player} found best move: {best_move} with score: {score}")

        if best_move is None:
            print("Agent sees a terminal state or has no moves.")
            return None

        self.board = utils.make_moveL(self.board, best_move, is_max)
        new_hash = utils.calculate_initial_hashL(self.board, self.zobrist_table)
        self.board_history[new_hash] = self.board_history.get(new_hash, 0) + 1

        return utils.format_move_to_stringL(best_move)