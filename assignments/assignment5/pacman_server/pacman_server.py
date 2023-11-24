import socket
from sys import argv, exit
import select
from time import sleep
from getopt import getopt, GetoptError

class Network():
    def __init__(self):
        self.port = 9872
        self.active_socks = []
        self.half_open_socks = {}
        self.waiting_socks = {}  #socket, indexed by password
        self.waiting_passwords = {} #password, indexed by socket
        self.sock_pairs = {}
        self.logfile = open("logfile.txt", "w+")
        try:
            self.listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err: 
            print("socket creation failed with error %s" %(err), file=self.logfile)
            exit()
        self.__recv_buf = bytes()

    def listen(self):
        print("listening on port", self.port)
        while True:
            try:
                self.listening_sock.bind(('', self.port))
                break
            except OSError as err:
                print(err, file=self.logfile)
                print("waiting, will retry in 10 seconds")
                sleep(10)
  
        # put the socket into listening mode 
        self.listening_sock.listen(5)
        print("listening for incoming connection...", file=self.logfile)
        self.active_socks.append(self.listening_sock)

    def parse_args(self, argv):
        try:
            if "pacman_server.py" in argv[0]:
                opts, args = getopt(argv[1:], "p:", ["port="])
            else:
                opts, args = getopt(argv, "p:", ["port="])
        except GetoptError:
            self.usage()
        for opt, arg in opts:
            if opt in ("-p", "--port"):
                self.port = int(arg)
            else:
                self.usage()

    def accept_connection(self):
        # Establish connection from client. 
        c_sock, addr = self.listening_sock.accept()
        print('Got connection from', addr, file=self.logfile)
        self.logfile.flush()
        self.half_open_socks[c_sock] = addr
        self.active_socks.append(c_sock)

    def receive_passwd(self, c_sock):
        fd = c_sock.fileno()
        print("receive_passwd, fd=", fd, file=self.logfile)
        try:
            msg = c_sock.recv(1024)
        except OSError:
            msg = bytes()

        if len(msg) == 0:
            # the connection died - cleanup its state
            print("half open connection died, fd=", fd, file=self.logfile)
            del self.half_open_socks[c_sock]
            if c_sock in self.active_socks:
                self.active_socks.remove(c_sock)
            return
            
        passwd = msg.decode()

        if passwd in self.waiting_socks:
            # password patches that of a waiting connection - join them up
            waiting_sock = self.waiting_socks[passwd]
            wfd = waiting_sock.fileno()
            print("fd ", fd, "passwd ", passwd, "matches fd", wfd, file=self.logfile)
            c_sock.send("OK\n".encode())
            waiting_sock.send("OK\n".encode())
            self.sock_pairs[c_sock] = waiting_sock
            self.sock_pairs[waiting_sock] = c_sock
            del self.waiting_passwords[waiting_sock]
            del self.waiting_socks[passwd]
        else:
            # move connection from half-open to one that has a password and is waiting
            print("fd ", fd, "received passwd ", passwd, file=self.logfile)
            self.waiting_socks[passwd] = c_sock
            self.waiting_passwords[c_sock] = passwd
            del self.half_open_socks[c_sock]

    def relay_message(self, sock):
        partner_sock = self.sock_pairs[sock]
        cleanup = False
        try:
            recv_bytes = sock.recv(10000)
            if len(recv_bytes) == 0:
                cleanup = True
            else:
                partner_sock.send(recv_bytes)
        except ConnectionResetError:
            cleanup = True
        except BrokenPipeError:
            cleanup = True
        if cleanup:
            sock.close()
            partner_sock.close()
            del self.sock_pairs[sock]
            del self.sock_pairs[partner_sock]
            self.active_socks.remove(sock)
            self.active_socks.remove(partner_sock)

    def close_half_open_sock(self, sock):
        print("Error: ", sock.fileno(),
              "got a message from a waiting sock!", file=self.logfile)
        # no idea what to do, just close it.
        self.active_socks.remove(sock)
        sock.close()
        passwd = self.waiting_passwords[sock]
        del self.waiting_passwords[sock]
        del self.waiting_socks[passwd]
        
    def check_for_messages(self):
        rd, wd, ed = select.select(self.active_socks, [],[])
        if not rd:
            pass
        else:
            for sock in rd:
                if sock is self.listening_sock:
                    # it's a new connection
                    self.accept_connection()
                elif sock in self.sock_pairs:
                    # it's a message on an existing pair
                    self.relay_message(sock)
                elif sock in self.half_open_socks:
                    # it's a message from a connection we've not yet heard a password
                    self.receive_passwd(sock)
                elif sock in self.waiting_passwords:
                    # it's a second message from a unpaired connection
                    self.close_half_open_sock(sock)
                else:
                    # we've no idea what happened!
                    print("Got a stray socket!", sock, file=self.logfile)
                    try:
                        sock.close()
                    except:
                        pass
                    

net = Network()
net.parse_args(argv)
net.listen()

while True:
    net.check_for_messages()
