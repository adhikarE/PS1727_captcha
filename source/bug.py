import socket
import threading

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

if input("Debugging (Y/N): ").upper() == 'Y':
    DEBUG = True
else:
    DEBUG = False

# Generate RSA key pair (bug's private and public key)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Encode server's public key in PEM format to share with the client
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

HOST = input("Enter the application IP address: ")
BUG_PORT = int(input("Enter the port for bug.py to listen for clients: "))  # Port for bug.py server
LEGACY_PORT = int(input("Enter the port for legacy_application.py to connect: "))  # Port for legacy application

# Set up a server socket for bug.py
bug_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bug_server.bind((HOST, BUG_PORT))
bug_server.listen(1)  # Listen for one incoming connection

# Connect to the legacy application
legacy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
legacy_socket.connect((HOST, LEGACY_PORT))


def extract_mac_ip(decrypted_message):
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



def ingress(client_socket):
    """Handle incoming data from the client, decrypt it, log MAC/IP, and forward it to the legacy application."""
    while True:
        try:
            encrypted_message = client_socket.recv(256)  # Receive encrypted data from client
            if not encrypted_message:
                break

            if DEBUG:
                print("\n" + "=" * 50)
                print(f"Received encrypted response: \n{encrypted_message.hex()}")
                print("=" * 50)

            # Decrypt the received encrypted message
            decrypted_message = private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode('ascii')

            # Extract IP, MAC, and actual command
            ip, mac, command = extract_mac_ip(decrypted_message)

            if DEBUG:
                print("\n" + "=" * 50)
                print(f"Received decrypted response: \n{decrypted_message}")
                if ip and mac:
                    print(f"Client IP: {ip}, Client MAC: {mac}")
                print(f"Command: {command}")
                print("=" * 50)

            # Forward only the command (without IP and MAC) to the legacy application
            legacy_socket.send(command.encode('ascii'))

        except Exception as e:
            print(f"Error in ingress: {e}")
            client_socket.close()
            break


def egress(client_socket, client_public_key):
    """Handle outgoing data from the legacy application, encrypt it, and send it to the client."""
    while True:
        try:
            response = legacy_socket.recv(1024)  # Receive data from the legacy application
            if not response:
                break

            # Encrypt the response from the legacy application
            encrypted_response = client_public_key.encrypt(
                response,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            if DEBUG:
                print("\n" + "=" * 50)
                print(f"Original response from legacy application: \n{response}")
                print("=" * 50)
                print(f"Encrypted response sent to client: \n{encrypted_response.hex()}")
                print("=" * 50 + "\n")

            # Send the encrypted response back to the client
            client_socket.send(encrypted_response)

        except Exception as e:
            print(f"Error in egress: {e}")
            client_socket.close()
            break


def handle_client(client_socket):
    """Send the public key to the client and start ingress and egress threads."""
    client_socket.send(public_pem)  # Send the public key to the client

    # Receive the client's public key
    client_public_pem = client_socket.recv(1024)
    client_public_key = serialization.load_pem_public_key(client_public_pem)

    # Start threads for handling incoming and outgoing data
    threading.Thread(target=ingress, args=(client_socket,)).start()
    threading.Thread(target=egress, args=(client_socket, client_public_key,)).start()


def start_bug_server():
    """Start the bug server to accept client connections."""
    print("Bug server started and listening...")

    while True:
        client_socket, addr = bug_server.accept()
        print(f"Connected to client with address {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


start_bug_server()
