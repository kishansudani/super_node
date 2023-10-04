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

raft_members_rewards = {}
raft_members_intervals = {}
next_connection_time = {}

reward_collection = new_client('rewards')
raft_members_intervals_collection = new_client('intervals')

class RaftNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.term = 0
        self.voted_for = None
        self.leader_id = None
        self.raft_members = set()  # Set of raft_members nodes
        self.election_timeout = self.generate_random_timeout()
        self.heartbeat_interval = 5  # seconds
        self.last_heartbeat_time = time.time()
        self.is_leader = False
        self.votes_sent_in_current_term = set()
        self.votes_received_in_current_term = set()
        self.last_ping_time = time.time()



    def generate_random_timeout(self):
        # Generate a random election timeout between 150 and 300 milliseconds
        return random.uniform(0.15, 0.3)

    def start_election(self):
        self.term += 1
        self.voted_for = self.node_id
        self.reset_election_timeout()
        votes_received = set()

        for raft_members in self.raft_members:
            vote_granted = self.send_request_vote_request(raft_members)
            if vote_granted:
                votes_received.add(raft_members)

        if len(votes_received) >= len(self.raft_members) // 2:
            # Received majority of votes, become leader
            self.become_leader()
        else:
            # Did not receive majority of votes, reset election process
            self.reset_election()

    def send_request_vote_request(self, raft_members):
        # Implement sending request for vote to a raft_members
        # Return True if the vote is granted, False otherwise
        try:
            raft_members_address = (raft_members.ip, raft_members.port)

            if raft_members_address in self.votes_sent_in_current_term:
                print(f"Vote request already sent to {raft_members_address} in the current term.")
                return False


            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(raft_members_address)
                request_vote_message = f"REQUEST_VOTE|{self.term}|{self.node_id}"
                sock.send(request_vote_message.encode())
                response = sock.recv(1024).decode()
                sock.close()

                self.votes_sent_in_current_term.add(raft_members_address)
                if raft_members_address not in self.votes_received_in_current_term:
                    self.votes_received_in_current_term.add(raft_members_address)
                    return True
                else:
                    print(f"Already received a vote from {raft_members_address} in the current term.")
                    return False

        except Exception as e:
            print(f"Error sending request vote to {raft_members_address}: {e}")
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
        # Implement sending heartbeat to raft_members
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

            if term in self.votes_received_in_current_term:
                return "VOTE_DENIED"
            else:
                self.votes_received_in_current_term.add(term)
                return "VOTE_GRANTED"
        else:
            return "VOTE_DENIED"  



    def handle_client(self, client_socket, addr):
        global raft_members_rewards, raft_members_intervals, next_connection_time
        while True:
            data = client_socket.recv(1024).decode()

            if data.startswith("REQUEST_VOTE"):
                _, term, candidate_id = data.split('|')
                response = self.handle_request_vote(int(term), candidate_id)

                # Send the response back to the super node
                client_socket.send(response.encode())
                break


    def ping_nodes(self):
        # Check for inactive nodes and handle Raft consensus
        # Implement Raft consensus logic here using RaftNode class
        while True:
            time.sleep(PING_INTERVAL)

            # Check for inactive Raft members and handle Raft consensus
            for member in self.raft_members:
                try:
                    response = self.send_ping_request(member)
                    if response == "PONG":
                        # Raft member responded, update last ping time
                        self.last_ping_time = time.time()
                    else:
                        # Raft member has not responded, check if it was the leader
                        if self.is_raft_leader(member):
                            print(f"Node {member} is the leader. No need to initiate a new election.")
                        else:
                            print(f"Node {member} not responding. Initiating election.")
                            self.start_election()
                except Exception as e:
                    print(f"Error pinging Raft member {member}: {e}")
    
    def has_responded(self, member):
        # Implement logic to check if the Raft member has responded recently
        # Return True if the member has responded, False otherwise
        pass
    
    def is_raft_leader(self, member):
        # Implement logic to check if the Raft member is the leader
        # You may need to query the leader information from your Raft protocol
        # Return True if the member is the leader, False otherwise
        try:
            member_address = (member.ip, member.port)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(member_address)
                ping_message = "PING"  # Assume PING is a heartbeat message
                sock.send(ping_message.encode())
                response = sock.recv(1024).decode()

                # Assuming the response includes information about the current leader
                # Modify this based on the actual structure of your heartbeat messages
                _, _, _, is_leader_str = response.split('|')
                
                return is_leader_str.lower() == "true"  # Convert the string to a boolean
        except Exception as e:
            print(f"Error checking if {member_address} is the leader: {e}")
            return False
    
    def send_ping_request(self, member):
        try:
            member_address = (member.ip, member.port)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(member_address)
                ping_message = "PING"
                sock.send(ping_message.encode())
                response = sock.recv(1024).decode()
                return response
        except Exception as e:
            print(f"Error sending ping to Raft member {member_address}: {e}")
            return "ERROR"


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


def main():
    node_id = "Node1"  
    raft_node = RaftNode(node_id)

    raft_thread = threading.Thread(target=raft_node_worker, args=(raft_node,))
    raft_thread.start()

    ping_thread = threading.Thread(target=raft_node.ping_nodes)
    ping_thread.start()

    # ... (rest of the existing code)

if __name__ == "__main__":
    main()
