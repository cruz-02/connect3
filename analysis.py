# analysis.py
#  GEMINI GENERATED

import matplotlib.pyplot as plt
import numpy as np
import utils
from agents import MiniMaxAgent, AlphaBeta

# --- Helper classes to add state counting and move reversal ---

class AnalysisMiniMax(MiniMaxAgent):
    """
    An extension of the MiniMaxAgent to count states and optionally reverse move order.
    """
    def __init__(self, player, reverse_moves=False):
        super().__init__(player)
        # The task requires starting from an empty board
        self.states_visited = 0
        self.reverse_moves = reverse_moves

    def count_states_for_depth(self, depth):
        """Resets counter and runs the search for a given depth."""
        self.states_visited = 0
        self.minimax(self.board, depth, True)
        return self.states_visited

    def minimax(self, state, depth, is_max):
        # A "visited state" is one where the minimax function is called
        self.states_visited += 1

        status = utils.game_status(state)
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)
        if self.reverse_moves:
            moves.reverse() # Reverse the move order for the experiment
        
        best_move = moves[0] if moves else None

        if is_max:
            max_eval = float('-inf')
            for move in moves:
                new_state = utils.make_move(state, move, True)
                eval_score, _ = self.minimax(new_state, depth - 1, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                new_state = utils.make_move(state, move, False)
                eval_score, _ = self.minimax(new_state, depth - 1, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            return min_eval, best_move

class AnalysisAlphaBeta(AlphaBeta):
    """
    An extension of the AlphaBeta agent to count states and optionally reverse move order.
    """
    def __init__(self, player, reverse_moves=False):
        super().__init__(player)
        self.states_visited = 0
        self.reverse_moves = reverse_moves
    
    def count_states_for_depth(self, depth):
        """Resets counter and runs the search for a given depth."""
        self.states_visited = 0
        self.minimax(self.board, depth, True, float('-inf'), float('inf'))
        return self.states_visited

    def minimax(self, state, depth, is_max, alpha, beta):
        self.states_visited += 1

        status = utils.game_status(state)
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)
        if self.reverse_moves:
            moves.reverse() # Reverse the move order for the experiment

        best_move = moves[0] if moves else None

        if is_max:
            max_eval = float('-inf')
            for move in moves:
                new_state = utils.make_move(state, move, True)
                eval_score, _ = self.minimax(new_state, depth - 1, False, alpha, beta)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                new_state = utils.make_move(state, move, False)
                eval_score, _ = self.minimax(new_state, depth - 1, True, alpha, beta)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

# --- Main Analysis Execution ---
if __name__ == '__main__':
    depths = [3, 4, 5, 6]
    minimax_normal_states = []
    minimax_reversed_states = []
    alphabeta_normal_states = []
    alphabeta_reversed_states = []

    # Instantiate all four agent configurations for analysis
    mm_agent_normal = AnalysisMiniMax(player=0, reverse_moves=False)
    mm_agent_reversed = AnalysisMiniMax(player=0, reverse_moves=True)
    ab_agent_normal = AnalysisAlphaBeta(player=0, reverse_moves=False)
    ab_agent_reversed = AnalysisAlphaBeta(player=0, reverse_moves=True)

    print("Running analysis... (This may take a moment for deeper searches)")
    for d in depths:
        print(f"\nCalculating for depth = {d}")
        
        # Minimax Normal
        count = mm_agent_normal.count_states_for_depth(d)
        minimax_normal_states.append(count)
        print(f"  Minimax (Normal Order) states: {count}")
        
        # Minimax Reversed
        count = mm_agent_reversed.count_states_for_depth(d)
        minimax_reversed_states.append(count)
        print(f"  Minimax (Reversed Order) states: {count}")

        # Alpha-Beta Normal
        count = ab_agent_normal.count_states_for_depth(d)
        alphabeta_normal_states.append(count)
        print(f"  Alpha-Beta (Normal Order) states: {count}")
        
        # Alpha-Beta Reversed
        count = ab_agent_reversed.count_states_for_depth(d)
        alphabeta_reversed_states.append(count)
        print(f"  Alpha-Beta (Reversed Order) states: {count}")

    # --- Plotting the results ---
    x = np.arange(len(depths))
    width = 0.35
    
    # === FIGURE 1: Minimax vs. Alpha-Beta (First Request) ===
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    rects1 = ax1.bar(x - width/2, minimax_normal_states, width, label='Minimax')
    rects2 = ax1.bar(x + width/2, alphabeta_normal_states, width, label='Alpha-Beta Pruning')

    ax1.set_ylabel('Number of States Visited (Log Scale)')
    ax1.set_xlabel('Search Depth Cutoff')
    ax1.set_title('Minimax vs. Alpha-Beta: States Visited by Search Depth')
    ax1.set_xticks(x)
    ax1.set_xticklabels(depths)
    ax1.legend()
    ax1.set_yscale('log')
    ax1.bar_label(rects1, padding=3, fmt='%d')
    ax1.bar_label(rects2, padding=3, fmt='%d')
    fig1.tight_layout()
    plt.savefig('states_visited_comparison.png')
    print("\nSaved chart 1: 'states_visited_comparison.png'")

    # === FIGURE 2: Effect of Move Order (Second Request) ===
    fig2, (ax2_top, ax2_bottom) = plt.subplots(2, 1, figsize=(10, 12))
    
    # Top Plot: Minimax Comparison
    rects3 = ax2_top.bar(x - width/2, minimax_normal_states, width, label='Normal Order')
    rects4 = ax2_top.bar(x + width/2, minimax_reversed_states, width, label='Reversed Order')

    ax2_top.set_ylabel('Number of States Visited')
    ax2_top.set_title('Effect of Move Order on Minimax')
    ax2_top.set_xticks(x)
    ax2_top.set_xticklabels(depths)
    ax2_top.set_xlabel('Search Depth Cutoff')
    ax2_top.legend()
    ax2_top.bar_label(rects3, padding=3, fmt='%d')
    ax2_top.bar_label(rects4, padding=3, fmt='%d')

    # Bottom Plot: Alpha-Beta Comparison
    rects5 = ax2_bottom.bar(x - width/2, alphabeta_normal_states, width, label='Normal Order')
    rects6 = ax2_bottom.bar(x + width/2, alphabeta_reversed_states, width, label='Reversed Order')

    ax2_bottom.set_ylabel('Number of States Visited (Log Scale)')
    ax2_bottom.set_title('Effect of Move Order on Alpha-Beta Pruning')
    ax2_bottom.set_xticks(x)
    ax2_bottom.set_xticklabels(depths)
    ax2_bottom.set_xlabel('Search Depth Cutoff')
    ax2_bottom.legend()
    ax2_bottom.set_yscale('log')
    ax2_bottom.bar_label(rects5, padding=3, fmt='%d')
    ax2_bottom.bar_label(rects6, padding=3, fmt='%d')

    fig2.tight_layout(pad=3.0)
    plt.savefig('move_order_comparison.png')
    print("Saved chart 2: 'move_order_comparison.png'")
    print("\nAnalysis complete.")