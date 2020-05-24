import socket
import os
from _thread import *
import time

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
# message = [""]
clients = {}
pks = {}
groups = {}
lock = allocate_lock()
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)


def send_all_groups(cl_name):
    connection = clients[cl_name]
    time.sleep(1)
    connection.sendall(str.encode("GROUPS"))
    time.sleep(0.1)
    string_for_group = ""
    for gr_name in groups:
        if cl_name in groups[gr_name]:
            string_for_group += gr_name + ":" + ",".join(groups[gr_name]) + ";"
    connection.sendall(str.encode(string_for_group[:-1]))


def send_all_pks(connection):
    time.sleep(1)
    connection.sendall(str.encode("Sending new dictionary of people"))
    cur_pks = pks.copy()
    time.sleep(1)
    print(len(cur_pks))
    connection.sendall(len(cur_pks).to_bytes(10, byteorder='big'))
    time.sleep(0.1)
    for name in cur_pks:
        connection.sendall(str.encode(name))
        time.sleep(0.1)
        connection.sendall(cur_pks[name][0])
        time.sleep(0.1)
        connection.sendall(cur_pks[name][1])
        time.sleep(0.1)


def send_message(name, text):
    if name == "all":
        for cl in clients:
            clients[cl].sendall(str.encode(text))
    elif name in clients:
        print("send to ", name, " from ", text)
        clients[name].sendall(str.encode(text))



def threaded_client(connection, ):
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
        # lock.acquire()
        # mes[0] = data
        # lock.release()
        # last_data = data
        try:
            message = data.decode('utf-8')
            print(message)
            if message == "EXIT":
                break
            elif message == "PEOPLE":
                send_all_pks(connection)
            elif "GROUPS" == message:
                send_all_groups(name)
            elif "GROUP" in message:
                if "CREATE" in message:
                    group_name, group_members = message.split(":", 1)
                    group_name = group_name.split("\"")[1]
                    members = group_members.split(",")
                    groups[group_name] = members
                    for mem_name in members:
                        send_all_groups(mem_name)
                if "ADD" in message:
                    group_name, group_members = message.split(":", 1)
                    group_name = group_name.split("\"")[1]
                    members = group_members.split(",")
                    groups[group_name].extend(members)
                    for mem_name in members:
                        send_all_groups(mem_name)
                if "REMOVE" in message:
                    group_name, group_members = message.split(":", 1)
                    group_name = group_name.split("\"")[1]
                    members = group_members.split(",")
                    print("in groups")
                    old_members=groups[group_name]
                    for mem_name in members:
                        groups[group_name].remove(mem_name)
                        print(f"{group_name} removed {mem_name}")
                    for mem_name in old_members:
                        send_all_groups(mem_name)


            elif "<" in message:
                name_to, text = message.split("<", 1)
                if name_to in clients:
                    send_message(name_to, name + ": " + text)
                elif name_to in groups:
                    for name_member in groups[name_to]:
                        send_message(name_member,f"({name_to}) {name}: {text}")
        except:
            continue

        # connection.sendall(str.encode(reply))
    lock.acquire()
    del clients[name]
    lock.release()
    connection.close()


# def thread_broadcast():
#     last_mess = ""
#     print("Listening")
#     while True:
#         cur_mess = message[0]
#         if last_mess != cur_mess:
#             print(cur_mess.decode('utf-8'))
#             for cl in clients:
#                 try:
#                     clients[cl].sendall(cur_mess)
#                 except:
#                     continue
#             last_mess = cur_mess


# start_new_thread(thread_broadcast, ())

while True:
    print("Searching")
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()
