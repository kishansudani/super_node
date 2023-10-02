### System Overview
- I've built a basic distributed system with a super node, a validator node, and follower nodes. The system involves communication between these nodes, handling rewards, versioning, banning, and more.

- Here's a brief overview of what I've built:

## Super Node:

- Manages the network and handles communication with follower nodes.
- Keeps track of follower nodes and their rewards.
- Enforces version compatibility.
- Implements banning for unresponsive nodes.
- Sends ping messages to follower nodes.
- Provides APIs for getting follower information and rewards.

## Follower Node:

- Connects to the super node.
- Sends ping messages with version, data, and node address.
- Can claim rewards from the super node.
- Implements version checking and validation.
- Has an API for claiming rewards.


- `Banning System`: The super node monitors follower nodes and bans them if they fail to respond after a certain number of pings.

- `Reward System`: Followers receive rewards for responding to pings. They can also claim rewards through an API.

- `Versioning`: The super node ensures that follower nodes have the correct version. If not, it disconnects them.

- `Ping System`: The super node pings follower nodes at regular intervals. If a follower node fails to respond, it's penalized.

- `APIs`: There are APIs defined for getting follower information, node details, and rewards.