"""

--Simple Python Chat Server--

Handles multiple users message's and updates all clients with new information

Flow:
1. Server Startup
    1a. Opens ports, and binds socket
    2a. Creates chat log file
2. Main Loop Entered
    2a. Creates connection with users, updating their chat with current log data
    2b. Receives messages from users
    2c. Updates all clients with new messages
3. Chat server close event
    3a. Notifies all current clients of chat closing
    3b. zips and stores log file

"""

import socket  # used to create the actual socket connection needed for TCP
import threading
import datetime
import ctypes


class UserConnection:

    def __init__(self, conn):

        self.connection = conn

        self.verified = False
        self.user_name = None

    def disconnect(self):
        # disconnects the actual connection with the server
        try:
            self.connection.send(b"Goodbye.")
            self.connection.close()
        except ConnectionResetError:
            # The connection was already closed so we cannot send a goodbye message and close it ourselves
            pass

    def send_message(self, message):
        # takes a bytes type message and sends to client
        if self.verified or message[0] == 0x01:  # only send data to a client if it has been verified, unless it admin
            self.connection.send(message)

    def receive_message(self, buffer):

        return self.connection.recv(buffer)

    def verification_update(self, user_name, welcome_message):

        self.verified = True
        self.user_name = user_name
        self.send_message(welcome_message)


class Server:

    def __init__(self, port, IP):

        self.version = [ctypes.c_uint8(1), ctypes.c_uint8(1)]

        self.welcome_message = b'Welcome. Type your message and send it across the world!'

        self.on = True
        self.IP = IP  # local IP for now
        self.PORT = port  # random port to use
        self.BUFFER_SIZE = 1024
        self.messages = []  # stored [[message, timestamp], ...]
        self.connections = []  # hold all current connections for broadcasting etc.

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.IP, self.PORT))
        self.socket.listen(10)

    def find_connections(self):
        # loop that is threaded to look for incoming connections
        while self.on:
            conn, addr = self.socket.accept()
            print('Connection Address: ', addr)
            client_thread = threading.Thread(target=self.verify_client, args=(conn, ))
            client_thread.start()  # starting client handling thread, actually starts in the verify function though

        # conn.close()

    def verify_client(self, conn):
        verify_message = bytes()  # essentially the message we need to see to verify client version etc.
        # will be:
        # Byte 0: Administration Identifier of 0x01
        # Bytes 1-4: CHAT as a verification message sort of, unique identifier
        # Bytes 5-6: Major, Minor Version
        # Byte 7: Length of User name
        # Byte 8-n: Username

        verify_message += b'\x01CHAT'
        verify_message += bytes(self.version[0])
        verify_message += bytes(self.version[1])
        u_conn = UserConnection(conn)
        data = u_conn.receive_message(24)  # maximum initial message size of 24 bytes

        if data[0:7] != verify_message:
            print(data[0:7])
            conn.send(b'\x01Wrong version or client for this connection!')
            self.disconnect_conn(conn)
        else:
            user_name_length = int(data[7])
            if len(data) - 8 != user_name_length:  # if the length doesn't match the data left in the message
                print(len(data) - 8, user_name_length)
                conn.send(b'\x01Wrong version or client for this connection!')
                self.disconnect_conn(u_conn)
            else:
                user_name = data[8:]
                u_conn.verification_update(user_name, self.welcome_message)
                self.connections.append(u_conn)
                self.client_connection_thread(u_conn)
        return True

    def client_connection_thread(self, u_conn):
        # where all of the client data is handled
        connected_time = datetime.datetime.now()
        first_data_received = False
        while self.on:
            try:
                data = u_conn.receive_message(self.BUFFER_SIZE)
            except ConnectionResetError:  # handling when a client disconnects abruptly
                self.disconnect_conn(u_conn)
                break
            if not data:
                break
            else:
                print("Received Data: ", data)
                out_data = u_conn.user_name + bytes(": ", 'utf-8') + data
                for connection in self.connections:
                    if connection != u_conn:  # make sure we aren't sending the client what it sends us
                        try:
                            connection.send_message(out_data)
                        except ConnectionResetError:  # client no longer connected, so we don't try to send them a msg
                            pass  # was going to actually delete any connections that disconnected here, but I will let
                            # threads remove their own connections

    def disconnect_conn(self, u_conn):
        # we disconnect the client and remove it from our list of clients here
        print("Disconnected: ", u_conn.connection)
        if u_conn.verified:
            index_pos = self.connections.index(u_conn)
            del self.connections[index_pos]




IP = input("Desired IP: ")
PORT = input("Desired Port: ")

s = Server(int(PORT), IP)
t = threading.Thread(target=s.find_connections)
t.start()


