import socket
import sys
from client import handle_connection

port = 9876

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind( ('', port) )
sock.listen(1)

while True:
    newsock, addr = sock.accept()
    handle_connection(newsock)
