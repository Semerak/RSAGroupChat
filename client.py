import socket
from _thread import *

SocketServer = socket.socket()

host = '127.0.0.1'
port = 1233

print('Waiting for connection')
try:
    SocketServer.connect((host, port))
except socket.error as e:
    print(str(e))
print("Connected!")


def wait_for_input(connection):
    while True:
        Response = connection.recv(1024)
        print(Response.decode('utf-8'))


start_new_thread(wait_for_input, (SocketServer,))
while True:
    value = input()
    SocketServer.send(str.encode(value))
    if value == "EXIT":
        break
SocketServer.close()
