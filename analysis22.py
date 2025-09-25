# analysis22.py
#  GEMINI GENERATED


import matplotlib.pyplot as plt
import numpy as np
import time
import utils
from agents import MiniMaxAgent, AlphaBeta, MiniMaxAgentV2, AlphaBetaV2

def simulate_game_and_time_moves(agent_white_class, agent_black_class, depth, moves_to_time=5):
    """
    Simulates a game, timing the first 5 moves of the White player.
    """
    player_white = agent_white_class(player=0)
    player_black = agent_black_class(player=1)
    
    # Start with the standard game board, not an empty one
    current_board = [
        [0, None, None, None, 1],
        [1, None, None, None, 0],
        [0, None, None, None, 1],
        [1, None, None, None, 0],
        ]
    
    current_player_id = 0
    move_times = []
    
    for i in range(moves_to_time):
        if utils.game_status(current_board) is not None: break

        # --- White's Turn (Player 0) ---
        player_white.board = [row[:] for row in current_board]
        start_time = time.time()
        move_str = player_white.find_best_move(depth)
        duration = time.time() - start_time
        move_times.append(duration)
        if not move_str: break
        
        move_tuple = ((int(move_str[0])-1, int(move_str[1])-1), (int(move_str[0])-1 + player_white.dirs[move_str[2]][0], int(move_str[1])-1 + player_white.dirs[move_str[2]][1]))
        current_board = utils.make_move(current_board, move_tuple, True)
        
        # --- Black's Turn (Player 1) ---
        if utils.game_status(current_board) is not None: break

        player_black.board = [row[:] for row in current_board]
        move_str = player_black.find_best_move(depth)
        if not move_str: break
        
        move_tuple = ((int(move_str[0])-1, int(move_str[1])-1), (int(move_str[0])-1 + player_black.dirs[move_str[2]][0], int(move_str[1])-1 + player_black.dirs[move_str[2]][1]))
        current_board = utils.make_move(current_board, move_tuple, False)
        
    return move_times

# --- Main Analysis Execution ---
if __name__ == '__main__':
    depths = [3, 4, 5, 6]
    num_games = 5 # Number of games to average over

    agent_classes = {
        "Minimax (Naive)": MiniMaxAgent,
        "Minimax (V2)": MiniMaxAgentV2,
        "Alpha-Beta (Naive)": AlphaBeta,
        "Alpha-Beta (V2)": AlphaBetaV2,
    }
    
    results = {name: [] for name in agent_classes}

    print("Running opening move timing analysis...")
    for d in depths:
        print(f"\n--- Calculating for depth = {d} ---")
        for name, agent_class in agent_classes.items():
            total_times = []
            print(f"  Running {num_games} games for {name}...")
            for i in range(num_games):
                # Agents play against themselves
                times = simulate_game_and_time_moves(agent_class, agent_class, d)
                if times: total_times.extend(times)
            
            avg_time = sum(total_times) / len(total_times) if total_times else 0
            results[name].append(avg_time)
            print(f"  -> Avg Time per Move: {avg_time:.4f}s")
            
    # --- Plotting the results ---
    x = np.arange(len(depths))
    width = 0.35

    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(10, 12))

    # Top Plot: Minimax Timing
    rects1 = ax_top.bar(x - width/2, results["Minimax (Naive)"], width, label='Naive Heuristic')
    rects2 = ax_top.bar(x + width/2, results["Minimax (V2)"], width, label='Improved Heuristic (V2)')
    ax_top.set_ylabel('Average Time per Move (seconds)')
    ax_top.set_title('Minimax: Average Time for First 5 Opening Moves')
    ax_top.set_xticks(x, depths)
    ax_top.set_xlabel('Search Depth Cutoff')
    ax_top.legend()
    ax_top.bar_label(rects1, padding=3, fmt='%.3fs')
    ax_top.bar_label(rects2, padding=3, fmt='%.3fs')

    # Bottom Plot: Alpha-Beta Timing
    rects3 = ax_bottom.bar(x - width/2, results["Alpha-Beta (Naive)"], width, label='Naive Heuristic')
    rects4 = ax_bottom.bar(x + width/2, results["Alpha-Beta (V2)"], width, label='Improved Heuristic (V2)')
    ax_bottom.set_ylabel('Average Time per Move (seconds)')
    ax_bottom.set_title('Alpha-Beta: Average Time for First 5 Opening Moves')
    ax_bottom.set_xticks(x, depths)
    ax_bottom.set_xlabel('Search Depth Cutoff')
    ax_bottom.legend()
    ax_bottom.bar_label(rects3, padding=3, fmt='%.3fs')
    ax_bottom.bar_label(rects4, padding=3, fmt='%.3fs')

    fig.tight_layout(pad=3.0)
    plt.savefig('heuristic_timing_comparison.png')
    print("\nAnalysis complete. Chart saved as 'heuristic_timing_comparison.png'")