import os
from configparser import ConfigParser

from lib.prototype import Client

config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
config = ConfigParser()
config.read(config_file)

# Initialize Client instance with manual IP and port
STATIC_IP = config["Client"]["network_interface_1"]
BUG_IP = config["Default"]["host"]  # SERVER_HOST = input("Enter the server IP address: ")
BUG_PORT = int(config["Client"]["port"])  # SERVER_PORT = int(input("Enter the server port number: ") or 12345)


def main():
    client_instance = Client(STATIC_IP, BUG_IP, BUG_PORT)
    client_instance.connect_to_server()

    while True:
        client_instance.communicate_with_server()


if __name__ == "__main__":
    main()
