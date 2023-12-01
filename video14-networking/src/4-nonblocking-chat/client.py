import socket
import sys
import select
from time import sleep
from nonblocking_readline import nonblocking_readline
port = 9876
ip = '127.0.0.1'

def handle_connection(sock):
    sock.setblocking(False)
    while(True):
        try:
            keytext = nonblocking_readline()
        except EOFError:
            sys.exit()

        if keytext != "":
            encoded_text = keytext.encode()
            try:
                sock.send(encoded_text)
            except BrokenPipeError:
                print("remote site disconnected")
                return

        try:
            encoded_text = sock.recv(1024)
            if len(encoded_text) == 0:
                print("remote site disconnected")
                sock.close()
                break
            text = encoded_text.decode()
            print(">>", text, "<<")
        except BlockingIOError:
            sleep(0.2)

if __name__ == "__main__":
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
    handle_connection(sock)
