import socket
from threading import Thread
import json
from time import sleep

router = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
router.bind(("localhost", 4000))
router.listen(4)

print("Server listening on localhost:4000")

IP_1 = "10.10.10.1"
IP_2 = "20.20.20.1"
IP_3 = "30.30.30.1"
IP_4 = "40.40.40.1"

clients = {IP_1: None, IP_2: None, IP_3: None, IP_4: None, "machine": None}

routing_table = {}

packets_information = {
    "client_not_connected": 0,
    "destination_not_found": 0,
    "lower_ttl": 0,
    "queue_full": 0,
    "packet_died": 0,
    "successfully_sent": 0,
    "routing": 0,
}

packet_queue = []


def print_routing_table():
    print("****************************************")
    print("*   ORIGIN   *   DESTIN.  *   METRIC   *")
    for origin, send_info in routing_table.items():
        print(f"* {origin} * {send_info['destination']} * {send_info['metricValue']} ")
    print("****************************************")


def connect_client(client_socket):
    if clients["machine"] == None:
        clients["machine"] = client_socket
        pass
    elif clients[IP_1] == None:
        clients[IP_1] = client_socket
        print("Client 1 is online!")
    elif clients[IP_2] == None:
        clients[IP_2] = client_socket
        print("Client 2 is online!")
    elif clients[IP_3] == None:
        clients[IP_3] = client_socket
        print("Client 3 is online!")
    elif clients[IP_4] == None:
        clients[IP_4] = client_socket
        print("Client 4 is online!")


def handle_send():
    print("Starting Send Thread! Queue Limit: 5")
    while True:
        if len(packet_queue) == 0:
            continue

        packet_to_send = packet_queue.pop(0)
        origin = packet_to_send["origin"]
        print(f"Receiving data packet from {origin}")
        print("Checking routing table...")
        print_routing_table()
        send_info = routing_table.get(origin)
        if send_info == None:
            print("Could not find destination, discarding packet")
            packets_information["destination_not_found"] += 1
        else:
            destination = send_info["destination"]
            metric = send_info["metricValue"]
            ttl = packet_to_send["ttl"]
            destination_socket = clients[destination]
            if destination_socket == None:
                print("Client not connected, discarding packet")
                packets_information["client_not_connected"] += 1
            elif ttl < metric:
                print(f"TTL: {ttl} / Metric: {metric}")
                print("Not enough time to wait for packet to send, discarding packet.")
                packets_information["lower_ttl"] += 1
            else:
                print(f"Waiting {metric} seconds before sending data packet...")
                sleep(metric)
                message = packet_to_send["message"]
                print(f"Sending '{message}' to {destination}")
                packets_information["successfully_sent"] += 1
                destination_socket.send(bytes(json.dumps(packet_to_send), "utf-8"))


def handle_client(client_socket, address):
    connect_client(client_socket)

    while True:
        packet = client_socket.recv(1024).decode("utf-8")
        packet_formatted = json.loads(packet)

        if "output_interface" in packet_formatted:
            origin = packet_formatted["output_interface"]
            destination = packet_formatted["destination"]
            metric = packet_formatted["metric"]
            print(
                f"Receiving routing packet from {origin}.\nUpdating routing table... ({origin} -> {destination})"
            )
            routing_table[origin] = {"destination": destination, "metricValue": metric}
            packets_information["routing"] += 1
        else:
            if len(packet_queue) != 0 and len(packet_queue) == 5:
                print("The queue is full, discarding packet.")
                packets_information["queue_full"] += 1
            else:
                packet_queue.append(packet_formatted)

        print("\n\n")


def print_summary():
    client_not_connected = packets_information["client_not_connected"]
    destination_not_found = packets_information["destination_not_found"]
    lower_ttl = packets_information["lower_ttl"]
    queue_full = packets_information["queue_full"]
    packet_died = packets_information["packet_died"]
    successfully_sent = packets_information["successfully_sent"]
    packets_lost = (
        client_not_connected
        + destination_not_found
        + lower_ttl
        + queue_full
        + packet_died
    )
    data_packets = successfully_sent + packets_lost
    routing_packets = packets_information["routing"]
    total_packets = data_packets + routing_packets
    print(
        "\n\n*********************************** Summary ***********************************"
    )
    print(f"Total Packets: {total_packets}")
    print(f"Routing Packets: {routing_packets}")
    print(f"Data Packets: {data_packets}")
    print(f"Data Packets Successfully Sent: {successfully_sent}")
    print(f"Data Packets Lost: { packets_lost }")
    if packets_lost > 0:
        print(f"- Not found in routing table: {destination_not_found}")
        print(f"- Packet TTL lower than metric from routing table: {lower_ttl}")
        print(f"- Queue was full: {queue_full}")
        print(f"- Packet TTL ended before reaching beginning of queue: {packet_died}")
        print(f"- Client was not connected: {client_not_connected}")
    print(
        "*******************************************************************************"
    )


def start_router():
    try:
        send_thread = Thread(target=handle_send)
        send_thread.daemon = True
        send_thread.start()

        while True:
            client_socket, address = router.accept()

            client_thread = Thread(target=handle_client, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        router.close()
        print("Router Closed!")
        print_summary()


if __name__ == "__main__":
    start_router()
