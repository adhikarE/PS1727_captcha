import os
import socket
import threading
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

# Determine the directory one folder above the current working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_DIR = os.path.join(BASE_DIR, '..')  # One folder up

# File paths for RSA keys
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, 'private_key.pem')
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, 'public_key.pem')

# Load the RSA public key
with open(PUBLIC_KEY_PATH, 'rb') as f:
    public_key = serialization.load_pem_public_key(f.read())

# Load the RSA private key
with open(PRIVATE_KEY_PATH, 'rb') as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Export public key in PEM format to send to the client
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

HOST = '127.0.0.1'
BUG_PORT = int(input("Enter the port for bug.py to listen: "))  # Port for bug.py server
LEGACY_PORT = int(input("Enter the port for legacy_application.py to connect: "))  # Port for legacy application

# Set up a server socket for bug.py
bug_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bug_server.bind((HOST, BUG_PORT))
bug_server.listen(1)  # Listen for one incoming connection

# Connect to the legacy application
legacy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
legacy_socket.connect((HOST, LEGACY_PORT))

def ingress(client_socket):
    """Handle incoming data from the client, decrypt it, and forward it to the legacy application."""
    while True:
        try:
            encrypted_message = client_socket.recv(256)  # Receive encrypted data from client
            if not encrypted_message:
                break
            
            # Decrypt the received encrypted message
            decrypted_message = private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode('ascii')
            
            # Forward decrypted message to the legacy application
            legacy_socket.send(decrypted_message.encode('ascii'))

        except Exception as e:
            print(f"Error in ingress: {e}")
            client_socket.close()
            break

def egress(client_socket):
    """Handle outgoing data from the legacy application, encrypt it, and send it to the client."""
    while True:
        try:
            response = legacy_socket.recv(1024)  # Receive data from the legacy application
            if not response:
                break
            
            # Encrypt the response from the legacy application
            encrypted_response = public_key.encrypt(
                response,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Send the encrypted response back to the client
            client_socket.send(encrypted_response)

        except Exception as e:
            print(f"Error in egress: {e}")
            client_socket.close()
            break

def handle_client(client_socket):
    """Send the public key to the client and start ingress and egress threads."""
    client_socket.send(public_pem)  # Send the public key to the client

    # Start threads for handling incoming and outgoing data
    ingress_thread = threading.Thread(target=ingress, args=(client_socket,))
    egress_thread = threading.Thread(target=egress, args=(client_socket,))

    ingress_thread.start()
    egress_thread.start()

    ingress_thread.join()
    egress_thread.join()

def start_bug_server():
    """Start the bug server to accept client connections."""
    print("Bug server started and listening...")

    while True:
        client_socket, addr = bug_server.accept()
        print(f"Connected to client with address {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

start_bug_server()
