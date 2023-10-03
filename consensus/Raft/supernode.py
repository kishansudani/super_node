import random
import socket
import time
import threading
from database.client import new_client

BAN_THRESHOLD = 10
PING_INTERVAL = 5
DATA_INTERVAL = 2
REWARD = 10
VERSION = "1.0"
PENALTY_AMOUNT = 5
MAX_SPAM_PING = 10

follower_rewards = {}
follower_intervals = {}
next_connection_time = {}

reward_collection = new_client('rewards')
follower_intervals_collection = new_client('intervals')

class RaftNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.term = 0
        self.voted_for = None
        self.leader_id = None
        self.followers = set()  # Set of follower nodes
        self.election_timeout = self.generate_random_timeout()
        self.heartbeat_interval = 5  # seconds
        self.last_heartbeat_time = time.time()
        self.is_leader = False
        self.votes_sent_in_current_term = set()


    def generate_random_timeout(self):
        # Generate a random election timeout between 150 and 300 milliseconds
        return random.uniform(0.15, 0.3)

    def start_election(self):
        self.term += 1
        self.voted_for = self.node_id
        self.reset_election_timeout()
        votes_received = set()

        for follower in self.followers:
            vote_granted = self.send_request_vote_request(follower)
            if vote_granted:
                votes_received.add(follower)

        if len(votes_received) >= len(self.followers) // 2:
            # Received majority of votes, become leader
            self.become_leader()
        else:
            # Did not receive majority of votes, reset election process
            self.reset_election()

    def send_request_vote_request(self, follower):
        # Implement sending request for vote to a follower
        # Return True if the vote is granted, False otherwise
        try:
            follower_address = (follower.ip, follower.port)

            if follower_address in self.votes_sent_in_current_term:
                print(f"Vote request already sent to {follower_address} in the current term.")
                return False


            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(follower_address)
                request_vote_message = f"REQUEST_VOTE|{self.term}|{self.node_id}"
                sock.send(request_vote_message.encode())
                response = sock.recv(1024).decode()
                
                self.votes_sent_in_current_term.add(follower_address)
                if response == "VOTE_GRANTED":
                    # Mark that a vote request has been sent to this follower in the current term
                    return True
                else:
                    return False

        except Exception as e:
            print(f"Error sending request vote to {follower_address}: {e}")
            return False

    def reset_election_timeout(self):
        # Reset the election timeout when starting a new election
        self.election_timeout = self.generate_random_timeout()

    def become_leader(self):
        self.is_leader = True
        self.leader_id = self.node_id
        print(f"Node {self.node_id} became the leader for term {self.term}")

    def reset_election(self):
        self.voted_for = None
        self.is_leader = False
        print(f"Node {self.node_id} reset election for term {self.term}")


    def send_heartbeat(self):
        # Implement sending heartbeat to followers
        pass

    def handle_append_entries(self, leader_id, entries, leader_commit):
        # Implement handling append entries from the leader
        pass

    def handle_request_vote(self, term, candidate_id):
        # Logic to handle request for vote from a candidate
        if term < self.current_term:
            return "VOTE_DENIED"  # Candidate's term is outdated
        
        if self.voted_for is None or self.voted_for == candidate_id:
            # Vote for the candidate if not voted in this term or voted for the same candidate
            self.voted_for = candidate_id
            self.current_term = term
            return "VOTE_GRANTED"
        else:
            return "VOTE_DENIED"  # Already voted for another candidate in this term



def handle_client(client_socket, addr):
    global follower_rewards, follower_intervals, next_connection_time

    # ... (rest of the existing code)

def raft_node_worker(raft_node):
    
    while True:
        time.sleep(1)

        if not raft_node.is_leader:
            raft_node.election_timeout -= 0.1

            if raft_node.election_timeout <= 0:
                # Election timeout reached, start a new election
                raft_node.start_election()
                print(f"Heartbeat timeout. Initiating election for Node {raft_node.node_id}")

        else:
            raft_node.send_heartbeat()

def ping_nodes():
    global follower_rewards
    ban_count = {}

    while True:
        time.sleep(PING_INTERVAL)

        # Check for inactive nodes and handle Raft consensus
        # Implement Raft consensus logic here using RaftNode class

def main():
    node_id = "Node1"  
    raft_node = RaftNode(node_id)

    raft_thread = threading.Thread(target=raft_node_worker, args=(raft_node,))
    raft_thread.start()

    ping_thread = threading.Thread(target=ping_nodes)
    ping_thread.start()

    # ... (rest of the existing code)

if __name__ == "__main__":
    main()
