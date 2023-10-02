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
