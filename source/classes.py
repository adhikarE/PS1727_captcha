import socket
import threading
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# Add the DEBUG mode
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
    def __init__(self, host, bug_port, legacy_port):
        super().__init__()
        self.key_generation()
        self.host = host
        self.bug_port = bug_port
        self.legacy_port = legacy_port

        self.legacy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.legacy_socket.connect((self.host, self.legacy_port))

        self.bug_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bug_server.bind((self.host, self.bug_port))
        self.bug_server.listen(1)

    def process_client_data(self, client_socket):
        """Process incoming data from the client, decrypt it, log MAC/IP, and forward it to the legacy application."""
        while True:
            try:
                encrypted_message = client_socket.recv(256)
                if not encrypted_message:
                    break

                decrypted_message = self.decrypt_message(encrypted_message, self.private_key)

                # Forward the decrypted message to the legacy application
                self.legacy_socket.send(decrypted_message.encode('ascii'))

            except Exception as e:
                print(f"Error in processing client data: {e}")
                client_socket.close()
                break

    def handle_legacy_responses(self, client_socket, client_public_key):
        """Handle outgoing data from the legacy application, encrypt it, and send it to the client."""
        while True:
            try:
                response = self.legacy_socket.recv(1024)
                if not response:
                    break

                encrypted_response = self.encrypt_message(response, client_public_key)
                client_socket.send(encrypted_response)

            except Exception as e:
                print(f"Error in handling legacy responses: {e}")
                client_socket.close()
                break

    def establish_client_connection(self, client_socket):
        """Send the public key to the client and start processing threads."""
        client_socket.send(self.public_pem)

        client_public_pem = client_socket.recv(1024)
        client_public_key = serialization.load_pem_public_key(client_public_pem)

        threading.Thread(target=self.process_client_data, args=(client_socket,)).start()
        threading.Thread(target=self.handle_legacy_responses, args=(client_socket, client_public_key)).start()

    def run(self):
        """Start the bug server to accept client connections."""
        print("Bug server started and listening...")
        while True:
            client_socket, addr = self.bug_server.accept()
            print(f"Connected to client with address {addr}")
            self.establish_client_connection(client_socket)


class Client(Utilities):
    def __init__(self, server_host, server_port):
        super().__init__()
        self.key_generation()
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        """Connect to the server and exchange public keys."""
        self.client_socket.connect((self.server_host, self.server_port))
        self.client_socket.send(self.public_pem)

        server_public_pem = self.client_socket.recv(1024)
        self.server_public_key = serialization.load_pem_public_key(server_public_pem)

    def communicate_with_server(self):
        """Send and receive messages from the server."""
        while True:
            try:
                message = input("Enter message: ")
                if message:
                    encrypted_message = self.encrypt_message(message.encode('ascii'), self.server_public_key)
                    self.client_socket.send(encrypted_message)
                    response = self.client_socket.recv(1024)
                    decrypted_response = self.decrypt_message(response, self.private_key)
                    print(f"Server: {decrypted_response}")

            except Exception as e:
                print(f"Error communicating with server: {e}")
                break
