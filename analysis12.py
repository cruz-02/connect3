# analysis12.py
#  GEMINI GENERATED


import matplotlib.pyplot as plt
import numpy as np
import time
import utils
from agents import MiniMaxAgent, AlphaBeta

def simulate_game_and_time_moves(agent_class, depth, moves_to_time=5):
    """
    Simulates a game between two instances of the same agent class.
    Records and returns the time taken for the first `moves_to_time` moves
    made by the first player (White).
    """
    player_white = agent_class(player=0)
    player_black = agent_class(player=1)
    
    current_board = [
        [0, None, None, None, 1],
        [1, None, None, None, 0],
        [0, None, None, None, 1],
        [1, None, None, None, 0],
    ]
    
    current_player_id = 0
    move_times = []
    
    # A game turn consists of a move from each player
    # We need 5 moves from white, so we need 5 full turns.
    for i in range(moves_to_time):
        
        # --- White's Turn (Player 0) ---
        if utils.game_status(current_board) is not None: break # Game ended early
        
        player_white.board = [row[:] for row in current_board] # Sync board
        
        start_time = time.time()
        move_str = player_white.find_best_move(depth)
        duration = time.time() - start_time
        move_times.append(duration)
        
        if not move_str: break # Game ended
        
        # Apply move to the master board
        is_max = (current_player_id == 0)
        move_tuple = ((int(move_str[0])-1, int(move_str[1])-1), (int(move_str[0])-1 + player_white.dirs[move_str[2]][0], int(move_str[1])-1 + player_white.dirs[move_str[2]][1]))
        current_board = utils.make_move(current_board, move_tuple, is_max)
        
        # Switch player
        current_player_id = 1
        
        # --- Black's Turn (Player 1) ---
        if utils.game_status(current_board) is not None: break

        player_black.board = [row[:] for row in current_board] # Sync board
        move_str = player_black.find_best_move(depth)

        if not move_str: break
        
        is_max = (current_player_id == 0)
        move_tuple = ((int(move_str[0])-1, int(move_str[1])-1), (int(move_str[0])-1 + player_black.dirs[move_str[2]][0], int(move_str[1])-1 + player_black.dirs[move_str[2]][1]))
        current_board = utils.make_move(current_board, move_tuple, is_max)
        
        # Switch player back to White
        current_player_id = 0

    return move_times

# --- Main Analysis Execution ---
if __name__ == '__main__':
    depths = [3, 4, 5, 6]
    num_games = 10
    moves_to_time = 5
    
    minimax_avg_times = []
    alphabeta_avg_times = []

    print("Running opening move timing analysis...")
    for d in depths:
        print(f"\n--- Calculating for depth = {d} ---")
        
        # --- Minimax Analysis ---
        print(f"  Running {num_games} games for Minimax...")
        total_mm_times = []
        for i in range(num_games):
            times = simulate_game_and_time_moves(MiniMaxAgent, d, moves_to_time)
            if times:
                total_mm_times.extend(times)
            print(f"    Game {i+1}/{num_games} complete.")
        
        if total_mm_times:
            avg_mm_time = sum(total_mm_times) / len(total_mm_times)
            minimax_avg_times.append(avg_mm_time)
            print(f"  Minimax Avg Time per Move: {avg_mm_time:.4f}s")
        else:
            minimax_avg_times.append(0) # In case no moves were made

        # --- Alpha-Beta Analysis ---
        print(f"  Running {num_games} games for Alpha-Beta...")
        total_ab_times = []
        for i in range(num_games):
            times = simulate_game_and_time_moves(AlphaBeta, d, moves_to_time)
            if times:
                total_ab_times.extend(times)
            print(f"    Game {i+1}/{num_games} complete.")

        if total_ab_times:
            avg_ab_time = sum(total_ab_times) / len(total_ab_times)
            alphabeta_avg_times.append(avg_ab_time)
            print(f"  Alpha-Beta Avg Time per Move: {avg_ab_time:.4f}s")
        else:
            alphabeta_avg_times.append(0)
            
    # --- Plotting the results ---
    x = np.arange(len(depths))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 7))
    rects1 = ax.bar(x - width/2, minimax_avg_times, width, label='Minimax')
    rects2 = ax.bar(x + width/2, alphabeta_avg_times, width, label='Alpha-Beta Pruning')

    ax.set_ylabel('Average Time per Move (seconds)')
    ax.set_xlabel('Search Depth Cutoff')
    ax.set_title('Average Time for First 5 Opening Moves')
    ax.set_xticks(x)
    ax.set_xticklabels(depths)
    ax.legend()

    ax.bar_label(rects1, padding=3, fmt='%.3fs')
    ax.bar_label(rects2, padding=3, fmt='%.3fs')

    fig.tight_layout()
    
    plt.savefig('opening_moves_timing.png')
    print("\nAnalysis complete. Chart saved as 'opening_moves_timing.png'")