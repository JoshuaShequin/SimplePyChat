import socket
import threading
import datetime

TCP_IP = '127.0.0.1'
TCP_PORT = 9999
BUFFER_SIZE = 1024
MESSAGE = bytes("Hello, World!", 'utf-8')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))


def receive_messages():

    while True:
        data = s.recv(BUFFER_SIZE)

        print("<<< " + str(data, 'utf-8'))


receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()


def send_message(message):

    s.send(bytes(message, 'utf-8'))


while True:
    send_data = input()
    send_message(send_data)

