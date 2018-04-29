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


class Server:

    def __init__(self, port, IP):

        self.version = [1, 1]

        self.on = True
        self.IP = IP  # local IP for now
        self.PORT = port  # random port to use
        self.BUFFER_SIZE = 1024
        self.messages = []  # stored [[message, timestamp], ...]
        self.connections = []  # hold all current connections for broadcasting

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.IP, self.PORT))
        self.socket.listen(10)

    def find_connections(self):
        # loop that is threaded to look for incoming connections
        while self.on:
            conn, addr = self.socket.accept()
            self.connections.append(conn)
            print('Connection Address: ', addr)
            client_thread = threading.Thread(target=self.client_connection_thread, args=(conn, ))
            client_thread.start()  # starting client handling thread

        # conn.close()

    def verify_client(self, message):
        verify_message = bytes()
        verify_message += b'\x01CHAT'
        verify_message += bytes(self.version[0])
        verify_message += bytes(self.version[1])
        if message[0:7] != verify_message:
            print(message[0:7])
            return False
        return True

    def client_connection_thread(self, conn):
        # where all of the client data is handled
        connected_time = datetime.datetime.now()
        first_data_received = False
        while self.on:
            try:
                data = conn.recv(self.BUFFER_SIZE)
                if datetime.datetime.now() - connected_time > datetime.timedelta(seconds=1):
                    conn.send(b'\x01Client took too long to validate.')
                    self.disconnect_conn(conn)
                    break
                if not first_data_received:
                    if len(data) < 6:
                        conn.send(b'\x01Wrong version or client for this connection!')
                        self.disconnect_conn(conn)
                        break
                    if self.verify_client(data):
                        first_data_received = True
                        print("Client Verified", conn)
                        continue
                    else:
                        conn.send(b'\x01Wrong version or client for this connection!')
                        self.disconnect_conn(conn)
                        break
            except ConnectionResetError:  # handling when a client disconnects abruptly
                self.disconnect_conn(conn)
                break
            if not data:
                break
            else:
                print("Received Data: ", data)
                for connection in self.connections:
                    if connection != conn:
                        try:
                            connection.send(data)
                        except ConnectionResetError:  # client no longer connected, so we don't try to send them a msg
                            pass  # was going to actually delete any connections that disconnected here, but I will let
                            # threads remove their own connections

    def disconnect_conn(self, conn):
        indexed = self.connections.index(conn)
        print("Disconnected: ", conn)
        self.connections[indexed].close()
        del self.connections[indexed]


IP = input("Desired IP: ")
PORT = input("Desired Port: ")

s = Server(int(PORT), IP)
t = threading.Thread(target=s.find_connections)
t.start()


