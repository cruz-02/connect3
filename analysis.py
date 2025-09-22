# analysis.py created completly with gemini

import matplotlib.pyplot as plt
import numpy as np
import utils
from agents import MiniMaxAgent, AlphaBeta

# --- Helper classes to add state counting ---

class AnalysisMiniMax(MiniMaxAgent):
    """
    An extension of the MiniMaxAgent to count the number of states visited.
    """
    def __init__(self, player):
        super().__init__(player)
        self.states_visited = 0

    def count_states_for_depth(self, depth):
        """Resets counter and runs the search for a given depth."""
        self.states_visited = 0
        # Player 0 (is_max=True) makes the first move from an empty board
        self.minimax(self.board, depth, True)
        return self.states_visited

    def minimax(self, state, depth, is_max):
        # A "visited state" is one where the minimax function is called
        self.states_visited += 1

        status = utils.game_status(state)
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)
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
    An extension of the AlphaBeta agent to count the number of states visited.
    """
    def __init__(self, player):
        super().__init__(player)
        self.states_visited = 0
    
    def count_states_for_depth(self, depth):
        """Resets counter and runs the search for a given depth."""
        self.states_visited = 0
        self.minimax(self.board, depth, True, float('-inf'), float('inf'))
        return self.states_visited

    def minimax(self, state, depth, is_max, alpha, beta):
        # A "visited state" is one where the minimax function is called
        self.states_visited += 1

        status = utils.game_status(state)
        if status is not None or depth == 0:
            return self.heuristic(state, status), None
        
        moves = self.gen_actions(state, is_max)
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
    minimax_states = []
    alphabeta_states = []

    # Instantiate the analysis agents
    # The player number (0) is arbitrary since we only need the search logic
    mm_agent = AnalysisMiniMax(player=0)
    ab_agent = AnalysisAlphaBeta(player=0)

    print("Running analysis... (This may take a moment for deeper searches)")
    for d in depths:
        print(f"\nCalculating for depth = {d}")
        
        # Run Minimax
        mm_count = mm_agent.count_states_for_depth(d)
        minimax_states.append(mm_count)
        print(f"  Minimax states visited: {mm_count}")
        
        # Run Alpha-Beta
        ab_count = ab_agent.count_states_for_depth(d)
        alphabeta_states.append(ab_count)
        print(f"  Alpha-Beta states visited: {ab_count}")

    # --- Plotting the results ---
    x = np.arange(len(depths))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, minimax_states, width, label='Minimax')
    rects2 = ax.bar(x + width/2, alphabeta_states, width, label='Alpha-Beta Pruning')

    ax.set_ylabel('Number of States Visited (Log Scale)')
    ax.set_xlabel('Search Depth Cutoff')
    ax.set_title('Minimax vs. Alpha-Beta: States Visited by Search Depth')
    ax.set_xticks(x)
    ax.set_xticklabels(depths)
    ax.legend()
    
    # Use a logarithmic scale for the y-axis to better visualize the difference
    ax.set_yscale('log')

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    
    # Save the plot to a file
    plt.savefig('states_visited_comparison.png')
    print("\nAnalysis complete. Chart saved as 'states_visited_comparison.png'")