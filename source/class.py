import socket
import threading
import uuid  # For MAC address retrieval
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

if input("Debugging (Y/N): ").upper() == 'Y':
    DEBUG = True
else:
    DEBUG = False


class Common():
    def __init__(self):
        self.private_key
        self.public_key # public key that we will revice from other party
        self.public_pem
        self.role = None # to know if bug = false or client = true

    # RSA key generation and public key encoding
    def key_generation(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Encode server's public key in PEM format to share with the client
        self.public_pem = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def encryption(self, message, public_key):
        message = message.encode('ascii') # assuming we're reciving plaintext including from legacy
        encrypted_message = public_key.encrypt(
                message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        return encrypted_message
    
    def decryption(self, message, private_key):
        decrypted_message = private_key.decrypt(
                message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode('ascii')
        return decrypted_message
        

class Bug(Common):
    pass

class Client(Common):
    pass