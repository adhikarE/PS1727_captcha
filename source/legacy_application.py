import socket
import threading

debug_opt = input("Debugging (Y/N): ")
debug_opt = debug_opt.upper()

if debug_opt == 'Y':

    DEBUG = True

else:
    
    DEBUG = False

HOST = '127.0.0.1'
PORT = int(input("Enter the port: "))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

client_list = []

DATA = ["Aadya, Anusha, Kavish, Sia, Suresh, Tatsam", "Problem Statement Number: 1727"]
ERROR = "Couldn't process!"

def serve():
    client, address = server.accept()
    client_list.append(client)
    print(f"{client} Connected to the application")

    while True:

        message = client.recv(1024).decode("ascii")

        if DEBUG == True:
            print("\n" + "="*50)
            print(f"Received PT response: \n{message}")
            print("="*50)

        if message == "data":
            client.send(DATA[0].encode("ascii"))
            
            if DEBUG == True:
                print("\n" + "="*50)
                print(f"Transmitted PT data: \n{DATA[0]}")
                print("="*50)
                

        elif message == "SIH":
            client.send(DATA[1].encode("ascii"))

            if DEBUG == True:
                print("\n" + "="*50)
                print(f"Transmitted PT data: \n{DATA[1]}")
                print("="*50)
                

        elif message == "RST":
            client_list.remove(client)
            client.close()
            print(f"{client} disconnected!")
            break

        else:
            client.send(ERROR.encode("ascii"))

            if DEBUG == True:
                print("\n" + "="*50)
                print(f"Transmitted PT data: \n{ERROR}")
                print("="*50)
            
            continue


thread = threading.Thread(target=serve)
thread.start()