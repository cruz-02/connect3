# analysis2.py

import matplotlib.pyplot as plt
import numpy as np
import utils
from agents import MiniMaxAgent, AlphaBeta, MiniMaxAgentV2, AlphaBetaV2

# --- Analysis classes to add state counting to all four agent types ---

class AnalysisAgent:
    """Base class for analysis agents to handle board setup and counting."""
    def __init__(self, player):
        # The task requires starting from an empty board for a fair comparison
        self.board = [
        [0, None, None, None, 1],
        [1, None, None, None, 0],
        [0, None, None, None, 1],
        [1, None, None, None, 0],
        ]
        self.states_visited = 0

class AnalysisMiniMaxV1(MiniMaxAgent, AnalysisAgent):
    def count_states_for_depth(self, depth):
        self.states_visited = 0
        self.minimax(self.board, depth, True)
        return self.states_visited

    def minimax(self, state, depth, is_max):
        self.states_visited += 1
        return super().minimax(state, depth, is_max)

class AnalysisAlphaBetaV1(AlphaBeta, AnalysisAgent):
    def count_states_for_depth(self, depth):
        self.states_visited = 0
        self.minimax(self.board, depth, True, float('-inf'), float('inf'))
        return self.states_visited
    
    def minimax(self, state, depth, is_max, alpha, beta):
        self.states_visited += 1
        return super().minimax(state, depth, is_max, alpha, beta)

class AnalysisMiniMaxV2(MiniMaxAgentV2, AnalysisAgent):
    def count_states_for_depth(self, depth):
        self.states_visited = 0
        self.minimax(self.board, depth, True)
        return self.states_visited
    
    def minimax(self, state, depth, is_max):
        self.states_visited += 1
        return super().minimax(state, depth, is_max)

class AnalysisAlphaBetaV2(AlphaBetaV2, AnalysisAgent):
    def count_states_for_depth(self, depth):
        self.states_visited = 0
        self.minimax(self.board, depth, True, float('-inf'), float('inf'))
        return self.states_visited

    def minimax(self, state, depth, is_max, alpha, beta):
        self.states_visited += 1
        return super().minimax(state, depth, is_max, alpha, beta)

# --- Main Analysis Execution ---
if __name__ == '__main__':
    depths = [3, 4, 5, 6]

    agents = {
        "Minimax (Naive)": AnalysisMiniMaxV1(player=0),
        "Minimax (V2)": AnalysisMiniMaxV2(player=0),
        "Alpha-Beta (Naive)": AnalysisAlphaBetaV1(player=0),
        "Alpha-Beta (V2)": AnalysisAlphaBetaV2(player=0),
    }
    
    results = {name: [] for name in agents}

    print("Running state count analysis for heuristics...")
    for d in depths:
        print(f"\n--- Calculating for depth = {d} ---")
        for name, agent in agents.items():
            count = agent.count_states_for_depth(d)
            results[name].append(count)
            print(f"  {name}: {count} states")
    
    # --- Plotting the results ---
    x = np.arange(len(depths))
    width = 0.35
    
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(10, 12))
    
    # Top Plot: Minimax States
    rects1 = ax_top.bar(x - width/2, results["Minimax (Naive)"], width, label='Naive Heuristic')
    rects2 = ax_top.bar(x + width/2, results["Minimax (V2)"], width, label='Improved Heuristic (V2)')
    ax_top.set_ylabel('Number of States Visited')
    ax_top.set_title('Minimax: Effect of Heuristic on States Visited')
    ax_top.set_xticks(x, depths)
    ax_top.set_xlabel('Search Depth Cutoff')
    ax_top.legend()
    ax_top.bar_label(rects1, padding=3, fmt='%.0f')
    ax_top.bar_label(rects2, padding=3, fmt='%.0f')

    # Bottom Plot: Alpha-Beta States
    rects3 = ax_bottom.bar(x - width/2, results["Alpha-Beta (Naive)"], width, label='Naive Heuristic')
    rects4 = ax_bottom.bar(x + width/2, results["Alpha-Beta (V2)"], width, label='Improved Heuristic (V2)')
    ax_bottom.set_ylabel('Number of States Visited (Log Scale)')
    ax_bottom.set_title('Alpha-Beta: Effect of Heuristic on States Visited')
    ax_bottom.set_xticks(x, depths)
    ax_bottom.set_xlabel('Search Depth Cutoff')
    ax_bottom.set_yscale('log')
    ax_bottom.legend()
    ax_bottom.bar_label(rects3, padding=3, fmt='%.0f')
    ax_bottom.bar_label(rects4, padding=3, fmt='%.0f')

    fig.tight_layout(pad=3.0)
    plt.savefig('heuristic_states_comparison.png')
    print("\nAnalysis complete. Chart saved as 'heuristic_states_comparison.png'")