import os
import sys
from configparser import ConfigParser

from lib.prototype import Bug

config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
config = ConfigParser()
config.read(config_file)

# Initialize Bug instance with manual IP and ports
if input("Do you want to use the configuration file: ").upper() == "Y":
    NETWORK_INTERFACE_1 = config["Bug"]["network_interface_1"]
    LEGACY_APPLICATION_IP = config["Legacy_Application"]["network_interface_1"]
    CLIENT_PORT = int(config["Client"]["port"])
    LEGACY_APPLICATION_PORT = int(config["Legacy_Application"]["port"])

else:
    NETWORK_INTERFACE_1 = input("Enter the IP address you want to assign to the bug: ")
    LEGACY_APPLICATION_IP = input("Enter the IP address of the server: ")
    CLIENT_PORT = int(input("Enter the port number to listen on for clients: "))
    LEGACY_APPLICATION_PORT = int(input("Enter the port number to connect onto the server: "))

bug_instance = Bug(NETWORK_INTERFACE_1, LEGACY_APPLICATION_IP, CLIENT_PORT, LEGACY_APPLICATION_PORT)
try:
    bug_instance.run()
except KeyboardInterrupt:
    print("Bug server shutting down...")
    bug_instance.bug_server.close()
    sys.exit()
