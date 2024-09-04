import socket
import threading

DEBUG = True

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

        if DEBUG == True: print(f"Debug message recieved: {message}")

        if message == "data":
            client.send("Aadya, Anusha, Kavish, Sia, Suresh, Tatsam".encode("ascii"))

        elif message == "SIH":
            client.send("Problem Statement Number: 2727".encode("ascii"))

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