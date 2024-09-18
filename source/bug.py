import os
import sys
from configparser import ConfigParser

from lib.prototype import Bug

config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
config = ConfigParser()
config.read(config_file)

# Initialize Bug instance with manual IP and ports

# HOST = input("Enter the application IP address (default is localhost): ")
# BUG_PORT = int(input("Enter the port for bug.py to listen for clients (default is 12345): ") or 12345)
# LEGACY_PORT = int(input("Enter the port for legacy_application.py to connect (default is 23456): ") or 23456)

LEGACY_APPLICATION_IP = config["Legacy_Application"]["network_interface_1"]
CLIENT_PORT = int(config["Client"]["port"])
LEGACY_APPLICATION_PORT = int(config["Legacy_Application"]["port"])

bug_instance = Bug(LEGACY_APPLICATION_IP, CLIENT_PORT, LEGACY_APPLICATION_PORT)
try:
    bug_instance.run()
except KeyboardInterrupt:
    print("Bug server shutting down...")
    bug_instance.bug_server.close()
    sys.exit()
