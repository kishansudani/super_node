# api/supernode_api.py

import json
import threading
from flask import Flask, jsonify, request
from super_node import follower_queue, follower_rewards, ban_count, penalize_follower, follower_intervals

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

@app.route('/get_follower_intervals', methods=['GET'])
def get_sequence_counter():
    data = []
    for key, val in follower_intervals.items():
        data.append({key: f'{val.getpeername()[0]}:{val.getpeername()[1]}'})
    return jsonify({'value': data})

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

