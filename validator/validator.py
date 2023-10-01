import socket
import threading
import json
import plyvel

VALIDATOR_PORT = 6666
SUPER_NODE_ADDR = "127.0.0.1"
SUPER_NODE_PORT = 5555

all_nodes = []

class Node:
    def __init__(self, addr, is_validator=False):
        self.addr = addr
        self.is_validator = is_validator

# Initialize LevelDB
db = plyvel.DB('./validator_db', create_if_missing=True)

def handle_super_node_data(data):
    # Add validation logic here
    # If data is valid, store it in LevelDB and share it across nodes
    try:
        data_json = json.loads(data)
        key = data_json.get('key')
        value = data_json.get('value')


        if key is not None and value is not None:
            db.put(key.encode('utf-8'), value.encode('utf-8'))
            share_data_with_nodes(data)
            print(f"Data stored in LevelDB: {data_json}")

    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")


def handle_node_list_from_super_node(data):
    try:
        node_list = json.loads(data)
        validator_nodes.clear()
        normal_nodes.clear()

        for node_address in node_list.get('all_nodes', []):
            is_validator = ':' in node_address  # Assume that if there's a colon, it's a validator
            all_nodes.append(Node(node_address, is_validator))

        print(f"Received node list from super node: {', '.join(str(node.addr) for node in all_nodes)}")

        # Add logic to store this information in LevelDB
        store_node_list_in_leveldb(node_list)


    except json.JSONDecodeError as e:
        print(f"Invalid JSON format for node list: {e}")


def store_node_list_in_leveldb(node_list):
    try:
        # Open LevelDB for writing
        with plyvel.DB('./validator_db', create_if_missing=True) as db:
            # Iterate through the node list and store information in LevelDB
            for node_address in node_list.get('all_nodes', []):
                is_validator = ':' in node_address  # Assume that if there's a colon, it's a validator
                node_type = 'validator' if is_validator else 'normal'
                
                # Use the node address as the key and store node type as the value
                db.put(node_address.encode('utf-8'), node_type.encode('utf-8'))

        print("Node list stored in LevelDB")

    except Exception as e:
        print(f"Error storing node list in LevelDB: {e}")

def share_data_with_nodes(data):
    # Add logic to share data with other validator nodes and normal nodes
    # You can use sockets or any other communication method

    # Example: Broadcast the data to other validator nodes
    for validator_node_addr in validator_nodes:
        send_data_to_validator_node(data, validator_node_addr)

    # Example: Broadcast the data to normal nodes
    for normal_node_addr in normal_nodes:
        send_data_to_normal_node(data, normal_node_addr)

def send_data_to_validator_node(data, validator_node_addr):
    # Implement logic to send data to other validator nodes
    pass

def send_data_to_normal_node(data, normal_node_addr):
    # Implement logic to send data to normal nodes
    pass

def start_validator_node():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", VALIDATOR_PORT))
    server.listen(5)

    print("Validator Node listening on port", VALIDATOR_PORT)

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr} established")

        data = client_socket.recv(1024).decode()

        if addr == SUPER_NODE_ADDR and addr[1] == SUPER_NODE_PORT:
            handle_node_list_from_super_node(data)
        else:
            handle_super_node_data(data)


        client_socket.close()

# List of validator nodes and normal nodes
validator_nodes = [("127.0.0.1", 5557)]  # Add the addresses of other validator nodes
normal_nodes = [("127.0.0.1", 5558)]      # Add the addresses of normal nodes

if __name__ == "__main__":
    start_validator_node()
