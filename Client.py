import socket
import threading
import datetime
import ctypes


class Client:

    def __init__(self, port, ip, username):

        self.version = [ctypes.c_uint8(1), ctypes.c_uint8(1)]

        self.TCP_IP = ip
        self.TCP_PORT = port
        self.BUFFER_SIZE = 1024
        self.username = username

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.TCP_IP, self.TCP_PORT))

        self.open = True

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        while self.open:
            send_data = input()
            self.send_message(send_data)

    def receive_messages(self):
        verify_message = bytes()  # essentially the message we need to see to verify client version etc.
        # will be:
        # Byte 0: Administration Identifier of 0x01
        # Bytes 1-4: CHAT as a verification message sort of, unique identifier
        verify_message += b'\x01CHAT'
        verify_message += bytes(self.version[0])
        verify_message += bytes(self.version[1])
        verify_message += bytes(ctypes.c_uint8(len(self.username)))
        verify_message += bytes(self.username, 'utf-8')
        self.socket.send(verify_message)
        while True:
            data = self.socket.recv(self.BUFFER_SIZE)
            if data == b'':
                self.open = False
                print("Connection Closed")
                break
            print(str(data, 'utf-8'))

    def send_message(self, message):
        self.socket.send(bytes(message, 'utf-8'))


IP = input("Desired IP Connection: ")
PORT = input("Desired Port Connection: ")
USERNAME = input("Desired Username: ")

while len(USERNAME) > 16:
    print("Username cannot be longer than 16 characters")

client = Client(int(PORT), IP, USERNAME)


