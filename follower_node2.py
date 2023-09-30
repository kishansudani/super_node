import socket
import time

def send_data(version):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))

    while True:
        data = client.recv(1024).decode()

        if data == "SEND_DATA":
            # Send data to main node
            data_to_send = f"{version}|2"  # Replace with your data
            client.send(data_to_send.encode())
            print(f"Sent data to main node: {data_to_send}")

if __name__ == "__main__":
    follower_version = "1.0"
    send_data(follower_version)
