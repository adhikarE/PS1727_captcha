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

# Load RSA private key for decryption
with open(PRIVATE_KEY_PATH, 'rb') as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Set up a client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', int(input("Enter the port: "))))  # Connect to bug.py server

# Receive the public key from bug.py
public_pem = client.recv(1024)
public_key = serialization.load_pem_public_key(public_pem)

def receive():
    """Receive encrypted messages from the server, decrypt them, and print them."""
    while True:
        try:
            encrypted_message = client.recv(256)
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

            print(f"Server: {decrypted_message}")
        except Exception as e:
            print(f"Decryption error: {e}")
            client.close()
            break

def write():
    """Read commands from user, encrypt them, and send to the server."""
    while True:
        message = input("Enter your command: ")
        
        # Encrypt the message to be sent
        encrypted_message = public_key.encrypt(
            message.encode('ascii'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        client.send(encrypted_message)

        if message == "RST":
            client.close()
            break

# Start threads for receiving and sending data
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
