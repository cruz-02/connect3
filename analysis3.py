# analysis3.py
#  GEMINI GENERATED


import matplotlib.pyplot as plt
import numpy as np
import utils
from agents import MiniMaxAgentV2, MiniMaxv2D, AlphaBetaV2, AlphaBetav2D

# --- Analysis classes to add state counting ---

class AnalysisAgent:
    """Base class for analysis agents."""
    def __init__(self, player):
        self.board = [
        [0, None, None, None, 1],
        [1, None, None, None, 0],
        [0, None, None, None, 1],
        [1, None, None, None, 0],
        ]
        self.states_visited = 0

class AnalysisMiniMaxV2(MiniMaxAgentV2, AnalysisAgent):
    def count_states_for_depth(self, depth):
        self.states_visited = 0
        self.minimax(self.board, depth, True)
        return self.states_visited

    def minimax(self, state, depth, is_max):
        self.states_visited += 1
        return super().minimax(state, depth, is_max)

class AnalysisMiniMaxV2D(MiniMaxv2D, AnalysisAgent):
    def count_states_for_depth(self, depth):
        self.states_visited = 0
        init_hash = utils.calculate_initial_hash(self.board, self.zobrist_table)
        init_history = {init_hash: 1}
        self.minimax(self.board, depth, True, init_hash, init_history)
        return self.states_visited
    
    def minimax(self, state, depth, is_max, curr_hash, history):
        self.states_visited += 1
        return super().minimax(state, depth, is_max, curr_hash, history)

class AnalysisAlphaBetaV2(AlphaBetaV2, AnalysisAgent):
    def count_states_for_depth(self, depth):
        self.states_visited = 0
        self.minimax(self.board, depth, True, float('-inf'), float('inf'))
        return self.states_visited
    
    def minimax(self, state, depth, is_max, alpha, beta):
        self.states_visited += 1
        return super().minimax(state, depth, is_max, alpha, beta)

class AnalysisAlphaBetaV2D(AlphaBetav2D, AnalysisAgent):
    def count_states_for_depth(self, depth):
        self.states_visited = 0
        init_hash = utils.calculate_initial_hash(self.board, self.zobrist_table)
        init_history = {init_hash: 1}
        self.minimax(self.board, depth, True, init_hash, init_history, float('-inf'), float('inf'))
        return self.states_visited

    def minimax(self, state, depth, is_max, curr_hash, history, alpha, beta):
        self.states_visited += 1
        return super().minimax(state, depth, is_max, curr_hash, history, alpha, beta)

# --- Main Analysis Execution ---
if __name__ == '__main__':
    depths = [3, 4, 5, 6]
    agents = {
        "Minimax (V2)": AnalysisMiniMaxV2(player=0),
        "Minimax (V2D)": AnalysisMiniMaxV2D(player=0),
        "Alpha-Beta (V2)": AnalysisAlphaBetaV2(player=0),
        "Alpha-Beta (V2D)": AnalysisAlphaBetaV2D(player=0),
    }
    results = {name: [] for name in agents}

    print("Running state count analysis for V2 vs V2D heuristics...")
    for d in depths:
        print(f"\n--- Calculating for depth = {d} ---")
        for name, agent in agents.items():
            count = agent.count_states_for_depth(d)
            results[name].append(count)
            print(f"  {name}: {count} states")
    
    x = np.arange(len(depths))
    width = 0.35
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(10, 12))
    
    rects1 = ax_top.bar(x - width/2, results["Minimax (V2)"], width, label='V2 Heuristic')
    rects2 = ax_top.bar(x + width/2, results["Minimax (V2D)"], width, label='V2 Heuristic + Draw Detection')
    ax_top.set_ylabel('Number of States Visited')
    ax_top.set_title('Minimax: States Visited (V2 vs. V2D)')
    ax_top.set_xticks(x, depths)
    ax_top.set_xlabel('Search Depth Cutoff')
    ax_top.bar_label(rects1, padding=3)
    ax_top.bar_label(rects2, padding=3)
    ax_top.legend()
    
    rects3 = ax_bottom.bar(x - width/2, results["Alpha-Beta (V2)"], width, label='V2 Heuristic')
    rects4 = ax_bottom.bar(x + width/2, results["Alpha-Beta (V2D)"], width, label='V2 Heuristic + Draw Detection')
    ax_bottom.set_ylabel('Number of States Visited (Log Scale)')
    ax_bottom.set_title('Alpha-Beta: States Visited (V2 vs. V2D)')
    ax_bottom.set_xticks(x, depths)
    ax_bottom.set_xlabel('Search Depth Cutoff')
    ax_bottom.set_yscale('log')
    ax_bottom.bar_label(rects3, padding=3)
    ax_bottom.bar_label(rects4, padding=3)
    ax_bottom.legend()

    fig.tight_layout(pad=3.0)
    plt.savefig('v2_vs_v2d_states_comparison.png')
    print("\nAnalysis complete. Chart saved as 'v2_vs_v2d_states_comparison.png'")