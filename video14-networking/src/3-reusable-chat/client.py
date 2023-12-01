import socket
import sys
from time import sleep
port = 9876
ip = '127.0.0.1'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    try:
        sock.connect( (ip, port) )
        break
    except ConnectionRefusedError:
        print("waiting for server...")
        sock.close()
        sock = socket.socket(socket.AF_INET, \
                             socket.SOCK_STREAM)
        sleep(1)

while(True):
    try:
        text = input(">")
    except EOFError:
        sys.exit()
    encoded_text = text.encode()
    try:
        sock.send(encoded_text)
    except BrokenPipeError:
        print("remote site disconnected")
        sys.exit()
