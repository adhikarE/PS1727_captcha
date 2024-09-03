import socket
import threading
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Generate RSA keys
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()

# Middleware ports
CLIENT_PORT = 65432  # Port to listen from client.py
LEGACY_PORT = 65433  # Port to communicate with legacy_application.py

# Host information
HOST = '127.0.0.1'

def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                # Receive encrypted message from client
                encrypted_message = b''
                while True:
                    part = client_socket.recv(1024)
                    if not part:
                        break
                    encrypted_message += part
                
                if not encrypted_message:
                    print("Client disconnected!")
                    break

                # Decrypt the message
                decrypted_message = private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode('ascii')
                print(f"Decrypted message from client: {decrypted_message}")

                # Forward the decrypted message to the legacy system
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as legacy_socket:
                    legacy_socket.connect((HOST, LEGACY_PORT))
                    legacy_socket.send(decrypted_message.encode('ascii'))
                    print(f"Sent to legacy system: {decrypted_message}")

                    # Receive the response from the legacy system
                    response = b''
                    while True:
                        part = legacy_socket.recv(1024)
                        if not part:
                            break
                        response += part
                    response = response.decode('ascii')
                    print(f"Response from legacy system: {response}")

                # Encrypt the response and send it back to the client
                encrypted_response = public_key.encrypt(
                    response.encode('ascii'),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                client_socket.send(encrypted_response)
                print("Response sent back to client")

            except Exception as e:
                print(f"An error occurred: {e}")
                client_socket.send(public_key.encrypt(
                    b"An error occurred in the middleware.",
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ))
                break


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, CLIENT_PORT))
        server_socket.listen()

        print(f"Middleware server listening on port {CLIENT_PORT}...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
