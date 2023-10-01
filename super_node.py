import json
import socket
import threading
import time
from flask import Flask, jsonify, request
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

BAN_THRESHOLD = 10
PING_INTERVAL = 5
DATA_INTERVAL = 2
REWARD = 10
VERSION = "1.0"
PENALTY_AMOUNT = 5

ban_count = {}
follower_queue = []
follower_rewards = {}

all_nodes = []

class Node:
    def __init__(self, addr, is_validator=False):
        self.addr = addr
        self.is_validator = is_validator

def handle_client(client_socket, addr):
    global ban_count, follower_rewards, all_nodes

    while True:
        data = client_socket.recv(1024).decode()

        if not data:
            break

        # Reset ban count for the node
        ban_count[addr] = 0

        received_version, _, address = data.split('|')
        formatted_addr = f'{addr[0]}:{address}'  # Format the address


        if received_version != VERSION:
            print(f"Follower version {received_version} does not match main node version {VERSION}. Disconnecting.")
            break

        if formatted_addr in follower_rewards:
            follower_rewards[formatted_addr] += REWARD
        else:
            follower_rewards[formatted_addr] = REWARD

    print(f"Connection from {addr} closed")
    client_socket.close()

    if client_socket in follower_queue:
        follower_queue.remove(client_socket)

    if addr in ban_count:
        del ban_count[addr]

def send_node_list_to_validator(new_validator_addr):
    node_list = {
        'all_nodes': [f'{node.addr}' for node in all_nodes]
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect(new_validator_addr)
            client_socket.sendall(json.dumps(node_list).encode('utf-8'))
            print(f"Sent node list to the new validator {new_validator_addr}")
        except Exception as e:
            print(f"Error sending node list to the new validator: {e}")


def validate_and_store_data(data):
    # Add logic here to validate and store data from validator nodes
    print(f"Validating and storing data: {data}")
    # to share the data
    '''
    if any(node.addr == formatted_addr and node.is_validator for node in all_nodes):
            validate_and_store_data(data)
    '''

def send_data_to_validator_node(data, validator_node_addr):
    data_json = {
        "key": "some_key",
        "value": "some_value",
        "timestamp": "2023-10-01T12:34:56"
    }

    # Serialize the data to JSON
    data_str = json.dumps(data_json)

    # Connect to the validator node and send the data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(validator_node_addr)
        client_socket.sendall(data_str.encode('utf-8'))

def ping_nodes():
    global ban_count, follower_rewards

    while True:
        time.sleep(PING_INTERVAL)

        # Check for inactive nodes
        for addr in list(ban_count.keys()):
            if addr in follower_queue:
                ban_count[addr] += 1

                if ban_count[addr] >= BAN_THRESHOLD:
                    print(f"Node {addr} exceeded ban threshold. Disconnecting.")
                    follower_queue.remove(addr)
                    del ban_count[addr]

def instruct_follower():
    global follower_queue

    while True:
        if follower_queue:
            for follower in list(follower_queue):  # Create a copy of the list to avoid modification during iteration
                time.sleep(DATA_INTERVAL)
                if follower in follower_queue:
                    try:
                        follower.send(b"SEND_DATA")
                    except:
                        print(f"{follower_queue}")

def penalize_follower(address):
    formatted_addr = f'{address[0]}:{address[1]}'
    if formatted_addr in follower_rewards:
        follower_rewards[formatted_addr] -= PENALTY_AMOUNT

app = Flask(__name__)

@app.route('/get_follower_queue', methods=['GET'])
def get_follower_queue():
    return jsonify({'follower_queue': [str(addr) for addr in follower_queue]})

@app.route('/node_info', methods=['GET'])
def get_node():
    node_list = [f'{addr[0]}:{addr[1]}' for addr in [sock.getpeername() for sock in follower_queue]]
    return jsonify({'node_info': node_list})

@app.route('/get_rewards', methods=['GET'])
def get_rewards():
    return jsonify({'rewards': follower_rewards})

@app.route('/claim', methods=['POST'])
def claim_rewards():
    data = request.get_json()

    if 'amount' not in data:
        return jsonify({'error': 'No amount defined'}), 400
    
    if 'address' not in data:
        return jsonify({'error': 'No address defined'}), 400

    ip = request.remote_addr
    amount = data['amount']
    address = data['address']

    formatted_addr = f'{ip}:{address}'

    if formatted_addr in follower_rewards and follower_rewards[formatted_addr] >= amount:
        follower_rewards[formatted_addr] -= amount
        return jsonify({'success': f'Claimed {amount} rewards successfully'}), 200
    else:
        # Penalize the follower node for invalid claims
        penalize_follower(formatted_addr)
        return jsonify({'error': 'Invalid claim or insufficient rewards'}), 400


@app.route('/add_node', methods=['POST'])
def add_node():
    data = request.get_json()

    if 'address' not in data:
        return jsonify({'error': 'No address defined'}), 400
    
    if 'ip' not in data:
        return jsonify({'error': 'No IP defined'}), 400
    
    if 'is_validator' not in data:
        return jsonify({'error': 'No permission defined'}), 400
    
    if 'port' not in data:
        return jsonify({'error': 'No permission defined'}), 400

    
    ip = data['ip']
    address = data['address']
    is_validator = data['is_validator']
    port = data['port']

    formatted_addr = f'{ip}:{address}'

    # Check if the node is already in the system
    if any(node.addr == formatted_addr for node in all_nodes):
        return jsonify({'error': 'Node already exists'}), 400

    # Create a new Node instance
    new_node = Node(formatted_addr, is_validator)

    # Add the new node to the list of all nodes
    all_nodes.append(new_node)

    if is_validator:
        threading.Thread(target=send_node_list_to_validator, args=(f'{ip}:{port}',)).start()



    return jsonify({'success': 'Node added successfully'}), 200


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5555))
    server.listen(5)

    print("Main Node listening on port 5555")

    threading.Thread(target=ping_nodes).start()
    threading.Thread(target=instruct_follower).start()

    threading.Thread(target=app.run, kwargs={'host':'127.0.0.1', 'port':5557}).start()

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr} established")

        # Initialize ban count for the node
        ban_count[addr] = 0

        # Add client socket to the follower queue
        follower_queue.append(client_socket)

        # Start a new thread to handle the client
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    main()
