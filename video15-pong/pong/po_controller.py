# Simple Pong Game.  Mark Handley, UCL, 2019

from tkinter import *
from po_model import Model
from po_view import View
from po_settings import Direction
from po_network import Network
from sys import argv
from getopt import getopt, GetoptError
import time

class Controller():
    def __init__(self):
        self.parse_args(argv)
        self.root = Tk();
        self.windowsystem = self.root.call('tk', 'windowingsystem')
        self.views = []
        self.root.bind_all('<KeyPress>', self.keypress)
        self.root.bind_all('<KeyRelease>', self.keyrelease)
        self.running = True
        self.scores = [0,0]
        self.bats = []
        self.ball = None
        self.net = Network(self)
        self.local_ip = self.net.get_local_ip_addr()        
        self.model = Model(self);
        self.add_view(View(self.root, self))
        self.init_net()
        self.model.activate(self.p2, self.autoplay)

    def parse_args(self, argv):
        try:
            if "pong.py" in argv[0]:
                opts, args = getopt(argv[1:], "sac:l:d:", ["player2", "autoplay", "connect=", "loss=", "delay="])
            else:
                opts, args = getopt(argv, "sac:l:d:", ["player2", "autoplay", "connect=", "loss=", "delay="])
        except GetoptError:
            self.usage()
        self.p2 = False
        self.autoplay = False
        self.connect_to = "127.0.0.1"
        self.lossrate = 0
        self.latency = 0
        for opt, arg in opts:
            if opt in ("-s", "--player2"):
                # there's not really a server and a client, but we need to decide
                # ports, and they can't be the same on localhost, so
                # this gives us an asymmetry we can use to determine P1 vs P2
                self.p2 = True
            elif opt in ("-a", "--autoplay"):
                self.autoplay = True
            elif opt in ("-c", "--connect"):
                self.connect_to = arg
            elif opt in ("-l", "--loss"):
                self.lossrate = arg
            elif opt in ("-d", "--delay"):
                self.latency = arg
            else:
                self.usage()
        try:
            self.lossrate = int(self.lossrate)
            if self.lossrate < 0 or self.lossrate > 100:
                sys.exit(2)
            if self.lossrate > 0:
                print("Emulating", self.lossrate, "% packet loss")
        except:
            print(e)
            print("Loss rate must be an integer percentage between 0 and 100%")
            sys.exit(2)
            
        try:
            self.latency = int(self.latency)
            if self.latency < 0 or self.latency > 1000:
                sys.exit(2)
            if self.latency > 0:
                print("Emulating", self.latency, "ms one-way network latency")
        except:
            print("Latency must be an integer between 0ms and 1000ms")
            sys.exit(2)
            
        if self.p2:
            self.local_port = 9872
            self.remote_port = 9873
            print("P2 mode, connecting to", self.connect_to, "port", self.remote_port)
        else:
            self.local_port = 9873
            self.remote_port = 9872
            print("P1 mode, connecting to", self.connect_to, "port", self.remote_port)

    def init_net(self):
        self.net.peer(self.local_port, self.connect_to, self.remote_port, \
                          self.lossrate, self.latency)

    def usage(self):
        print("pong.py [-s | --player2] [-c <ip address> | --connect=<ip address>] \n          [-l <lossrate> | --loss=<lossrate>] [-d <delay in ms> | --delay=<delay in ms>]")
        sys.exit(2)            

    def register_bat(self, obj):
        self.bats.append(obj)
        for view in self.views:
            view.register_bat(obj)

    def register_ball(self, ball):
        self.ball = ball
        for view in self.views:
            view.register_ball(ball)

    def rotate_scene(self):
        for view in self.views:
            view.rotate_view()

    def add_view(self, view):
        self.views.append(view)
        view.register_ball(self.ball)
        for obj in self.bats:
            view.register_bat(obj)

    #handle communication updates
    def update_bat(self, bat):
        self.net.send_bat_update(bat.y, bat.velocity)

    def remote_bat_update(self, y, vy):
        self.model.remote_bat_update(y, vy)

    def update_ball(self, ball):
        self.net.send_ball_update(ball.position, ball.velocity)

    def remote_ball_update(self, pos, velocity):
        self.model.remote_ball_update(pos, velocity)

    #some helper functions to hide the controller implementation from
    #the model and the controller
    def update_scores(self, scores):
        self.scores = scores

    def get_scores(self):
        return self.scores
        
    def game_over(self):
        for view in self.views:
            view.game_over()
        
    def keypress(self, event):
        if event.char == 's' or event.keysym == 'Up':
            self.current_keysym = event.keysym
            self.model.move_bat(Direction.UP)
        elif event.char == 'd' or event.keysym == 'Down':
            self.current_keysym = event.keysym
            self.model.move_bat(Direction.DOWN)
        elif event.char == 'q':
            self.running = False
        elif event.char == 'r':
            for view in self.views:
                view.clear_messages()
            self.model.restart()

    def keyrelease(self, event):
        # only cancel the move if the keyup is the same as the most recent keydown
        # avoids problems when overlap between keypresses
        if event.keysym == 'r':
            return
        if self.current_keysym == event.keysym:
            self.model.move_bat(Direction.NONE)

    def run(self):
        i = 0
        last_time = time.time()
        while self.running:
            now = time.time()
            self.net.check_for_messages(now)
            self.model.update()
            for view in self.views:
                view.update()
            self.root.update()
            i = i + 1
            if i == 60:
                t = time.time()
                elapsed = t - last_time
                last_time = t
                fps = 60/elapsed
                i = 0;
        self.root.destroy()
