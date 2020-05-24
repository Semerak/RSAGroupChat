import socket
import time

from crypto import *
from _thread import *

name = input("Your name: ")
NUMBER_BYTES = 100
Cryp = RSA(NUMBER_BYTES, name)
myPK = Cryp.get_pk()
print("Key generated!")
print("Welcome ", myPK.name)
print("e: ", myPK.e)
print("n: ", myPK.n)

SocketServer = socket.socket()

host = '127.0.0.1'
port = 1233

print('Waiting for connection')
try:
    SocketServer.connect((host, port))
except socket.error as e:
    print(str(e))
print("Connected!")


def wait_for_message(connection):
    while True:
        Response = connection.recv(1024)
        print(Response.decode('utf-8'))




SocketServer.sendall(str.encode(myPK.name))
time.sleep(0.1)
SocketServer.sendall(myPK.e.to_bytes(1024, byteorder='big'))
time.sleep(0.1)
SocketServer.sendall(myPK.n.to_bytes(1024, byteorder='big'))
time.sleep(0.1)
# read current clients
clients = {}
data = SocketServer.recv(10)
amount_of_users = int.from_bytes(data, "big")
time.sleep(0.1)
for i in range(amount_of_users):
    data = SocketServer.recv(2048)
    name = data.decode('utf-8')
    time.sleep(0.1)
    data = SocketServer.recv(2048)
    e = int.from_bytes(data, "big")
    time.sleep(0.1)
    data = SocketServer.recv(2048)
    n = int.from_bytes(data, "big")
    time.sleep(0.1)
    clients[name] = [e, n]
print("Now in network: ")
#for cl in clients:
#    print(cl)
print(clients)
start_new_thread(wait_for_message, (SocketServer,))
while True:
    value = input()
    SocketServer.send(str.encode(value))
    if value == "EXIT":
        break
SocketServer.close()
