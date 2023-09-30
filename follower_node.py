import json
import socket
import threading
import time
from flask import Flask, jsonify, request
import requests

super_node_url = "http://127.0.0.1:5557/claim"
version = "1.0"
unique_address = '3c0995799f067215f44397ec0072cdca4fb9c200'
secret_key = '8075d41b1fe853fa44a23ae331fa2b0333cc934779ba888829ad04111e792c1b'

def send_data():
    global version
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client.connect(("127.0.0.1", 5555))
            break
        except Exception as e:
            print(f"Error connecting to the super node: {e}")

    while True:
        data = client.recv(1024).decode()

        if data == "SEND_DATA":
            # Send data to main node
            data_to_send = f"{version}|1|"  # Replace with your data
            client.send(data_to_send.encode())
            print(f"Sent data to main node: {data_to_send}")

app = Flask(__name__)

def make_claim_request(amount):
    claim_request = {'amount': amount}
    try:
        response = requests.post(super_node_url, json=claim_request)
        if response.status_code == 200:
            print(f"Claim successful. Response from super node: {response.json()}")
        else:
            print(f"Claim failed. Response from super node: {response.json()}")
    except Exception as e:
        print(f"Error making claim request: {e}")


@app.route('/claim', methods=['GET'])
def claim_rewards():
    # data = request.get_json()

    # if 'amount' not in data:
    #     return jsonify({'error': 'Invalid request'}), 400

    # amount = data['amount']

    amount = 10

    # Example of making a claim request to the super node through the Flask API
    threading.Thread(target=make_claim_request, args=(amount,)).start()

    return jsonify({'success': 'Claim request received'}), 200


def main():
    threading.Thread(target=send_data).start()
    threading.Thread(target=app.run, kwargs={'host':'127.0.0.1', 'port':5558}).start()

if __name__ == "__main__":
    main()