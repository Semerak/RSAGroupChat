import socket
import os
from _thread import *
import time

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
message = [""]
clients = {}
pks = {}
lock = allocate_lock()
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)


def send_all_pks(connection):
    cur_pks = pks.copy()
    connection.sendall(len(cur_pks).to_bytes(10, byteorder='big'))
    time.sleep(0.1)
    for name in cur_pks:
        connection.sendall(str.encode(name))
        time.sleep(0.1)
        connection.sendall(cur_pks[name][0])
        time.sleep(0.1)
        connection.sendall(cur_pks[name][1])
        time.sleep(0.1)


def threaded_client(connection, mes):
    # connection.send(str.encode('Welcome to the Server\n'))
    data = connection.recv(2048)
    name = data.decode('utf-8')
    # name = data
    e = connection.recv(2048)
    n = connection.recv(2048)
    print("New member ", name)
    print(name, " e: ", int.from_bytes(e, "big"))
    print(name, " n: ", int.from_bytes(n, "big"))
    pks[name] = [e, n]
    clients[name] = connection
    send_all_pks(connection)

    while True:

        data = connection.recv(2048)
        # reply = data.decode('utf-8')
        if not data:
            break
        lock.acquire()
        mes[0] = data
        lock.release()
        last_data = data
        if data.decode('utf-8') == "EXIT":
            break
        # connection.sendall(str.encode(reply))
    lock.acquire()
    clients.remove(connection)
    lock.release()
    connection.close()


def thread_broadcast():
    last_mess = ""
    print("Listening")
    while True:
        cur_mess = message[0]
        if last_mess != cur_mess:
            print(cur_mess.decode('utf-8'))
            for cl in clients:
                try:
                    clients[cl].sendall(cur_mess)
                except:
                    continue
            last_mess = cur_mess


start_new_thread(thread_broadcast, ())

while True:
    print("Searching")
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, message,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()
