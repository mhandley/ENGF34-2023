import socket
import sys
import pickle
import select
from random import Random
from time import sleep, time

MSG_INIT = 1
MSG_INITACK = 2
MSG_BAT = 3
MSG_BALL = 4

class Network():
    def __init__(self, controller):
        self.__controller = controller
        self.__server = False
        self.__connected = False
        self.rand = Random()
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as err: 
            print("socket creation failed with error %s" %(err))
            sys.exit()
        self.__recv_buf = bytes()
        self.get_local_ip_addr()
        self.queue = []

    def peer(self, my_port, their_ip, their_port, lossrate, latency):
        self.use_udp = True
        self.got_init = False
        self.__sock.bind(('', my_port))
        self.dst = (their_ip, their_port)
        self.lossrate = lossrate/100
        self.latency = latency
        while True:
            rd, wd, ed = select.select([self.__sock],[],[],1)
            if self.__sock in rd:
                recv_bytes, addr = self.__sock.recvfrom(10000)
                recv_len = int.from_bytes(recv_bytes[0:2], byteorder='big')
                msg_type = int.from_bytes(recv_bytes[2:3], byteorder='big')
                payload = recv_bytes[3:]
                if msg_type == MSG_INIT and recv_len == 0:
                    self.got_init = True
                elif msg_type == MSG_INITACK and recv_len == 0:
                    return
                elif self.got_init and (msg_type == MSG_BAT or msg_type == MSG_BALL):
                    return
                else:
                    print("bad handshake")
                    sys.exit()
            if not self.got_init:
                #print("sending INIT")
                self.send(MSG_INIT, None)
            else:
                #print("sending INITACK")
                self.send(MSG_INITACK, None)
                

    def get_local_ip_addr(self):
        # ugly hacky way to find our IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # connect to nrg.cs.uc.ac.uk
        try:
            s.connect(("128.16.66.166", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "127.0.0.1"
        return ip

    @property
    def connected(self):
        return self.__connected

    def send(self, msgtype, payload):
        r = self.rand.random()
        if r < self.lossrate:
            print("drop")
            return
        type_byte = msgtype.to_bytes(1, byteorder='big')
        if payload:
            lenbytes = len(payload).to_bytes(2, byteorder='big')
            packet = lenbytes + type_byte + payload
        else:
            lenbytes = int(0).to_bytes(2, byteorder='big')
            packet = lenbytes + type_byte

        if msgtype != MSG_INIT and msgtype != MSG_INITACK and self.latency != 0:
            self.queue.append((time(), packet))
        else:
            self.__sock.sendto(packet, self.dst)

    def check_queue(self, now):
        while True:
            if len(self.queue) == 0:
                return
            first, pkt = self.queue[0]
            if now - first > 0.05:
                self.__sock.sendto(pkt, self.dst)
                self.queue.pop(0)
            else:
                return

    def check_for_messages(self, now):
        self.check_queue(now)
        while True:
            rd, wd, ed = select.select([self.__sock],[],[],0)
            if not rd:
                return
            else:
                try:
                    recv_bytes, addr = self.__sock.recvfrom(10000)
                except ConnectionResetError as e:
                    print("Remote game has quit: ", e)
                    sys.exit()
                recv_len = int.from_bytes(recv_bytes[0:2], byteorder='big')
                recv_msg = recv_bytes[2:]
                self.parse_msg(recv_msg)
                    
    def parse_msg(self, recv_msg):
        msg_type = int.from_bytes(recv_msg[0:1], byteorder='big')
        payload = recv_msg[1:]
        if msg_type == MSG_BAT:
            self.bat_update(payload)
        elif msg_type == MSG_BALL:
            self.ball_update(payload)
        
    def bat_update(self, msg):
        y = int.from_bytes(msg[0:2], byteorder='big')
        vy = int.from_bytes(msg[2:4], byteorder='big', signed=True)
        self.__controller.remote_bat_update(y, vy)

    def send_bat_update(self, y, vy):
        msg = y.to_bytes(2, byteorder='big') \
            + vy.to_bytes(2, byteorder='big', signed=True)
        self.send(MSG_BAT, msg)
        
    def ball_update(self, msg):
        x = int.from_bytes(msg[0:2], byteorder='big', signed=True)
        y = int.from_bytes(msg[2:4], byteorder='big', signed=True)
        ivx = int.from_bytes(msg[4:6], byteorder='big', signed=True)
        ivy = int.from_bytes(msg[6:8], byteorder='big', signed=True)
        vx = ivx/1024 #convert from fixed point representation to float
        vy = ivy/1024
        self.__controller.remote_ball_update((x,y), (vx,vy))

    def send_ball_update(self, pos, velocity):
        vx, vy = velocity
        ivx = int(vx*1024) #use fixed point representation
        ivy = int(vy*1024) #use fixed point representation
        msg = pos[0].to_bytes(2, byteorder='big', signed=True) \
            + pos[1].to_bytes(2, byteorder='big', signed=True) \
            + ivx.to_bytes(2, byteorder='big', signed=True) \
            + ivy.to_bytes(2, byteorder='big', signed=True)
        self.send(MSG_BALL, msg)

    def score_update(self, msg):
        score = msg[0]
        self.__controller.update_remote_score(score)

    def send_score_update(self, score):
        payload = [score] # probably shouldn't be a list
        msg = ["score", payload]
        self.send(msg)
        
