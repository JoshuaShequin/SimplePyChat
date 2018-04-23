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

    def __init__(self):

        self.on = True
        self.IP = '127.0.0.1'  # local IP for now
        self.PORT = 5005  # random port to use
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

    def client_connection_thread(self, conn):
        # where all of the client data is handled
        while self.on:
            data = conn.recv(self.BUFFER_SIZE)
            if not data:
                break
            else:
                print("Received Data: ", data)
                remList = []  # using this list to remove connections after loop finishes
                counter = 0
                for connection in self.connections:
                    if connection != conn:
                        try:
                            connection.send(data)
                        except ConnectionResetError:
                            remList.append(counter)
                    counter += 1

                remList.sort(reverse=True)  # have to sort otherwise we delete the, intended index - deleted items
                for rem in remList:
                    del self.connections[rem]


s = Server()
t = threading.Thread(target=s.find_connections)
t.start()


