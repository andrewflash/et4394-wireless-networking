# Possible Scenario
Here is a list of possible scenario for project 1 - Wi-Fi in NS3
(performance vs number of stations):

1. Equal bandwidth and distance (circular ring)
  * Create x nodes as client with the same distance to AP; This can be done by using circular topology
  * Create 1 nodes as server placed directly below AP
  * Allocate equal bandwith to every nodes
  * Broadcast message from the server to clients (running same app)
  * Increase or decrease the nodes and measure the performance metrics:
    * Throughput (bytes/sec)
2. Random placement of nodes
  * Create random placement of nodes by placing the nodes randomly within a disc
  * Measure throughput vs number of nodes
3. Dynamic nodes mobility
  * Create dynamic nodes using 2D random walk
  * Measure throughput vs number of nodes
4. DSSS data rate
  * Measure throughput with different types of DSSS data rate
5. The effect of payload to the throughput
  * Compare different size of payload and evaluate the throughput
6. Evaluate the advantage of RTS/CTS to the throughput
  * Measure the network throughput when RTS/CTS is enabled or disabled