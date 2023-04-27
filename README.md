# Trabalho GA - Redes

This project consist in creating a router simulator. The machine sends movie ideas to router, and with routing information, it will send to the right client.

## Components

### Machine

The machine is responsible for connecting to the router and sending data packets every 1 second. The information inside the packet is generated randomly
```JSON
{
  origin // picked randomly between the 4 clients
  message // picked randomly between a list of movies
  ttl // number between 1 and 5 that represents the time to live of the packet
}
```

### Router

The router is responsible for receiving the connections from the machine and the 4 clients.
The router receives the routing packets from the clients and with those informations, it builds the routing table.
Example:
```
************************************
*   ORIGIN   *   DESTIN.  * METRIC *
* 10.10.10.1 * 20.20.20.1 *    1   *
* 20.20.20.1 * 40.40.40.1 *    2   *
* 30.30.30.1 * 10.10.10.1 *    3   *
* 40.40.40.1 * 30.30.30.1 *    2   *
************************************
```

The router can also receive data packets from the machine.
The packets are stored in a queue that has size of 5.
If the queue is full, the packet will be discarded. If not, the packet is added to the end of the queue.

To send the data packet to a client, we have a method called `hadnle_send`.
This method is responsible for picking the first packet of the queue and sending it to its destination.
Here are the steps (validations) used to send the packet to its destination:
1. With the origin, we check the routing table to see the corresponding destination.
  1. If a destination is not found, then the packet will be discarded.
2. With the destination, we can get the client connected, so that we can send the packet to it
  1. If the client is not connected, the packet will be discarded.
3. Then we check the TTL (time to live) and the metric.
  1. If the TTL is smaller than the metric, that means that the time the packet has to live is lower than the time it needs to wait at the router before sending to the client. In that case, the packet is discarded.
4. If passing all the validations above, the packet can successfully be sent to its destination.


The router is also the main component of the project, which means that when we interrupt the code by typing `ctrl+c`, the router stops and so the machine and clients.
When the router stops, we receive a summary containing useful informations about what happened, like:
- Total of packets
- Total of routing packets
- Total of data packets
  - Successfully sent packets
  - Packets Lost
    - Not found in the routing table
    - TTL lower than the metric
    - Queue was full
    - Client not connected


### Client 1/2/3/4
The clients are responsible for connecting to the router and sending routing packets to it.
The routing packet has important information that will be used by the router to build a routing table.
```
{
  output_interface // is the IP of the client that sent the packet
  destination // picked randomly between the other 3 clients
  metric // the metric used to handle the data packets later
}
```
The metric used for this project is the amount of seconds that the router needs to hold the data packet after sending it to the destination.
Also, the client can receive data packets from the router. In this case, they receive the data and print the origin and the message itself.

