import socket
port = 9876
ip = '127.0.0.1'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect( (ip, port) )

while(True):
    text = input(">")
    encoded_text = text.encode()
    sock.send(encoded_text)
