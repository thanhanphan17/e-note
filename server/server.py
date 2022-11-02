from request import send_all_note
from upload import add_note, note_size
from connect import get_access_urls, upload_file
from signup import *
from login import *

import glob
import socket
import os
import pickle
import threading


PORT = 5050
SERVER = '0.0.0.0'
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

MAX_BYTE = 2048
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
PATH = os.path.dirname(os.path.realpath(__file__))


def remove_file():
    files = glob.glob(PATH + "/img/" + "*")
    for f in files:
        os.remove(f)

    files = glob.glob(PATH + "/file/" + "*")
    for f in files:
        os.remove(f)


def receive_command(conn):
    msg = conn.recv(MAX_BYTE)
    return msg.decode(FORMAT)


def receive_login_account(conn):
    msg = conn.recv(MAX_BYTE)
    lst = pickle.loads(msg)

    for element in lst:
        element = str(element)

    return lst[0], lst[1]


def receive_register_account(conn):
    msg = conn.recv(MAX_BYTE)
    lst = pickle.loads(msg)

    for element in lst:
        element = str(element)

    return lst[0], lst[1], lst[2]


def receive_new_note(conn):
    file_size = int(conn.recv(MAX_BYTE).decode(FORMAT))
    file_data = conn.recv(file_size)

    while (len(file_data) < file_size):
        remain = conn.recv(file_size - len(file_data))
        file_data += remain

    # print(len(file_data))

    lst = conn.recv(MAX_BYTE)
    data = pickle.loads(lst)
    ext = data[2]

    # print(ext)
    file_name = "data/" + str(note_size()) + "." + str(ext)
    # print(file_name)
    file_write = open(PATH + "/" + file_name, "wb")
    file_write.write(file_data)

    note = {
        "author": "ptan21",
        "title": data[0],
        "type": "text",
        "content": data[1],
        "file": file_name
    }
    return file_data, note


def receive_note(conn):
    note_type = conn.recv(MAX_BYTE).decode(FORMAT)
    # print(note_type)
    if note_type == "text":
        lst = conn.recv(MAX_BYTE)
        data = pickle.loads(lst)
        author = data[0]
        title = data[1]
        content = data[2]
        day = data[3]

        note = {
            "author": author,
            "title": title,
            "type": note_type,
            "content": content,
            "time": day
        }

        return note
    elif note_type == "image":
        file_size = int(conn.recv(MAX_BYTE).decode(FORMAT))
        file_data = conn.recv(file_size)

        while (len(file_data) < file_size):
            remain = conn.recv(file_size - len(file_data))
            file_data += remain

        lst = conn.recv(MAX_BYTE)
        data = pickle.loads(lst)

        # print(data)
        author = data[0]
        title = data[1]
        ext = data[2]
        day = data[3]
        # print(ext)

        file_name = "img/" + str(note_size()) + "." + ext
        # print(file_name)
        file_write = open(PATH + "/" + file_name, "wb")
        file_write.write(file_data)

        note = {
            "author": author,
            "title": title,
            "type": note_type,
            "file": file_name,
            "time": day
        }

        return note
    else:
        file_size = int(conn.recv(MAX_BYTE).decode(FORMAT))
        file_data = conn.recv(file_size)

        while (len(file_data) < file_size):
            remain = conn.recv(file_size - len(file_data))
            file_data += remain

        lst = conn.recv(MAX_BYTE)
        data = pickle.loads(lst)

        # print(data)
        author = data[0]
        title = data[1]
        day = data[3]

        file_name = "file/" + data[2]
        # print(file_name)
        file_write = open(PATH + "/" + file_name, "wb")
        file_write.write(file_data)

        note = {
            "author": author,
            "title": title,
            "type": note_type,
            "file": file_name,
            "time": day
        }

        return note


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try:
        connected = True
        while connected:
            cmd = receive_command(conn)
            if cmd == "login":
                username, password = receive_login_account(conn)
                user = authenticate(username, password)
                conn.send(loginMessage(username, password).encode(FORMAT))
                if user:
                    send_all_note(conn, username)

            if cmd == "signup":
                fullname, username, password = receive_register_account(conn)
                # print(fullname, username, password)
                reg_msg = register(fullname, username, password)
                conn.sendall(reg_msg.encode(FORMAT))

            if cmd == "send_note":
                note = receive_note(conn)
                add_note(note)
                send_all_note(conn, username)

                if note["type"] != "text":
                    url = note["file"]
                    upload_file(PATH + "/" + url, url)

                remove_file()

            if cmd == "request image":
                file_name = conn.recv(2048).decode(FORMAT)
                url = get_access_urls(file_name)
                conn.sendall(url.encode(FORMAT))

            if cmd == "request file":
                file_name = conn.recv(2048).decode(FORMAT)
                url = get_access_urls(file_name)
                conn.sendall(url.encode(FORMAT))

    except:
        print(f"{conn.getpeername()} closed")

    conn.close()


def start():
    try:
        server.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(
                target=handle_client, args=(conn, addr))
            thread.start()
            # print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
    except:
        print("Error")


if __name__ == "__main__":
    print("[STARTING] server is starting...")
    start()
