import socket
import threading

HOST = '127.0.0.1'
PORT = int(input("Enter the port: "))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

client_list = []


def serve():
    client, address = server.accept()
    client_list.append(client)
    print(f"{client} Connected to the application")

    while True:

        message = client.recv(1024).decode("ascii")

        if message == "data":
            client.send("Apple, Banana, Mango, Litchi, Kiwi".encode("ascii"))

        elif message == "RST":
            client_list.remove(client)
            client.close()
            print(f"{client} disconnected!")
            break

        else:
            client.send("Couldn't process!".encode("ascii"))
            continue


thread = threading.Thread(target=serve)
thread.start()