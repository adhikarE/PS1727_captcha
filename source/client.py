import os
import socket
import threading
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_DIR = os.path.join(BASE_DIR, '..')  # One folder up
DEBUG = True

HOST = '127.0.0.1'
PORT = int(input("Enter the port: "))


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
class dataHandeler:
    def __init__(self, KEY) -> None:
        self.KEY = KEY
        
    def encrypt(self, text):
        result = ""

        # traverse text
        for i in range(len(text)):
            char = text[i]

            # Encrypt uppercase characters
            if (char.isupper()):
                result += chr((ord(char) + self.KEY - 65) % 26 + 65)

            # Encrypt lowercase characters
            else:
                result += chr((ord(char) + self.KEY - 97) % 26 + 97)

        return result
    
    def decrypt(self, text):
        result = ""

        # traverse text
        for i in range(len(text)):
            char = text[i]

            # Encrypt uppercase characters
            if (char.isupper()):
                result += chr((ord(char) - self.KEY - 65) % 26 + 65)

            # Encrypt lowercase characters
            else:
                result += chr((ord(char) - self.KEY - 97) % 26 + 97)

        return result
        
    def ingress(self):  # TODO
        pass
    
    def egress(self):   # TODO
        pass

handler = dataHandeler(3)

def receive():
    """Receive encrypted messages from the server, decrypt them, and print them."""
    while True:
        try:
            encrypted_message = client.recv(256)
            if not encrypted_message:
                break
            
            print("\n" + "="*50)
            print(f"Received encrypted response: \n{encrypted_message.hex()}")
            print("="*50)

            # Decrypt the received encrypted message
            decrypted_message = private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode('ascii')
            
            message = client.recv(1024).decode('ascii')  # Receiving message from server

            if DEBUG == True: print(f"Debug message recieeved: {message}")

            message = handler.decrypt(message)

            print(f"Server: {message}")

            print(f"Decrypted response: \n{decrypted_message}")
            print("="*50 + "\n")
        except Exception as e:
            print(f"Decryption error: {e}")
            client.close()
            break

def write():
    """Read commands from user, encrypt them, and send to the server."""
    while True:
        # Prompt the user for input without an extra newline
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
        
        print("\n" + "="*50)
        print(f"Original message: \n{message}")
        print("="*50)
        print(f"Encrypted message: \n{encrypted_message.hex()}")
        print("="*50 + "\n")

        client.send(encrypted_message)  # Send encrypted message to server
        
        message = handler.encrypt(message)

        if DEBUG == True: print(f"Debug encrypted text send: {message}")

        client.send(message.encode('ascii'))

        if message == "RST":
            client.close()
            break

# Start threads for receiving and sending data
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
