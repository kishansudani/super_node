import socket
import threading
import time
from flask import Flask, jsonify

BAN_THRESHOLD = 10
PING_INTERVAL = 5
DATA_INTERVAL = 2

ban_count = {}
follower_queue = []

main_node_version = "1.0"

follower_rewards = {}

def handle_client(client_socket, addr):
    global ban_count, follower_rewards

    while True:
        data = client_socket.recv(1024).decode()

        if not data:
            break

        print(f"Received data from {addr}: {data}")

        # Reset ban count for the node
        ban_count[addr] = 0
        formatted_addr = f'{addr[0]}:{addr[1]}'  # Format the address

        received_version, received_data = data.split('|')
        if received_version != main_node_version:
            print(f"Follower version {received_version} does not match main node version {main_node_version}. Disconnecting.")
            break

        if formatted_addr in follower_rewards:
            follower_rewards[formatted_addr] += 10
        else:
            follower_rewards[formatted_addr] = 10


    print(f"Connection from {addr} closed")
    client_socket.close()

    if client_socket in follower_queue:
        follower_queue.remove(client_socket)

    if addr in ban_count:
        del ban_count[addr]

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

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5556))
    server.listen(5)

    print("Main Node listening on port 5556")

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
