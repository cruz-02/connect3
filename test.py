import socket
import utils

# The server's hostname or IP address
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
# The port used by the server
PORT = 12345

# Use a 'with' statement to automatically close the socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        # Connect to the server
        s.connect((HOST, PORT))
        print(f"Successfully connected to {HOST}:{PORT}")

        # --- MODIFIED SECTION START ---

        # 1. Get a message string from the user via the terminal
        message_string = input("Enter message to send: ")

        # 2. Encode the string into bytes and send it
        s.sendall((message_string + '\n').encode('utf-8'))
        print(f"Sent: {message_string}")

        # Wait for a response from the server (buffer size 1024 bytes)
        data = s.recv(1024)
        print(f"Received: {data.decode('utf-8')}")

        while True:
            # 1. Get a message string from the user via the terminal
            message_string = input("Enter message to send: ")

            # 2. Encode the string into bytes and send it
            s.sendall((message_string + '\n').encode('utf-8'))
            print(f"Sent: {message_string}")

            # Wait for a response from the server (buffer size 1024 bytes)
            data = s.recv(1024)
            print(f"Received: {data.decode('utf-8')}")


    except ConnectionRefusedError:
        print(f"Connection failed. Is the server running on {HOST}:{PORT}?")
    except Exception as e:
        print(f"An error occurred: {e}")
