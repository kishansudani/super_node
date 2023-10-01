import hashlib
import socket
import threading
import requests
from flask import Flask, jsonify
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


version = "1.0"
node_name = 'follower2'
sdata = '2'
api_host = '127.0.0.1'
api_port = 5559
SUPER_NODE_IP = '127.0.0.1'
SUPER_NODE_PORT = 5555
SUPER_NODE_API_PORT = 5557
super_node_url_claim_url = f"http://{SUPER_NODE_IP}:{SUPER_NODE_API_PORT}/claim"


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

def generate_40_char_address(data):
    data_bytes = bytes(data, 'utf-8')
    hash_object = hashlib.sha256(data_bytes)
    hash_hex = hash_object.hexdigest()
    address = hash_hex[:40]
    return '0x'+ address

def createNodeKey():
    key = load_key_from_file(f'../pem/{node_name}_public_key.pem', is_private=False)
    user_pub_key_str = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    user_address = generate_40_char_address(user_pub_key_str)

    return user_address

key = createNodeKey()

def send_data():
    global version
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client.connect((SUPER_NODE_IP, SUPER_NODE_PORT))
            break
        except Exception as e:
            print(f"Error connecting to the super node: {e}")

    while True:
        data = client.recv(1024).decode()
        if data == "SEND_DATA":
            # Send data to main node
            data_to_send = f"{version}|{sdata}|{key}"  # Replace with your data
            client.send(data_to_send.encode())
            print(f"Sent data to main node: {data_to_send}")

app = Flask(__name__)

def make_claim_request(amount):
    claim_request = {'amount': amount, 'address': key}
    try:
        response = requests.post(super_node_url_claim_url, json=claim_request)
        if response.status_code == 200:
            print(f"Claim successful. Response from super node: {response.json()}")
        else:
            print(f"Claim failed. Response from super node: {response.json()}")
    except Exception as e:
        print(f"Error making claim request: {e}")


@app.route('/claim', methods=['GET'])
def claim_rewards():
    amount = 10
    threading.Thread(target=make_claim_request, args=(amount,)).start()

    return jsonify({'success': 'Claim request sent'}), 200


def main():
    threading.Thread(target=send_data).start()
    threading.Thread(target=app.run, kwargs={'host':api_host, 'port':api_port}).start()

if __name__ == "__main__":
    main()