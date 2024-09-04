from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate RSA keys
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Save private key to file
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Save public key to filefrom cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,  # Common public exponent value
    key_size=2048  # Size of the key in bits
)

# Derive the public key from the private key
public_key = private_key.public_key()

# File paths to save the keys
PRIVATE_KEY_PATH = 'private_key.pem'  # Path for saving the private key
PUBLIC_KEY_PATH = 'public_key.pem'  # Path for saving the public key

# Save the private key to a PEM file
with open(PRIVATE_KEY_PATH, 'wb') as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,  # Encoding format for the private key
        format=serialization.PrivateFormat.PKCS8,  # Private key format
        encryption_algorithm=serialization.NoEncryption()  # No encryption for the private key file
    ))

# Save the public key to a PEM file
with open(PUBLIC_KEY_PATH, 'wb') as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,  # Encoding format for the public key
        format=serialization.PublicFormat.SubjectPublicKeyInfo  # Public key format
    ))

print(f"Private key saved to {PRIVATE_KEY_PATH}")
print(f"Public key saved to {PUBLIC_KEY_PATH}")

with open("public_key.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))
