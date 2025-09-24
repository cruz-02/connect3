# main.py MODIFIED BY GEMINI SO THAT IT WORKS WITH THE GAME SERVER.
import argparse
import socket
import utils
from games import Connect3M, Connect3L, Connect3MServer # Assuming Connect3MServer is your client class

def play_local_game(args):
    """Handles the setup and execution of a local, interactive game."""
    while True:
        try:
            if args.grid == 'large':
                model = str(input("Choose your model ('mmv2', 'abpv2'): "))
            else:
                model = str(input("Choose your model ('mm', 'mmv2', 'abp', 'abpv2'): "))
            
            choice = int(input("Choose your player: 0 (White, moves first) or 1 (Black, moves second): "))
            if choice in [0, 1]:
                human_player = choice
                break
            else:
                print("Invalid choice. Please enter 0 or 1.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Instantiate the correct local game class based on the grid size
    if args.grid == 'large':
        game = Connect3L(model=model, human_player=human_player)
    else:
        game = Connect3M(model=model, human_player=human_player)
        
    game.play()

def play_server_game(args):
    """Handles connecting to a server and running a network game."""
    # Determine server details based on the --server_type argument
    if args.server_type == 'prof':
        host = '156trlinux-1.ece.mcgill.ca'
        port = 12345
    else: # 'local'
        host = '127.0.0.1'
        port = 12345

    print(f"Attempting to connect to server at {host}:{port}...")

    # Get game details from the user
    model = str(input("Choose AI model for this client ('mmv2', 'abpv2'): "))
    color = str(input("Choose color for this client ('white' or 'black'): ")).lower()
    
    if color not in ['white', 'black']:
        print("Invalid color choice. Exiting.")
        return
        
    my_player_id = 0 if color == 'white' else 1
    initial_message = f"{args.gameid} {color}"

    # Use a 'with' statement to automatically close the socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Successfully connected to server.")

            # 1. Send the initial game setup message
            print(f"Sending setup message: '{initial_message}'")
            utils.send_move(s, initial_message)

            # 2. Instantiate the server-aware game client
            # The client needs to know its player ID and have the active socket
            game_client = Connect3MServer(model=model, my_player_id=my_player_id, sock=s)
            
            # 3. Start the network game loop
            game_client.play()

        except ConnectionRefusedError:
            print(f"Connection failed. Is the server running on {host}:{port}?")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Play Dynamic Connect-3.")
    parser.add_argument('--mode', type=str, default='local', choices=['local', 'server'],
                        help="Select play mode: 'local' for interactive, 'server' for network play.")
    parser.add_argument('--grid', type=str, default='standard', choices=['standard', 'large'],
                        help="Select grid size for local mode ('standard' or 'large').")
    parser.add_argument('--server_type', type=str, default='local', choices=['local', 'prof'],
                        help="Select which server to connect to in server mode.")
    parser.add_argument('--gameid', type=str, default='game01',
                        help="Game ID for the server.")
    
    args = parser.parse_args()

    if args.mode == 'local':
        play_local_game(args)
    elif args.mode == 'server':
        play_server_game(args)


# python main.py
# # Or for the large grid
# python main.py --grid large

# # Terminal 1 (White Player)
# python main.py --mode server --server_type local --gameid mygame

# # Terminal 2 (Black Player)
# python main.py --mode server --server_type local --gameid mygame

# # Example for a player choosing to be Black in game "tourney123"
# python main.py --mode server --server_type prof --gameid tourney123
# # The script will then prompt you to choose your color (white/black) and AI model.