import hashlib
import hmac
import secrets


def sign_data(data, secret_key):
    # Convert the secret key to bytes
    secret_key_bytes = bytes(secret_key, 'utf-8')

    # Convert the data to bytes
    data_bytes = bytes(data, 'utf-8')

    # Use HMAC-SHA256 for the signature
    signature = hmac.new(secret_key_bytes, msg=data_bytes, digestmod=hashlib.sha256).hexdigest()

    return signature


def generate_64_characters():
    # Generate a random 32-byte string
    random_bytes = secrets.token_bytes(32)

    # Convert the bytes to a hexadecimal string
    hex_string = secrets.token_hex(32)

    return hex_string

def create_unique_address(data):
    # Convert the data to bytes
    data_bytes = bytes(data, 'utf-8')

    # Use SHA-256 hash function
    hash_object = hashlib.sha256(data_bytes)

    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()

    # Take the first 32 characters for the address
    address = hash_hex[:40]

    return address

# Example usage
# secret_key = generate_64_characters()
secret_key = '8075d41b1fe853fa44a23ae331fa2b0333cc934779ba888829ad04111e792c1b'
print(f"New 64 characters: {secret_key}")


# Example usage
data_to_sign = "Hello, World!"

unique_address = create_unique_address(secret_key)
print(f"Unique address: {unique_address}")

signature = sign_data(data_to_sign, secret_key)
print(f"Data: {data_to_sign}")
print(f"Signature: {signature}")
