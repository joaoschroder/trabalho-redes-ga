import socket
from time import sleep
from threading import Thread
import json
from random import choice, randrange

IP = "20.20.20.1"
HOST = "localhost"
PORT = 4000

router = (HOST, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(router)

destinations = ["10.10.10.1", "30.30.30.1", "40.40.40.1"]


def handle_receive():
    try:
        while True:
            received_packet = json.loads(client.recv(1024).decode("utf-8"))
            origin = received_packet["origin"]
            message = received_packet["message"]
            print(f"({origin}) >>> {message}")
    except socket.error:
        print("Client 2 Closed!")
    except json.decoder.JSONDecodeError:
        client.close()


def handle_send():
    try:
        while True:
            sleep(6)
            routing_packet = {
                "destination": choice(destinations),
                "output_interface": "20.20.20.1",
                "metric": randrange(2, 4),
            }

            client.send(bytes(json.dumps(routing_packet), "utf-8"))
    except socket.error:
        client.close()
        print("Client 2 Closed!")


def start_client():
    try:
        receive_thread = Thread(target=handle_receive)
        receive_thread.start()
        send_thread = Thread(target=handle_send)
        send_thread.start()
    except KeyboardInterrupt:
        client.close()
        print("Client 2 Closed!")


if __name__ == "__main__":
    start_client()
