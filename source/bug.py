from classes import Bug

# Initialize Bug instance with manual IP and ports
HOST = input("Enter the application IP address (default is localhost): ")
BUG_PORT = int(input("Enter the port for bug.py to listen for clients (default is 12345): ") or 12345)
LEGACY_PORT = int(input("Enter the port for legacy_application.py to connect (default is 23456): ") or 23456)

bug_instance = Bug(HOST, BUG_PORT, LEGACY_PORT)
bug_instance.run()
