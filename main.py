import socket
import threading

from super_node import handle_client, instruct_follower, ping_nodes, ban_count, follower_queue, reward_collection, follower_rewards, sequence_counter, follower_intervals_collection
from api.supernode_api import app

API_ADDRESS = '127.0.0.1'
API_PORT = 5777

SERVER_SOCKET_IP = '127.0.0.1'
SERVER_SOCKET_PORT =  5555

connection_ports = [5070, 5071]

def set_follower_rewards_dict():
    global follower_rewards
    try:
        if reward_collection.count_documents({}) != 0:
            cursor = reward_collection.find({})
            for _ in cursor:
                node = _['node']
                amount = _['amount']
                follower_rewards[node] = amount
        else:
            follower_rewards = {}
    except Exception as e:
        print(e)



def main():
    set_follower_rewards_dict()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_SOCKET_IP, SERVER_SOCKET_PORT))
    server.listen(5)

    print(f"Super Node listening on port {SERVER_SOCKET_PORT}")

    threading.Thread(target=ping_nodes).start()
    threading.Thread(target=instruct_follower).start()

    threading.Thread(target=app.run, kwargs={'host':API_ADDRESS, 'port':API_PORT}).start()

    while True:
        try:
            client_socket, addr = server.accept()
            if addr[1] not in connection_ports:
                print(f'{addr[0]} is trying to connect from {addr[1]}')
                client_socket.send(b'PORT ERROR')
                client_socket.close()
            else:
                print(f"Connection from {addr} established")

                # Initialize ban count for the node
                ban_count[addr] = 0

                # Add client socket to the follower queue
                follower_queue.append(client_socket)

                # Start a new thread to handle the client
                threading.Thread(target=handle_client, args=(client_socket, addr)).start()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()