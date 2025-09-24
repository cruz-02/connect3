# main.py
import argparse
from games import Connect3M, Connect3L

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Play Dynamic Connect-3.")
    parser.add_argument('--grid', type=str, default='standard', choices=['standard', 'large'], # Added by gemini
                        help="Select the grid size ('standard' for 4x5, 'large' for 7x6).")
    args = parser.parse_args()

    while True:
        try:
            if args.grid == 'large':
                model = str(input("Choose your model ('mmv2', 'abpv2'): "))
            else:
                model = str(input("Choose your model ('mm', 'mmv2', 'abp', 'abpD', 'abpv2'): "))
            choice = int(input("Choose your player: 0 (White, moves first) or 1 (Black, moves second): "))
            if choice in [0, 1]:
                human = choice
                break
            else:
                print("Invalid choice. Please enter 0 or 1.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Instantiate the correct game class based on the command-line argument
    if args.grid == 'large':
        game = Connect3L(model=model, human_player=human)
    else:
        game = Connect3M(model=model, human_player=human)
        
    game.play()

    