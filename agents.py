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
                    eval, _ = self.minimax(utils.make_move(state, move, True), depth-1, False, new_hash, new_history, alpha, beta)
                
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
                    eval, _= self.minimax(utils.make_move(state, move, False), depth-1, True, new_hash, new_history, alpha, beta)
                
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
        def_factor = 1.5
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils.count_forcing_threats(state, opp_player)

        
        if opp_threats >=2:
            return -9999
        if my_threats >=2:
            return 9999
        
        threat_score = 10 * (my_threats - opp_threats * def_factor)
        pattern_score = 2 * (my_patterns - opp_patterns * def_factor)

        my_runsoftwo = utils.count_runsoftwo(state, curr_player)
        opp_runsoftwo = utils.count_runsoftwo(state, opp_player)

        runsoftwo_score = my_runsoftwo - opp_runsoftwo * def_factor

        my_pos = utils.pos_score(state, curr_player)
        opp_pos = utils.pos_score(state, opp_player)

        pos_score = my_pos - opp_pos * def_factor

        
        return threat_score + pattern_score + runsoftwo_score + pos_score
    
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
        def_factor = 1.5
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils.count_forcing_threats(state, opp_player)

        
        if opp_threats >=2:
            return -9999
        if my_threats >=2:
            return 9999
        
        threat_score = 10 * (my_threats - opp_threats * def_factor)
        pattern_score = 2 * (my_patterns - opp_patterns * def_factor)

        my_runsoftwo = utils.count_runsoftwo(state, curr_player)
        opp_runsoftwo = utils.count_runsoftwo(state, opp_player)

        runsoftwo_score = my_runsoftwo - opp_runsoftwo * def_factor

        my_pos = utils.pos_score(state, curr_player)
        opp_pos = utils.pos_score(state, opp_player)

        pos_score = my_pos - opp_pos * def_factor

        
        return threat_score + pattern_score + runsoftwo_score + pos_score
    
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
    

class MiniMaxv2D(MiniMaxAgentD):
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
        def_factor = 1.5
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils.count_forcing_threats(state, opp_player)

        
        if opp_threats >=1:
            return -9999
        if my_threats >=2:
            return 9999
        
        threat_score = 10 * (my_threats - opp_threats * def_factor)
        pattern_score = 2 * (my_patterns - opp_patterns * def_factor)

        my_runsoftwo = utils.count_runsoftwo(state, curr_player)
        opp_runsoftwo = utils.count_runsoftwo(state, opp_player)

        runsoftwo_score = my_runsoftwo - opp_runsoftwo * def_factor

        my_pos = utils.pos_score(state, curr_player)
        opp_pos = utils.pos_score(state, opp_player)

        pos_score = 10 *  (my_pos - opp_pos * def_factor)

        
        return threat_score + pattern_score + runsoftwo_score + pos_score


class AlphaBetav2D(AlphaBetaD):
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
        def_factor = 1.5
        curr_player = self.player
        opp_player = 1 - self.player
        
        my_patterns, my_threats = utils.count_forcing_threats(state, curr_player)
        opp_patterns, opp_threats = utils.count_forcing_threats(state, opp_player)

        
        if my_threats >1: # maybe change return to add
            return -9999
        if opp_threats > 1:
            return 9999
        
        threat_score = 10 * (my_threats - opp_threats * def_factor)
        pattern_score = 3 * (my_patterns - opp_patterns * def_factor)

        my_runsoftwo = utils.count_runsoftwo(state, curr_player)
        opp_runsoftwo = utils.count_runsoftwo(state, opp_player)

        runsoftwo_score = 4 * (my_runsoftwo - opp_runsoftwo * def_factor)

        my_pos = utils.pos_score(state, curr_player)
        opp_pos = utils.pos_score(state, opp_player)

        pos_score = 5 *  (my_pos - opp_pos * def_factor)

        
        return threat_score + pattern_score + runsoftwo_score + pos_score
    
    def minimax(self, state, depth, is_max, curr_hash, history, alpha, beta):

        status = utils.game_status(state)
        #terminal state or depth cutoff
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)
        # moves = utils.order_moves(state, moves, is_max, self.player)

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
                    eval, _ = self.minimax(utils.make_move(state, move, True), depth-1, False, new_hash, new_history, alpha, beta)
                
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
                    eval, _= self.minimax(utils.make_move(state, move, False), depth-1, True, new_hash, new_history, alpha, beta)
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, min_eval)
            return min_eval, best_move
    
