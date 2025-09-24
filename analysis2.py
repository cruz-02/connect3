# analysis2.py

import matplotlib.pyplot as plt
import numpy as np
import time
import utils
from agents import MiniMaxAgent, AlphaBeta, MiniMaxAgentV2, AlphaBetaV2

# --- Analysis classes to add state counting to all four agent types ---

class AnalysisAgent(MiniMaxAgent):
    """Base class for analysis agents to handle board setup and counting."""
    def __init__(self, player):
        super().__init__(player)
        # The task requires starting from an empty board
        self.board = [
            [0, None, None, None, 1],
            [1, None, None, None, 0],
            [0, None, None, None, 1],
            [1, None, None, None, 0],
        ]
        self.states_visited = 0

    def count_states_for_depth(self, depth):
        # This is a placeholder to be implemented by child classes
        raise NotImplementedError

class AnalysisMiniMaxV1(AnalysisAgent):
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
    time_limit = 10.0  # 10 second cutoff

    agents = {
        "Minimax (Naive)": AnalysisMiniMaxV1(player=0),
        "Minimax (V2)": AnalysisMiniMaxV2(player=0),
        "Alpha-Beta (Naive)": AnalysisAlphaBetaV1(player=0),
        "Alpha-Beta (V2)": AnalysisAlphaBetaV2(player=0),
    }
    
    results = {name: {"states": [], "times": []} for name in agents}

    print("Running analysis with a 10-second time limit per run...")
    for d in depths:
        print(f"\n--- Calculating for depth = {d} ---")
        for name, agent in agents.items():
            start_time = time.time()
            count = agent.count_states_for_depth(d)
            duration = time.time() - start_time
            
            if duration > time_limit:
                print(f"  {name}: DNF (Did not finish in {time_limit:.0f}s)")
                results[name]["states"].append(np.nan)
                results[name]["times"].append(time_limit)
            else:
                results[name]["states"].append(count)
                results[name]["times"].append(duration)
                print(f"  {name}: {count} states in {duration:.4f}s")
    
    # --- Plotting the results ---
    x = np.arange(len(depths))
    width = 0.35
    
    # === FIGURE 1: Heuristic Performance (States Visited) ===
    fig1, (ax1_top, ax1_bottom) = plt.subplots(2, 1, figsize=(10, 12))
    
    # Top Plot: Minimax States
    rects1 = ax1_top.bar(x - width/2, results["Minimax (Naive)"]["states"], width, label='Naive Heuristic')
    rects2 = ax1_top.bar(x + width/2, results["Minimax (V2)"]["states"], width, label='Improved Heuristic (V2)')
    ax1_top.set_ylabel('Number of States Visited')
    ax1_top.set_title('Minimax: Effect of Heuristic on States Visited')
    ax1_top.set_xticks(x, depths)
    ax1_top.set_xlabel('Search Depth Cutoff')
    ax1_top.legend()
    ax1_top.bar_label(rects1, padding=3, fmt='%.0f')
    ax1_top.bar_label(rects2, padding=3, fmt='%.0f')

    # Bottom Plot: Alpha-Beta States
    rects3 = ax1_bottom.bar(x - width/2, results["Alpha-Beta (Naive)"]["states"], width, label='Naive Heuristic')
    rects4 = ax1_bottom.bar(x + width/2, results["Alpha-Beta (V2)"]["states"], width, label='Improved Heuristic (V2)')
    ax1_bottom.set_ylabel('Number of States Visited (Log Scale)')
    ax1_bottom.set_title('Alpha-Beta: Effect of Heuristic on States Visited')
    ax1_bottom.set_xticks(x, depths)
    ax1_bottom.set_xlabel('Search Depth Cutoff')
    ax1_bottom.set_yscale('log')
    ax1_bottom.legend()
    ax1_bottom.bar_label(rects3, padding=3, fmt='%.0f')
    ax1_bottom.bar_label(rects4, padding=3, fmt='%.0f')

    fig1.tight_layout(pad=3.0)
    plt.savefig('heuristic_performance.png')
    print("\nSaved chart 1: 'heuristic_performance.png'")

    # === FIGURE 2: Computational Tradeoffs (Time) ===
    fig2, (ax2_top, ax2_bottom) = plt.subplots(2, 1, figsize=(10, 12))

    # Top Plot: Minimax Time
    rects5 = ax2_top.bar(x - width/2, results["Minimax (Naive)"]["times"], width, label='Naive Heuristic')
    rects6 = ax2_top.bar(x + width/2, results["Minimax (V2)"]["times"], width, label='Improved Heuristic (V2)')
    ax2_top.set_ylabel('Time Taken (seconds)')
    ax2_top.set_title('Minimax: Computational Tradeoff of Heuristic Complexity')
    ax2_top.set_xticks(x, depths)
    ax2_top.set_xlabel('Search Depth Cutoff')
    ax2_top.legend()
    for i, rect in enumerate(rects6): # Add DNF labels for V2
        if results["Minimax (V2)"]["states"][i] is np.nan:
            ax2_top.text(rect.get_x() + rect.get_width() / 2., time_limit, 'DNF', ha='center', va='bottom')

    # Bottom Plot: Alpha-Beta Time
    rects7 = ax2_bottom.bar(x - width/2, results["Alpha-Beta (Naive)"]["times"], width, label='Naive Heuristic')
    rects8 = ax2_bottom.bar(x + width/2, results["Alpha-Beta (V2)"]["times"], width, label='Improved Heuristic (V2)')
    ax2_bottom.set_ylabel('Time Taken (seconds)')
    ax2_bottom.set_title('Alpha-Beta: Computational Tradeoff of Heuristic Complexity')
    ax2_bottom.set_xticks(x, depths)
    ax2_bottom.set_xlabel('Search Depth Cutoff')
    ax2_bottom.legend()
    for i, rect in enumerate(rects8): # Add DNF labels for V2
        if results["Alpha-Beta (V2)"]["states"][i] is np.nan:
            ax2_bottom.text(rect.get_x() + rect.get_width() / 2., time_limit, 'DNF', ha='center', va='bottom')
    
    fig2.tight_layout(pad=3.0)
    plt.savefig('computational_tradeoffs.png')
    print("Saved chart 2: 'computational_tradeoffs.png'")
    print("\nAnalysis complete.")