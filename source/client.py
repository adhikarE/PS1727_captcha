import socket
import threading

HOST = '127.0.0.1'
PORT = int(input("Enter the port: "))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


def receive():
    while True:

        try:
            message = client.recv(1024).decode('ascii')  # Receiving message from server
            print(f"Server: {message}")

        except:
            print("Server Disconnected!")
            client.close()
            break


def write():
    while True:
        message = input("Enter your command: ")
        client.send(message.encode('ascii'))

        if message == "RST":
            client.close()
            break


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()