# main.py
import argparse
import socket
import utils
from games import Connect3M, Connect3L, Connect3MServer

def play_local_game(args):
    """Handles the setup and execution of a local, interactive game."""
    # ... (This function remains unchanged) ...

def play_server_game(args):
    """Handles connecting to a server and running a network game."""
    # Determine server details
    if args.server_type == 'prof':
        # --- MODIFICATION IS HERE ---
        # Dynamically build the hostname based on the --host_number argument
        host = f'156trlinux-{args.host_number}.ece.mcgill.ca'
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

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Successfully connected to server.")

            print(f"Sending setup message: '{initial_message}'")
            utils.send_move(s, initial_message)

            game_client = Connect3MServer(model=model, my_player_id=my_player_id, sock=s)
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
    # --- NEW ARGUMENT IS HERE ---
    parser.add_argument('--host_number', type=int, default=1, choices=range(1, 11),
                        help="Specify the server machine number (1-10) for the prof's server.")
    
    args = parser.parse_args()

    if args.mode == 'local':
        play_local_game(args)
    elif args.mode == 'server':
        play_server_game(args)