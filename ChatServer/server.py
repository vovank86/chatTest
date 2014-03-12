#!/usr/bin/env python
# -*- coding: utf-8 -*-

#******************************
# Chat server
#******************************

__author__ = 'Vladimir Kanubrikov'

import socket
import select
import settings
import db
import json
import sys
import threading


def vote_complete(vote_id, user_name, room_name):
    print "vote complete"
    auth(sock, json.dumps({'operation': 'vote_complete', 'user': user_name, 'room': room_name}))
    broadcast_data(sock, json.dumps({'operation': 'vote_complete', 'user': user_name, 'room': room_name}))
    if db.send_result_of_vote(vote_id):
        auth(sock, json.dumps({'operation': 'kick_user', 'user': user_name, 'room': room_name}))
        broadcast_data(sock, json.dumps({'operation': 'kick_user', 'user': user_name, 'room': room_name}))


def auth(sock, data):
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket == sock:
            try:
                socket.send(data)
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)


def broadcast_data(sock, message):
    """Function to broadcast chat messages to all connected clients."""

    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock:
            try:
                socket.send(message)
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)


def update_user_info(room):
    temp_user_dict = {}
    for user in room['users']:
        if user in users:
            temp_user_dict[user] = users[user]
        else:
            temp_user_dict[user] = ''
    room['users'] = temp_user_dict


if __name__ == "__main__":

    CONNECTION_LIST = []
    users = {}
    RECV_BUFFER = settings.SERVER_SOCKET['BUFFER_SIZE']
    PORT = settings.SERVER_SOCKET['PORT']
    HOST = settings.SERVER_SOCKET['HOST']

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    def cheek_first_run():
        """
        Cheek is it a first run of the chat server or not.
        If it's the first run this function run the installation process.
        """
        session = db.Session()
        if 0 == session.query(db.User).order_by(db.User.id).count():
            db.install_chat(session, PORT)
        else:
            print "Chat server started on port " + str(PORT)

    cheek_first_run()

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        user_data = json.loads(data)
                        print 'called server operation:', user_data["operation"]
                        if "login" == user_data["operation"]:
                            if not db.auth_user(user_data['user'], user_data['password']):
                                send_text = 'fail'
                                print "Client (%s, %s) login wrong" % addr
                                sock.close()
                                CONNECTION_LIST.remove(sock)
                            else:
                                base_data = db.auth_user(user_data['user'], user_data['password'])

                                if users:
                                    if not base_data['user_name'] in users:
                                        users[base_data['user_name']] = addr

                                else:
                                    users[base_data['user_name']] = addr

                                for room in base_data['user_rooms']:
                                    update_user_info(room)

                                change_users_status = json.dumps({'operation': 'change_user_status', 'users': users})
                                send_text = json.dumps(base_data)
                                #print send_text
                                print "Client (%s, %s) was login" % addr
                                auth(sock, send_text)
                                broadcast_data(sock, change_users_status)

                        elif "send_mess" == user_data["operation"]:
                            user_data = json.dumps(user_data)
                            auth(sock, user_data)
                            broadcast_data(sock, user_data)

                        elif "exit" == user_data["operation"]:
                            address = users.get(user_data['user'])
                            users.pop(user_data['user'])
                            change_users_status = json.dumps({'operation': 'change_user_status', 'users': users})
                            broadcast_data(sock, change_users_status)
                            print "Client (%s, %s) is offline" % address
                            sock.close()
                            CONNECTION_LIST.remove(sock)
                            continue

                        elif "is_admin" == user_data["operation"]:
                            is_admin = db.is_admin(user_data["user"], user_data["room"])
                            is_admin = json.dumps({'operation': 'is_admin', 'val': is_admin})
                            auth(sock, is_admin)

                        elif "kick_user" == user_data["operation"]:
                            kick = db.kick_user(user_data["user"], user_data["room"])
                            if kick:
                                kick = json.dumps(
                                    {'operation': 'kick_user', 'user': user_data["user"], 'room': user_data["room"]})
                                broadcast_data(sock, kick)
                                auth(sock, kick)

                        elif "get_users" == user_data["operation"]:
                            auth(sock, json.dumps({'operation': 'get_users', 'val': db.get_users(user_data['room'])}))

                        elif "get_perms" == user_data["operation"]:
                            auth(sock, json.dumps({'operation': 'get_perms', 'val': db.get_perms()}))

                        elif "add_user" == user_data["operation"]:
                            user = user_data['user']
                            room = user_data['room']
                            perms = user_data['perm']
                            add_user_obj = db.add_u_to_the_r(user, room, perms)
                            user = add_user_obj['user_name']
                            room = add_user_obj['room']
                            update_user_info(room)
                            auth(sock, json.dumps({'operation': 'add_user', 'user': user, 'room': room}))
                            broadcast_data(sock, json.dumps({'operation': 'add_user', 'user': user, 'room': room}))

                        elif "start_vote" == user_data["operation"]:
                            user = user_data['user']
                            room = user_data['room']
                            vote = db.create_vote(user, room)
                            if vote:
                                start = json.dumps(
                                    {'operation': user_data["operation"], 'user': user, 'room': room, 'vote': vote})

                                auth(sock, start)
                                broadcast_data(sock, start)

                                def go():
                                    vote_complete(vote, user, room)

                                t = threading.Timer(60.0, go)
                                t.start()
                                print "start timer 60s..."



                except:
                    e = sys.exc_info()[0]
                    print e
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue

server_socket.close()
