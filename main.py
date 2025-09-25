# PARTIALLY GENERATED WITH GEMINI DUE TO THE INTEGRATION OF GAME SERVER AND LARGER GRIDS
import argparse
import socket
import utils
from games import Connect3M, Connect3L, Connect3MServer, Connect3LServer


def play_local_game(args):
    """Handles the setup and execution of a local, interactive game."""
    # Logic to select grid size and model
    if args.grid == 'large':
        print("Large grid selected. The only available model is 'ab2D'.")
        model = 'ab2D'
        game_class = Connect3L
    else: # standard grid
        model = str(input("Choose your model ('mm', 'mmD', 'mm2', 'mm2D', 'ab', 'abD', 'ab2', 'ab2D'): "))
        game_class = Connect3M

    while True:
        try:
            choice = int(input("Choose your player: 0 (White, moves first) or 1 (Black, moves second): "))
            if choice in [0, 1]:
                human_player = choice
                break
            else:
                print("Invalid choice. Please enter 0 or 1.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Instantiate the correct game class
    game = game_class(model=model, human_player=human_player)
    game.play()

def play_server_game(args):
    """Handles connecting to a server and running a network game."""
    if args.server_type == 'prof':
        host = f'156trlinux-{args.host_number}.ece.mcgill.ca'
        port = 12345
    else:
        host = '127.0.0.1'
        port = 12345
    print(f"Attempting to connect to server at {host}:{port}...")

    # Logic to select correct model and game class based on grid size
    if args.grid == 'large':
        print("Large grid selected for server play. Model is 'ab2D'.")
        model = 'ab2D'
        server_game_class = Connect3LServer
    else:
        model = str(input("Choose AI model for this client ('mm', 'mmD', 'mm2', 'mm2D', 'ab', 'abD', 'ab2', 'ab2D'): "))
        server_game_class = Connect3MServer

    color = str(input("Choose color for this client ('white' or 'black'): ")).lower()
    if color not in ['white', 'black']:
        print("Invalid color choice. Exiting.")
        return
        
    my_player_id = 0 if color == 'white' else 1
    initial_message = f"{args.gameid} {color}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print("Successfully connected to server.")
            print(f"Sending setup message: '{initial_message}'")
            utils.send_move(s, initial_message)

            # Instantiate the correct server game client
            game_client = server_game_class(model=model, my_player_id=my_player_id, sock=s)
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
                        help="Select grid size ('standard' or 'large').")
    parser.add_argument('--server_type', type=str, default='local', choices=['local', 'prof'],
                        help="Select which server to connect to in server mode.")
    parser.add_argument('--gameid', type=str, default='game01',
                        help="Game ID for the server.")
    parser.add_argument('--host_number', type=int, default=1, choices=range(1, 11),
                        help="Specify the server machine number (1-10) for the prof's server.")
    
    args = parser.parse_args()

    if args.mode == 'local':
        play_local_game(args)
    elif args.mode == 'server':
        play_server_game(args)

# python main.py --mode server --server_type prof --host_number 5