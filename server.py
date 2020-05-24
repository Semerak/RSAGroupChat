import socket
import os
from _thread import *

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
message = [""]
clients = []
lock = allocate_lock()
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection, mes):
    connection.send(str.encode('Welcome to the Server\n'))
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
            for connection in clients:
                try:
                    connection.sendall(cur_mess)
                except:
                    continue
            last_mess = cur_mess


start_new_thread(thread_broadcast, ())

while True:
    print("Searching")
    Client, address = ServerSocket.accept()
    clients.append(Client)
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, message,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()
