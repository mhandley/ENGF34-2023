import socket
import sys
import pickle
import select
from time import sleep

class Network():
    def __init__(self, controller, password):
        self.__controller = controller
        self.__password = password
        self.__server = False
        self.__connected = False
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err: 
            print("socket creation failed with error %s" %(err))
            sys.exit()
        self.__recv_buf = bytes()
        self.get_local_ip_addr()


    def server(self, port):
        self.__server = True
        while True:
            try:
                self.__sock.bind(('', port))
                break
            except OSError as err:
                print(err)
                print("waiting, will retry in 10 seconds")
                sleep(10)
  
        # put the socket into listening mode 
        self.__sock.listen(5)
        print("listening for incoming connection...")

        while True: 
            # Establish connection with client. 
            c_sock, addr = self.__sock.accept()
            #print('Got connection from', addr)
            msg = c_sock.recv(1024)
            txt = msg.decode()
            if txt == self.__password:
                c_sock.send("OK\n".encode())
                break
            else:
                c_sock.close()
        # swap the socket names so send/recv functions don't care if we're client or server
        self.__listen_sock = self.__sock
        self.__sock = c_sock
        self.__connected = True
            

    def client(self, ip, port):
        self.__sock.connect((ip, port))
        self.__sock.send(self.__password.encode())
        msg = self.__sock.recv(1024)
        txt = msg.decode()
        if txt == "OK\n":
            self.__connected = True
        else:
            print("handshake failed\n")

    def get_local_ip_addr(self):
        # ugly hacky way to find our IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # connect to nrg.cs.uc.ac.uk
        s.connect(("128.16.66.166", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    @property
    def connected(self):
        return self.__connected

    def send(self, msg):
        send_bytes = pickle.dumps(msg)
        lenbytes = len(send_bytes).to_bytes(2, byteorder='big')
        self.__sock.send(lenbytes + send_bytes)

    def send_maze(self, maze):
        msg = ["maze", maze]
        self.send(msg)

    def check_for_messages(self, now):
        rd, wd, ed = select.select([self.__sock],[],[],0)
        if not rd:
            pass
        else:
            recv_bytes = self.__sock.recv(10000)
            self.__recv_buf += recv_bytes  # concat onto whatever is left from prev receive
            recv_len = int.from_bytes(self.__recv_buf[0:2], byteorder='big')
            while (len(self.__recv_buf) - 2 >= recv_len):
                self.parse_msg(self.__recv_buf[2:recv_len+2])
                self.__recv_buf = self.__recv_buf[recv_len+2:]
                if len(self.__recv_buf) > 2:
                    recv_len = int.from_bytes(self.__recv_buf[0:2], byteorder='big')
                    
        
    def parse_msg(self, buf):
        msg = pickle.loads(buf)
        if msg[0] == "maze":
            maze = msg[1]
            self.__controller.received_maze(maze)
        elif msg[0] == "newpacman":
            #A pacman has arrived message
            self.foreign_pacman_arrived(msg[1])
        elif msg[0] == "pacmanleft":
            #A pacman has left message
            self.foreign_pacman_left(msg[1])
        elif msg[0] == "pacmandied":
            #A pacman has left message
            self.foreign_pacman_died(msg[1])
        elif msg[0] == "pacmanhome":
            #Pacman go home!
            self.pacman_go_home(msg[1])
        elif msg[0] == "pacman":
            #A pacman update message
            self.pacman_update(msg[1])
        elif msg[0] == "ghost":
            #A ghost update message
            self.ghost_update(msg[1])
        elif msg[0] == "ghosteaten":
            #The foreign pacman ate our ghost!
            self.foreign_pacman_ate_ghost(msg[1])
        elif msg[0] == "eat":
            #A food update message
            self.eat(msg[1])
        elif msg[0] == "score":
            #A score update message
            self.score_update(msg[1])
        elif msg[0] == "status":
            #A status update message
            self.status_update(msg[1])
        else:
            print("Unknown message type: ", msg[0])
        

    def foreign_pacman_arrived(self, msg):
        #print("received pacman_arrived")
        self.__controller.foreign_pacman_arrived()

    def send_foreign_pacman_arrived(self):
        #print("send pacman_arrived")
        payload = []
        msg = ["newpacman", payload]
        self.send(msg)

    def foreign_pacman_left(self, msg):
        #print("received pacman_left")
        self.__controller.foreign_pacman_left()

    def send_foreign_pacman_left(self):
        print("send pacman_left")
        payload = []
        msg = ["pacmanleft", payload]
        self.send(msg)

    def foreign_pacman_died(self, msg):
        #print("received pacman_died")
        self.__controller.foreign_pacman_died()

    def send_foreign_pacman_died(self):
        #print("send pacman_died")
        payload = []
        msg = ["pacmandied", payload]
        self.send(msg)

    def pacman_go_home(self, msg):
        self.__controller.pacman_go_home()

    def send_pacman_go_home(self):
        print("send pacman_go_home")
        payload = []
        msg = ["pacmanhome", payload]
        self.send(msg)

    def pacman_update(self, msg):
        #print("received pacman_update")
        pos = msg[0] #position in pixels
        dir = msg[1] #direction enum
        speed = msg[2] 
        self.__controller.foreign_pacman_update(pos, dir, speed)

    def send_pacman_update(self, pos, dir, speed):
        #print("send pacman_update")
        payload = [pos, dir, speed]
        msg = ["pacman", payload]
        self.send(msg)

    def ghost_update(self, msg):
        #print("received ghost_update")
        ghostnum = msg[0]
        pos = msg[1] #position in pixels
        dirn = msg[2] #direction enum
        speed = msg[3] 
        mode = msg[4] 
        self.__controller.remote_ghost_update(ghostnum, pos, dirn, speed, mode)

    def send_ghost_update(self, ghostnum, pos, dirn, speed, mode):
        #print("send ghost_update")
        payload = [ghostnum, pos, dirn, speed, mode]
        msg = ["ghost", payload]
        self.send(msg)

    def send_foreign_pacman_ate_ghost(self, ghostnum):
        payload = [ghostnum] # probably shouldn't be a list - inefficient
        msg = ["ghosteaten", payload]
        self.send(msg)

    def foreign_pacman_ate_ghost(self, msg):
        ghostnum = msg[0]
        self.__controller.foreign_pacman_ate_ghost(ghostnum)
        
    def eat(self, msg):
        pos = msg[0]
        is_foreign = msg[1]
        is_powerpill = msg[2]
        if is_foreign:
            # A foreign pacman ate food on our screen
            self.__controller.foreign_eat(pos, is_powerpill)
        else:
            # Food was eaten on the remote screen
            self.__controller.remote_eat(pos, is_powerpill)

    def send_eat(self, pos, is_foreign, is_powerpill):
        payload = [pos, is_foreign, is_powerpill]
        msg = ["eat", payload]
        self.send(msg)

    def score_update(self, msg):
        score = msg[0]
        self.__controller.update_remote_score(score)

    def send_score_update(self, score):
        payload = [score] # probably shouldn't be a list
        msg = ["score", payload]
        self.send(msg)
        
    def status_update(self, msg):
        status = msg[0]
        self.__controller.remote_status_update(status)

    def send_status_update(self, status):
        payload = [status] # probably shouldn't be a list
        msg = ["status", payload]
        self.send(msg)
        
