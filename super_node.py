import json
import socket
import time

BAN_THRESHOLD = 10
PING_INTERVAL = 5
DATA_INTERVAL = 2
REWARD = 10
VERSION = "1.0"
PENALTY_AMOUNT = 5
MAX_SPAM_PING = 10
sequence_counter = 0

ban_count = {}
spam_count = {}
follower_queue = []
follower_rewards = {}
follower_intervals = {}

all_nodes = []

class Node:
    def __init__(self, addr, is_validator=False):
        self.addr = addr
        self.is_validator = is_validator

def handle_client(client_socket, addr):
    global ban_count, follower_rewards, all_nodes, sequence_counter, follower_intervals

    while True:
        data = client_socket.recv(1024).decode()

        if client_socket != follower_intervals[sequence_counter]:
            spam_count[addr] += 1 
            if spam_count[addr] == MAX_SPAM_PING:
                break

        if not data:
            follower_rewards[formatted_addr] -= PENALTY_AMOUNT
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
    global follower_queue, sequence_counter
    while True:
        if follower_queue:
            for follower in list(follower_queue):  # Create a copy of the list to avoid modification during iteration
                time.sleep(DATA_INTERVAL)
                if follower in follower_queue:
                    try:
                        sequence_counter += 1
                        follower_intervals[sequence_counter] = follower
                        follower.send(b"SEND_DATA")
                    except:
                        print(f"{follower_queue}")

def penalize_follower(address):
    formatted_addr = f'{address[0]}:{address[1]}'
    if formatted_addr in follower_rewards:
        follower_rewards[formatted_addr] -= PENALTY_AMOUNT
