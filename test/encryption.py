from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def save_key_to_file(key, filename, is_private=True):
    if is_private:
        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    else:
        pem = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    with open(filename, 'wb') as f:
        f.write(pem)

def load_key_from_file(filename, is_private=True):
    with open(filename, 'rb') as f:
        pem_data = f.read()

    if is_private:
        key = serialization.load_pem_private_key(
            pem_data,
            password=None,
            backend=default_backend()
        )
    else:
        key = serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )

    return key

# Generate and save key pair
private_key, public_key = generate_key_pair()
save_key_to_file(private_key, 'private_key.pem')
save_key_to_file(public_key, 'public_key.pem', is_private=False)

# Load keys from files
loaded_private_key = load_key_from_file('private_key.pem')
loaded_public_key = load_key_from_file('public_key.pem', is_private=False)

# Example usage: Encryption and Decryption
message_to_encrypt = "Hello, this is a secret message!"

# Encryption
ciphertext = loaded_public_key.encrypt(
    message_to_encrypt.encode('utf-8'),
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Fix here
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Decryption
decrypted_message = loaded_private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Fix here
        algorithm=hashes.SHA256(),
        label=None
    )
).decode('utf-8')

# Display results
print("Original Message:", message_to_encrypt)
print("Encrypted Message:", ciphertext)
print("Decrypted Message:", decrypted_message)
