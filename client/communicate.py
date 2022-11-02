import socket
import pickle

# Client connect
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "0.0.0.0"
ADDR = (SERVER, PORT)
client = ""


def connect_server(ADDR):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        return client
    except:
        return False


# Send message to server
def send_message(client, msg):
    client.send(msg.encode(FORMAT))


# Send request command to server
def send_command(client, cmd):
    client.sendall(cmd.encode(FORMAT))


# Send list by pickle to server
def send_pickle(client, lst):
    data = pickle.dumps(lst)
    client.sendall(data)


# Receive message from server
def receive_message(client):
    return str(client.recv(2048).decode(FORMAT))
