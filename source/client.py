import socket
import threading

HOST = '127.0.0.1'
PORT = int(input("Enter the port: "))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

KEY = 3

def encrypt(text,s):
    result = ""

    for i in range(len(text)):
        char = text[i]

        if (char.isupper()):
            result += chr((ord(char) + s - 65) % 26 + 65)

        else:
            result += chr((ord(char) + s - 97) % 26 + 97)

    return result

def decrypt(text,s):
    result = ""

    for i in range(len(text)):
        char = text[i]

        if (char.isupper()):
            result += chr((ord(char) - s - 65) % 26 + 65)

        else:
            result += chr((ord(char) - s - 97) % 26 + 97)

    return result

def receive():
    while True:

        try:
            message = decrypt(client.recv(1024).decode('ascii'), KEY)  # Receiving message from server
            print(f"Server: {message}")

        except:
            print("Server Disconnected!")
            client.close()
            break

def write():
    while True:
        message = encrypt(input("Enter your command: "), KEY)
        client.send(message.encode('ascii'))

        if message == encrypt("RST", KEY):
            client.close()
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()