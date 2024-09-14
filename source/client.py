from classes import Client

# Initialize Client instance with manual IP and port
SERVER_HOST = input("Enter the server IP address: ")
SERVER_PORT = int(input("Enter the server port number (default is 12345): ") or 12345)


def main():
    client_instance = Client(SERVER_HOST, SERVER_PORT)
    client_instance.connect_to_server()

    while True:
        client_instance.communicate_with_server()


if __name__ == "__main__":
    main()
