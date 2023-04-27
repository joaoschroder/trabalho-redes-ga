import socket
from time import sleep
from random import choice, randrange
import json

HOST = "localhost"
PORT = 4000

router = (HOST, PORT)

machine = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sleep(3)
machine.connect(router)

origins = ["10.10.10.1", "20.20.20.1", "30.30.30.1", "40.40.40.1"]
movie_ideas = [
    "The Godfather",
    "Casino Royale",
    "Skyfall",
    "Spectre",
    "Kingdom of Heaven",
    "Gladiator",
    "Troy",
    "The Last Samurai",
    "Schindler's List",
    "The Pianist",
    "John Wick",
    "Hacksaw Ridge",
    "Braveheart",
    "Scent of a Woman",
    "Moneyball",
    "Whiplash",
]

print("Sending movie ideas...")


def start_machine():
    try:
        while True:
            sleep(1)
            data_packet = {
                "origin": choice(origins),
                "destination": "",
                "ttl": randrange(1, 6),
                "tos": "Type Of Service",
                "message": choice(movie_ideas),
            }
            machine.send(bytes(json.dumps(data_packet), "utf-8"))
    except KeyboardInterrupt:
        machine.close()
        print("Machine Closed!")
    except socket.error:
        machine.close()
        print("Machine Closed!")


if __name__ == "__main__":
    start_machine()
