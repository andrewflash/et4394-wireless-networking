# Possible Scenario
Here is a list of possible scenario for project 1 - Wi-Fi in NS3 
(performance vs number of stations):

1. Equal bandwidth and distance (circular ring)
  * Create x nodes as client with the same distance to AP; This can be done by using circular topology
  * Create 1 nodes as server placed directly below AP
  * Allocate equal bandwith to every nodes
  * Broadcast message from the server to clients (running same app)
  * Increase or decrease the nodes and measure the performance metrics:
    * Error rate model
    * Interference due to other nodes
    * Flow monitor
    * Delay
    * Response time
    * Throughput (bytes/sec)
2. Measuring signal strength and quality of the Wi-Fi due to presence of buildings
  * Create at least two Wi-Fi nodes, one is not blocked by building, another one is blocked
  * Measure the transmitted power of the access point and the received power from both nodes
  * Measure error rates or other quality metrics
3. Only change the number of nodes
  * Measure flow monitor
  * Delay
  * Error rate
