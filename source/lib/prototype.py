import socket
import threading
import uuid  # For MAC address retrieval
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

DEBUG = (bool)

if input("Debugging (Y/N): ").upper() == 'Y':
    DEBUG = True

else:
    DEBUG = False

class Utilities():
    def __init__(self) -> None:
        self.private_key = (str)
        self.public_key = (str)     # public key that we will receive from other party
        self.public_pem = (str)
        self.terminate = "RST"

    # RSA key generation and public key encoding
    def key_generation(self) -> None:
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Encode server's public key in PEM format to share with the client
        self.public_pem = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def encryption(self, message, public_key) -> str:
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
        return encrypted_message
    
    def decryption(self, message, private_key) -> str:
        decrypted_message = private_key.decrypt(
                message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode('ascii')
        return decrypted_message
        

class Bug(Utilities):
    def __init__(self) -> None:
        super().__init__()
        self.key_generation()
        
        self.HOST = input("Enter the application IP address: ")
        self.BUG_PORT = int(input("Enter the port for bug.py to listen for clients: "))  # Port for bug.py server
        self.LEGACY_PORT = int(input("Enter the port for legacy_application.py to connect: "))  # Port for legacy application
        
        # Connect to the legacy application
        self.legacy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.legacy_socket.connect((self.HOST, self.LEGACY_PORT))
        
        # Set up a server socket for bug.py
        self.bug_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bug_server.bind((self.HOST, self.BUG_PORT))


    def extract_mac_ip(self, decrypted_message):
        """Extract MAC and IP address from the received message."""
        try:
            # Split the message by spaces to get IP, MAC, and the actual command
            parts = decrypted_message.split(" ", 2)
            
            # IP and MAC might be enclosed in brackets, so clean that up
            ip = parts[0].split(":")[1].strip("[]")
            
            # For MAC, instead of splitting by colon, capture the entire MAC format
            mac = parts[1].split(":", 1)[1].strip("[]")
            
            # The remainder is the command
            command = parts[2]
            
            return ip, mac, command
        except IndexError:
            return None, None, decrypted_message


    def client_handler(self):
        """Handle incoming data from the client, decrypt it, log MAC/IP, and forward it to the legacy application."""
        while True:
            try:
                encrypted_message = self.client_socket.recv(256)  # Receive encrypted data from client
                if not encrypted_message:
                    break

                if DEBUG:
                    print("\n" + "=" * 50)
                    print(f"Received encrypted response: \n{encrypted_message.hex()}")
                    print("=" * 50)

                # Decrypt the received encrypted message
                decrypted_message = self.decryption(encrypted_message, self.private_key)

                # Extract IP, MAC, and actual command
                ip, mac, command = self.extract_mac_ip(decrypted_message)

                if DEBUG:
                    print("\n" + "=" * 50)
                    print(f"Received decrypted response: \n{decrypted_message}")
                    if ip and mac:
                        print(f"Client IP: {ip}, Client MAC: {mac}")
                    print(f"Command: {command}")
                    print("=" * 50)

                # Forward only the command (without IP and MAC) to the legacy application
                self.legacy_socket.send(command.encode('ascii'))

            except Exception as e:
                print(f"Error in ingress: {e}")
                self.client_socket.close()
                break

    def application_handler(self, client_public_key):
        """Handle outgoing data from the legacy application, encrypt it, and send it to the client."""
        while True:
            try:
                response = self.legacy_socket.recv(1024)  # Receive data from the legacy application
                if not response:
                    break

                # Encrypt the response from the legacy application
                encrypted_response = self.encryption(response, client_public_key)

                if DEBUG:
                    print("\n" + "=" * 50)
                    print(f"Original response from legacy application: \n{response}")
                    print("=" * 50)
                    print(f"Encrypted response sent to client: \n{encrypted_response.hex()}")
                    print("=" * 50 + "\n")

                # Send the encrypted response back to the client
                self.client_socket.send(encrypted_response)

            except Exception as e:
                print(f"Error in egress: {e}")
                self.client_socket.close()
                break
    
    def handle_client(self):
        """Send the public key to the client and start ingress and egress threads."""
        self.client_socket.send(self.public_pem)  # Send the public key to the client

        # Receive the client's public key
        client_public_pem = self.client_socket.recv(1024)
        client_public_key = serialization.load_pem_public_key(client_public_pem)

        # Start threads for handling incoming and outgoing data
        threading.Thread(target = self.client_handler).start()
        threading.Thread(target = self.application_handler, args=(client_public_key,)).start()
    
    def run(self):

        self.bug_server.listen(1)  # Listen for one incoming connection
       
        """Start the bug server to accept client connections."""
        print("Bug server started and listening...")

        while True:
            self.client_socket, addr = self.bug_server.accept()
            print(f"Connected to client with address {addr}")
            client_thread = threading.Thread(target = self.handle_client)
            client_thread.start()

class Client(Utilities):
    def __init__(self) -> None:
        super().__init__()
        self.key_generation()
        self.client_mac = None
        self.client_ip = None
        
        self.remote_host = input("Enter the remote host IP address: ")

        # Set up a client socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.remote_host, int(input("Enter the port: "))))  # Connect to bug.py server


    def receive(self):
        """Receive encrypted messages from the server, decrypt them, and print them."""
        while True:
            try:
                encrypted_message = self.client.recv(256)
                if not encrypted_message:
                    break

                if DEBUG:
                    print("\n" + "=" * 50)
                    print(f"Received encrypted response: \n{encrypted_message.hex()}")
                    print("=" * 50)

                # Decrypt the received encrypted message
                decrypted_message = self.decryption(encrypted_message, self.private_key)

                print(f"Decrypted response: \n{decrypted_message}")
                print("=" * 50 + "\n")

                if decrypted_message == self.terminate:
                    break

            except Exception as e:
                print(f"Decryption error: {e}")
                self.client.close()
                break


    def write(self):
        """Read commands from user, encrypt them, and send to the server."""
        while True:
            # Prompt the user for input without an extra newline
            message = input("Enter your command: ")

            # Add IP and MAC address to the message
            message_with_info = f"[IP:{self.client_ip}] [MAC:{self.client_mac}] {message}"

            # Encrypt the message to be sent
            encrypted_message = self.encryption(message_with_info, self.public_key)

            if DEBUG:
                print("\n" + "=" * 50)
                print(f"\nOriginal message with IP and MAC: \n{message_with_info}")
                print("=" * 50)
                print(f"\nEncrypted message: \n{encrypted_message.hex()}")
                print("=" * 50 + "\n")

            self.client.send(encrypted_message)  # Send encrypted message to server

            if message == self.terminate:
                self.client.close()
                break

    def get_IP_MAC(self):
        # Get client's IP address
        self.client_ip = socket.gethostbyname(socket.gethostname())

        # Get client's MAC address
        self.client_mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])

        # Display MAC and IP for debugging
        if DEBUG:
            print(f"Client IP: {self.client_ip}")
            print(f"Client MAC: {self.client_mac}")
    
    def handle_bug(self):
        self.get_IP_MAC()
        bug_public_pem = self.client.recv(1024)
        self.public_key = serialization.load_pem_public_key(bug_public_pem)

        self.client.send(self.public_pem)

        # Start threads for receiving and sending data
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()

        
