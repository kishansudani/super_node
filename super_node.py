import socket
import time

import pymongo

from database.client import new_client
from datetime import datetime, timedelta

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
next_connection_time = {}

reward_collection = new_client('rewards')
follower_intervals_collection = new_client('intervals')


def handle_client(client_socket, addr):
    global ban_count, follower_rewards, sequence_counter, follower_intervals, next_connection_time
    isBanned = False

    if addr in next_connection_time:
        current_time = datetime.now()
        if current_time < next_connection_time[addr]:
            isBanned = True
            client_socket.send(b"You are banned wait for cooldown")
        else:
            del next_connection_time[addr]
    
    while not isBanned:
        data = client_socket.recv(1024).decode()

        if client_socket != follower_intervals[sequence_counter]:
            if addr in spam_count.keys():
                spam_count[addr] += 1 
            else:
                spam_count[addr] = 1 

            if spam_count[addr] == MAX_SPAM_PING:
                del spam_count[addr]
                current_time = datetime.now()
                unban_time = current_time + timedelta(minutes=10)
                next_connection_time[addr] = unban_time
                break

            continue

        if not data:
            try:
                follower_rewards[formatted_addr] -= PENALTY_AMOUNT
                reward_collection.update_one({"node": formatted_addr},{"$inc": {"amount": PENALTY_AMOUNT * -1}})
                break
            except:
                break

        try:
            received_version, _, address = data.split('|')
        except:
            print('Wrong Data')
            break

        if received_version != VERSION:
            print(f"Follower version {received_version} does not match main node version {VERSION}. Disconnecting.")
            break

        formatted_addr = f'{addr[0]}:{address}'  # Format the address

        if formatted_addr in follower_rewards:
            follower_rewards[formatted_addr] += REWARD
        else:
            follower_rewards[formatted_addr] = REWARD
        
        isExist = reward_collection.count_documents({"node": formatted_addr})
        if isExist:
            reward_collection.update_one({"node": formatted_addr},{"$inc": {"amount": 10}})
        else:
            reward_collection.insert_one({"node": formatted_addr, "amount": 10})

        # Reset ban count for the node
        ban_count[addr] = 0

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

def set_sequence_counter():
    global sequence_counter
    try:
        last_document = follower_intervals_collection.find_one(sort=[('_id', pymongo.DESCENDING)])
        last_key = list(last_document.keys())[1] if last_document else None
        if last_key is None:
            sequence_counter = 0
        else:
            sequence_counter = int(last_key)
    except Exception as e:
        print(e)

def instruct_follower():
    global follower_queue, sequence_counter
    set_sequence_counter()
    while True:
        if follower_queue:
            for follower in list(follower_queue):  # Create a copy of the list to avoid modification during iteration
                time.sleep(DATA_INTERVAL)
                if follower in follower_queue:
                    try:
                        sequence_counter += 1
                        follower_intervals[sequence_counter] = follower
                        follower_intervals_collection.insert_one({str(sequence_counter): f"{follower.getpeername()[0]}:{follower.getpeername()[1]}"})
                        follower.send(b"SEND_DATA")
                    except socket.error as e:
                        if e.errno == 107:
                            print(f"Disconnecting Follower node from super node: {follower.getpeername()[0]}:{follower.getpeername()[1]}")
                            follower.close() 
                            follower_queue.remove(follower) 

                    except Exception as e:
                        print(f"{e}")

def penalize_follower(address):
    formatted_addr = f'{address[0]}:{address[1]}'
    if formatted_addr in follower_rewards:
        follower_rewards[formatted_addr] -= PENALTY_AMOUNT
