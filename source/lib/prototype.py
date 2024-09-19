import socket
import sys
import threading

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

DEBUG = True if input("Debugging (Y/N): ").upper() == 'Y' else False


class Utilities:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.public_pem = None

    def key_generation(self):
        """Generate RSA key pair and encode public key in PEM format."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def encrypt_message(self, message, public_key):
        """Encrypt a message using the provided public key."""
        if isinstance(message, str):
            message = message.encode('ascii')

        encrypted_message = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        if DEBUG:
            print("\n" + "=" * 50)
            print(f"Message before encryption: {message.decode('ascii')}")
            print(f"Encrypted message (hex): {encrypted_message.hex()}")
            print("=" * 50)
        return encrypted_message

    def decrypt_message(self, encrypted_message, private_key):
        """Decrypt a message using the provided private key."""
        decrypted_message = private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode('ascii')

        if DEBUG:
            print("\n" + "=" * 50)
            print(f"Encrypted message (hex): {encrypted_message.hex()}")
            print(f"Decrypted message: {decrypted_message}")
            print("=" * 50)

        return decrypted_message


class Bug(Utilities):
    def __init__(self, network_interface_1, legacy_application_ip, client_port, legacy_application_port):
        super().__init__()
        self.bug_server = None
        self.key_generation()
        self.legacy_application_ip = legacy_application_ip
        self.client_port = client_port
        self.legacy_application_port = legacy_application_port

        self.network_interface_1 = network_interface_1

        self.legacy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.legacy_socket.bind((self.network_interface_1, 0))
        self.legacy_socket.connect((self.legacy_application_ip, self.legacy_application_port))

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind((self.network_interface_1, self.client_port))
        self.client_socket.listen(1)

        self.is_running = True  # Flag to control server shutdown

    def process_client_data(self, client_socket):
        """Process incoming data from the client, decrypt it, log MAC/IP, and forward it to the legacy application."""
        while self.is_running:
            try:
                encrypted_message = client_socket.recv(256)
                if not encrypted_message:
                    break

                decrypted_message = self.decrypt_message(encrypted_message, self.private_key)

                if decrypted_message == 'rst':
                    print("Termination command received. Shutting down bug server...")

                    # Notify the client
                    client_socket.send("Connection terminated".encode('ascii'))

                    # Close sockets and shut down gracefully
                    self.is_running = False  # Stop server
                    client_socket.close()
                    self.legacy_socket.close()
                    self.client_socket.close()
                    return

                # Forward the decrypted message to the legacy application
                self.legacy_socket.send(decrypted_message.encode('ascii'))

            except Exception as e:
                print(f"Error in processing client data: {e}")
                break

        client_socket.close()

    def handle_legacy_responses(self, client_socket, client_public_key):
        """Handle outgoing data from the legacy application, encrypt it, and send it to the client."""
        while self.is_running:
            try:
                response = self.legacy_socket.recv(1024)
                if not response:
                    break

                encrypted_response = self.encrypt_message(response, client_public_key)
                client_socket.send(encrypted_response)

            except Exception as e:
                print(f"Error in handling legacy responses: {e}")
                break

        client_socket.close()

    def establish_client_connection(self, client_socket):
        """Send the public key to the client and start processing threads."""
        try:
            client_socket.send(self.public_pem)

            client_public_pem = client_socket.recv(1024)
            client_public_key = serialization.load_pem_public_key(client_public_pem)

            threading.Thread(target=self.process_client_data, args=(client_socket,)).start()
            threading.Thread(target=self.handle_legacy_responses, args=(client_socket, client_public_key)).start()

        except Exception as e:
            print(f"Error in client connection: {e}")
            client_socket.close()

    def run(self):
        """Start the bug server to accept client connections."""
        print("Bug server started and listening...")
        while self.is_running:
            try:
                client_socket, addr = self.client_socket.accept()
                print(f"Connected to client with address {addr}")
                self.establish_client_connection(client_socket)
            except OSError as e:
                if not self.is_running:
                    print("Server shutting down gracefully.")
                else:
                    print(f"Error in accepting connection: {e}")
                break


class Client(Utilities):
    def __init__(self, static_ip, bug_ip, bug_port):

        super().__init__()

        self.server_public_key = None
        self.key_generation()

        self.static_ip = static_ip

        self.bug_ip = bug_ip
        self.bug_port = bug_port

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind((self.static_ip, 0))

    def connect_to_server(self):
        """Connect to the server and exchange public keys."""
        self.client_socket.connect((self.bug_ip, self.bug_port))
        self.client_socket.send(self.public_pem)

        server_public_pem = self.client_socket.recv(1024)
        self.server_public_key = serialization.load_pem_public_key(server_public_pem)

    def communicate_with_server(self):
        """Send and receive messages from the server."""
        while True:
            try:
                message = input("Enter message: ").lower()

                if message:
                    # If the command is 'rst', terminate the connection
                    if message == "rst":
                        encrypted_message = self.encrypt_message(message.encode('ascii'), self.server_public_key)
                        self.client_socket.send(encrypted_message)

                        # Wait for the server to acknowledge the termination
                        ack = self.client_socket.recv(1024)
                        print(f"Server: {ack.decode('ascii')}")  # Display the termination message from the server

                        print("Connection terminated by the server.")
                        self.client_socket.close()

                        print("Client disconnected. Exiting...")
                        sys.exit()  # Exit the program completely after closing the socket

                    # Encrypt the message and send
                    encrypted_message = self.encrypt_message(message.encode('ascii'), self.server_public_key)

                    # Send encrypted message to the server
                    self.client_socket.send(encrypted_message)

                    # Receive and decrypt the server's response
                    response = self.client_socket.recv(1024)
                    decrypted_response = self.decrypt_message(response, self.private_key)
                    print(f"Server: {decrypted_response}")

            except Exception as e:
                print(f"Error communicating with server: {e}")
                self.client_socket.close()  # Ensure the socket is closed in case of an exception
                print("Client disconnected. Exiting...")
                sys.exit()  # Exit completely to avoid further errors
