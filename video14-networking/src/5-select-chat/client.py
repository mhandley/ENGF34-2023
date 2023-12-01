import socket
import sys
import select
from time import sleep
port = 9876
ip = '127.0.0.1'

def handle_connection(sock):
    while(True):
        rd, wd, ed = select.select([sock, sys.stdin], [], [])
        if sys.stdin in rd:
            try:
                keytext = sys.stdin.readline()
            except EOFError:
                sys.exit()

            encoded_text = keytext.encode()
            try:
                sock.send(encoded_text)
            except BrokenPipeError:
                print("remote site disconnected")
                return

        if sock in rd:
            encoded_text = sock.recv(1024)
            if len(encoded_text) == 0:
                sock.close()
                break
            text = encoded_text.decode()
            print(">>", text, "<<")

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
