import os
from configparser import ConfigParser

from lib.prototype import Client

config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
config = ConfigParser()
config.read(config_file)

# Initialize Client instance with manual IP and port
if input("Do you want to use the configuration file: ").upper() == "Y":
    STATIC_IP = config["Client"]["network_interface_1"]
    BUG_IP = config["Bug"]["network_interface_1"]  # SERVER_HOST = input("Enter the server IP address: ")
    BUG_PORT = int(config["Client"]["port"])  # SERVER_PORT = int(input("Enter the server port number: ") or 12345)

else:
    STATIC_IP = input("Enter the IP address you want to assign to the client: ")
    BUG_IP = input("Enter the IP address of the bug network interface: ")
    BUG_PORT = int(input("Enter the port number that you want to connect onto the bug: "))


def main():
    client_instance = Client(STATIC_IP, BUG_IP, BUG_PORT)
    client_instance.connect_to_server()

    while True:
        client_instance.communicate_with_server()


if __name__ == "__main__":
    main()
