# api/supernode_api.py

import threading
from flask import Flask, jsonify, request
from super_node import follower_queue, follower_rewards, ban_count, all_nodes, penalize_follower, send_node_list_to_validator, Node

API_ADDRESS = '127.0.0.1'
API_PORT = 5777

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

