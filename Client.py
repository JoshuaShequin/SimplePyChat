import socket
import threading
import datetime


class Client:

    def __init__(self, port, ip):

        self.TCP_IP = ip
        self.TCP_PORT = port
        self.BUFFER_SIZE = 1024

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.TCP_IP, self.TCP_PORT))

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        while True:
            send_data = input()
            self.send_message(send_data)

    def receive_messages(self):
        while True:
            data = self.socket.recv(self.BUFFER_SIZE)

            print("<<< " + str(data, 'utf-8'))

    def send_message(self, message):
        self.socket.send(bytes(message, 'utf-8'))


IP = input("Desired IP Connection: ")
PORT = input("Desired Port Connection: ")

client = Client(int(PORT), IP)


