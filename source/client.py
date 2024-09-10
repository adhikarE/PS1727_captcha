import socket
import threading
import uuid  # For MAC address retrieval
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

debug_opt = input("Debugging (Y/N): ")

if debug_opt.upper() == 'Y':
    DEBUG = True
else:
    DEBUG = False

# Generate RSA key pair (client's private and public key)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Export client's public key in PEM format to share with the server
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Get client's IP address
client_ip = socket.gethostbyname(socket.gethostname())

# Get client's MAC address
client_mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])

# Display MAC and IP for debugging
if DEBUG:
    print(f"Client IP: {client_ip}")
    print(f"Client MAC: {client_mac}")


REMOTE_HOST = input("Enter the remote host IP address: ")

# Set up a client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((REMOTE_HOST, int(input("Enter the port: "))))  # Connect to bug.py server

# Receive the server's public key
bug_public_pem = client.recv(1024)
bug_public_key = serialization.load_pem_public_key(bug_public_pem)

# Send the client's public key to the server
client.send(public_pem)

TERMINATE = "RST"


def receive():
    """Receive encrypted messages from the server, decrypt them, and print them."""
    while True:
        try:
            encrypted_message = client.recv(256)
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

            print(f"Decrypted response: \n{decrypted_message}")
            print("=" * 50 + "\n")

            if decrypted_message == "RST":
                break

        except Exception as e:
            print(f"Decryption error: {e}")
            client.close()
            break


def write():
    """Read commands from user, encrypt them, and send to the server."""
    while True:
        # Prompt the user for input without an extra newline
        message = input("Enter your command: ")

        # Add IP and MAC address to the message
        message_with_info = f"[IP:{client_ip}] [MAC:{client_mac}] {message}"

        # Encrypt the message to be sent
        encrypted_message = bug_public_key.encrypt(
            message_with_info.encode('ascii'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        if DEBUG:
            print("\n" + "=" * 50)
            print(f"\nOriginal message with IP and MAC: \n{message_with_info}")
            print("=" * 50)
            print(f"\nEncrypted message: \n{encrypted_message.hex()}")
            print("=" * 50 + "\n")

        client.send(encrypted_message)  # Send encrypted message to server

        if message == TERMINATE:
            client.close()
            break


# Start threads for receiving and sending data
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
