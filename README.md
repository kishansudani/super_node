## WARNING:


- I don't know what I'm building also but I'm trying to create something and trying to learn python also.

- What I've build so far?

- I've build cluster where there is:
    - One super Node
    - Validator Node
    - Follower Node

- `Ping`:
    - Follower node pings to the super node with `version|data|node_address`.
    - Super node will send ping message to follower node in array line by line at perticular interval if node does not send proper response super node will penalize the follower node.

- `Reward`:
    - Super node will receive the ping and list this address into dict and reward him.

- `Versioning`:
    - If version of follower and supernode does not matches than it will disconnect the follower node.

- `Banning system`:
    - Super node pings follower node at perticular time interval, if it doesn't respond then it will increase ban count.
    - If ban count reaches the ban thresold for perticular node, super node will disconnect the follower node.

- `Reward claiming api`:
    - if follower node try to claim more reward than it;s currently has then it will penalize that follower node

- `List of API`:
    - `Super Node API`:
        - `get_follower_queue | Get list of followers` 
        - `node_info | get list of node with ip and port`
        - `get_rewards | get follower address and reward`


### To Do:
- Store everything into DB
- Check ping response from follower node that it's his turn to ping the super node or not, if not increase ban count.
- Add validator node structor
    - when user send data it forwards to the super node, super node will send data to validator node in sequnace/
    - validator will sign the data and store it DB
    - Validator then send this signed data to the other validators and follower node
    - Other validator will verify this data and store it
    - Follower node will store the data
    - Create API for fetching stored data
    - Create api for sending data to follower node and validator node
    - Create Bootstrap node for new node(validator and follower)
- Use GRPC to communicate between two node