import os
import socket
import sys
import threading
from configparser import ConfigParser

config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
config = ConfigParser()
config.read(config_file)

DEBUG = True if input("Debugging (Y/N): ").upper() == 'Y' else False

# HOST = input("Enter the static IP address you want to set: ")
# PORT = int(input("Enter the port for legacy application: "))

STATIC_IP = config["Default"]["host"]
PORT = int(config["Legacy_Application"]["port"])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((STATIC_IP, PORT))
server.listen()

client_list = []
DATA = {
    "data": "Aadya, Anusha, Kavish, Sia, Suresh, Tatsam",
    "sih": "Smart India Hackathon Problem Statement Number 1727"
}


def handle_client(client, address):
    """Handles the communication with a connected client."""
    print(f"{client} Connected from {address}")
    client_list.append(client)

    while True:
        try:
            message = client.recv(1024).decode("ascii")

            if not message:
                break  # Client disconnected

            if DEBUG:
                print("\n" + "=" * 50)
                print(f"Received PT response from {address}: \n{message}")
                print("=" * 50)

            # Command processing
            if message in DATA:
                client.send(DATA[message].encode("ascii"))
                if DEBUG:
                    print("\n" + "=" * 50)
                    print(f"Transmitted PT data: \n{DATA[message]}")
                    print("=" * 50)
            elif message.lower() == "rst":
                client_list.remove(client)
                client.send("rst".encode("ascii"))
                print(f"{client} disconnected!")

                # Close client socket before exiting
                client.close()

                print("Closing server socket...")
                server.close()  # Close the server socket
                print("Terminating legacy application server...")
                sys.exit()  # Graceful exit after closing sockets
            else:
                client.send("Could not process!".encode("ascii"))
                if DEBUG:
                    print("\n" + "=" * 50)
                    print(f"Transmitted error message: Could not process!")
                    print("=" * 50)

        except Exception as e:
            print(f"Error with client {address}: {e}")
            break

    client.close()


def start_server():
    """Start the server to accept multiple clients."""
    print("Legacy Application Server started and listening...")

    while True:
        client, address = server.accept()
        # Spawn a new thread for each client
        client_thread = threading.Thread(
            target=handle_client, args=(client, address))
        client_thread.start()


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("Server is shutting down...")
        server.close()  # Ensure the server socket is closed on shutdown
        sys.exit()
