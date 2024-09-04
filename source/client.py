import socket
import threading

DEBUG = True

HOST = '127.0.0.1'
PORT = int(input("Enter the port: "))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

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
    while True:

        try:
            
            message = client.recv(1024).decode('ascii')  # Receiving message from server

            if DEBUG == True: print(f"Debug message recieeved: {message}")

            message = handler.decrypt(message)

            print(f"Server: {message}")

        except:
            print("Server Disconnected!")
            client.close()
            break


def write():
    while True:
        message = input("Enter your command: ")
        
        message = handler.encrypt(message)

        if DEBUG == True: print(f"Debug encrypted text send: {message}")

        client.send(message.encode('ascii'))

        if message == "RST":
            client.close()
            break


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()