import socket
import sys

port = 9876

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind( ('', port) )
sock.listen(1)

while True:
    newsock, addr = sock.accept()

    while(True):
        encoded_text = newsock.recv(1024)
        if len(encoded_text) == 0:
            print("remote site disconnected")
            newsock.close()
            break
        text = encoded_text.decode()
        print(">>", text, "<<")
