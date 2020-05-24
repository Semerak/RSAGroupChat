import socket
import time

from crypto_simple import *
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
groups = {}
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


def tutorial():
    print("""
    PEOPLE - update all information about users in network
    [name]<[text] - send encrypted message to person
    [name_group]<[text] - send encrypted message to group
    GROUPS - update information about groups, you are in
    GROUP CREATE "[name_group]":[name_user1],[name_user2] - create new group
    GROUP ADD "[name_group]:[name_user1],[name_user2] - add users to group
    GROUP REMOVE "[name_group]:[name_user1],[name_user2] - remove users from group
    EXIT - to exit messenger 
    ? - open tutorial
    """)


def update_groups(connection):
    data = connection.recv(2048)
    text = data.decode('utf-8')
    new_groups = {}
    new_groups_text = text.split(";")
    for new_group_text in new_groups_text:
        new_name, members_text = new_group_text.split(":")
        try:
            new_group = Group()
            for mem_name in members_text.split(","):
                new_group.add(clients[mem_name])
            new_groups[new_name] = new_group
            print(new_group_text)
        except:
            print("Problem with group ", new_name)
    global groups
    groups = new_groups


def wait_for_message(connection):
    global read
    while read:
        try:
            string_to_print = ""
            Response = connection.recv(1024)
            full_message = Response.decode('utf-8')
            if full_message == "GROUPS":
                update_groups(connection)
            elif ":" in full_message:
                name_from, text = full_message.split(":")
                global clients
                decrypt_text = Cryp.decrypt(int(text), to_str)
                string_to_print = name_from + ": " + decrypt_text
            if string_to_print == "":
                string_to_print = full_message
            print(string_to_print)
        except:
            continue


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
tutorial()
while True:
    value = input()
    if value == "MY GROUPS":
        print("current groups:")
        for gr_name in groups:
            string_for_group = gr_name + ": "
            for pk in groups[gr_name].get():
                string_for_group += pk.name + " "
            print(string_for_group)
    elif "GROUPS" == value:
        SocketServer.send(str.encode(value))

    elif "GROUP" in value:
        if "CREATE" in value:
            SocketServer.send(str.encode(value))
            # group_name, group_members = value.split(":", 1)
            # group_name = group_name.split("\"")[1]
            # members = group_members.split(",")
            # groups[group_name] = Group()
            # mem in members:
            #    groups[group_name].add(clients[mem])
        elif "ADD" in value:
            group_name = value.split("\"")[1]
            group_members = value.split(":")[1]
            members = group_members.split(",")
            if clients[name] in groups[group_name].get():
                for mem in members:
                    if groups[group_name].add(clients[mem]):
                        SocketServer.send(str.encode(value))
            else:
                print("You don`t have an access")
        elif "REMOVE" in value:
            group_name = value.split("\"")[1]
            group_members = value.split(":")[1]
            members = group_members.split(",")
            if clients[name] in groups[group_name].get():
                for mem in members:
                    groups[group_name].remove(clients[mem])
                    SocketServer.send(str.encode(value))
            else:
                print("You don`t have an access")


    elif "<" in value:
        name_to, text = value.split("<", 1)
        if name_to in clients:
            encrypt_text = clients[name_to].encrypt(text, to_int)
            SocketServer.sendall(str.encode(name_to + "<" + str(encrypt_text)))
        elif name_to in groups:
            encrypt_text = groups[name_to].encrypt(text, to_int)
            SocketServer.sendall(str.encode(name_to + "<" + str(encrypt_text)))
        else:
            SocketServer.send(str.encode(value))
    elif value == "EXIT":
        SocketServer.send(str.encode(value))
        break
    elif value == "PEOPLE":
        SocketServer.send(str.encode(value))
        update_clients(SocketServer)
    elif value =="?":
        tutorial()
    else:
        SocketServer.send(str.encode(value))

SocketServer.close()
