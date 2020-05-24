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
clients = {}
SocketServer = socket.socket()

host = '127.0.0.1'
port = 1233

print('Waiting for connection')
try:
    SocketServer.connect((host, port))
except socket.error as e:
    print(str(e))
print("Connected!")

read = True


def wait_for_message(connection):
    global read
    while read:
        string_to_print = ""
        Response = connection.recv(1024)
        full_message = Response.decode('utf-8')
        if ":" in full_message:
            name_from, text = full_message.split(":")
            global clients
            if name_from in clients:
                decrypt_text = Cryp.decrypt(int(text), to_str)
                string_to_print = name_from + ": " + decrypt_text
        if string_to_print == "":
            string_to_print = full_message
        print(string_to_print)


def update_clients(connection):
    global read
    read = False
    global clients
    clients = {}
    data = connection.recv(10)
    amount_of_users = int.from_bytes(data, "big")
    print(amount_of_users)
    time.sleep(0.1)
    for i in range(amount_of_users):
        data = connection.recv(2048)
        cl_name = data.decode('utf-8')
        time.sleep(0.1)
        data = connection.recv(2048)
        e = int.from_bytes(data, "big")
        time.sleep(0.1)
        data = connection.recv(2048)
        n = int.from_bytes(data, "big")
        time.sleep(0.1)

        clients[cl_name] = PK(e, n, cl_name)
    read = True
    start_new_thread(wait_for_message, (SocketServer,))
    print("Now in network: ")
    for cl in clients:
        print(cl)
    # print(clients)


start_new_thread(wait_for_message, (SocketServer,))
SocketServer.sendall(str.encode(myPK.name))
time.sleep(0.1)
SocketServer.sendall(myPK.e.to_bytes(1024, byteorder='big'))
time.sleep(0.1)
SocketServer.sendall(myPK.n.to_bytes(1024, byteorder='big'))
time.sleep(0.1)
# read current clients

update_clients(SocketServer)

while True:
    value = input()
    if "<" in value:
        name_to, text = value.split("<", 1)
        if name_to in clients:
            encrypt_text = clients[name_to].encrypt(text, to_int)
            SocketServer.sendall(str.encode(name_to + "<" + str(encrypt_text)))
        else:
            SocketServer.send(str.encode(value))
    elif value == "EXIT":
        SocketServer.send(str.encode(value))
        break
    elif value == "PEOPLE":
        SocketServer.send(str.encode(value))
        update_clients(SocketServer)
    else:
        SocketServer.send(str.encode(value))

SocketServer.close()
