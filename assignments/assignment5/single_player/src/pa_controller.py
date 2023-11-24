# PacMan Game.  Mark Handley, UCL, 2018

from tkinter import *
from pa_model import Model
from pa_view import View
from pa_settings import Direction
import time

class Controller():
    def __init__(self):
        self.root = Tk();
        self.windowsystem = self.root.call('tk', 'windowingsystem')
        self.views = []
        self.root.bind_all('<KeyPress>', self.keypress)
        self.root.bind_all('<KeyRelease>', self.keyrelease)
        self.running = True
        self.score = -1
        self.level = -1
        self.ghosts = []
        self.pacmen = []
        self.food_coords = []
        self.model = Model(self);
        self.add_view(View(self.root, self))
        self.model.activate()

    def unregister_objects(self):
        self.ghosts.clear()
        for view in self.views:
            view.unregister_objects()

    def register_pacman(self, pacman):
        self.pacmen.append(pacman)
        for view in self.views:
            view.register_pacman(pacman)

    def unregister_pacman(self, pacman):
        self.pacmen.remove(pacman)
        for view in self.views:
            view.unregister_pacman(pacman)

    def register_ghost(self, ghost):
        self.ghosts.append(ghost)
        for view in self.views:
            view.register_ghost(ghost)

    def register_food(self, coordlist):
        self.food_coords = coordlist
        for view in self.views:
            view.register_food(coordlist)

    def register_powerpills(self, coordlist):
        self.powerpill_coords = coordlist
        for view in self.views:
            view.register_powerpills(coordlist)

    def eat_food(self, coords):
        self.food_coords.remove(coords)
        for view in self.views:
            view.eat_food(coords)

    def eat_powerpill(self, coords):
        self.powerpill_coords.remove(coords)
        for view in self.views:
            view.eat_powerpill(coords)

    def ghost_died(self):
        for view in self.views:
            view.ghost_died()

    def add_view(self, view):
        self.views.append(view)
        for pacman in self.pacmen:
            view.register_pacman(pacman)
        for ghost in self.ghosts:
            view.register_ghost(ghost)
        view.register_food(self.food_coords)

    #some helper functions to hide the controller implementation from
    #the model and the controller
    def update_score(self, score):
        self.score = score

    def get_score(self):
        return self.score

    def update_maze(self, maze):
        for view in self.views:
            view.update_maze(maze)
        
    def update_level(self, level):
        self.level = level
        for view in self.views:
            view.reset_level()

    def get_level(self):
        return self.level

    def update_lives(self, lives):
        self.lives = lives

    def get_lives(self):
        return self.lives

    def died(self, pacman):
        for view in self.views:
            view.died(pacman)

    def game_over(self):
        for view in self.views:
            view.game_over()
        
    def keypress(self, event):
        if event.char == 'a' or event.keysym == 'Left':
            self.model.key_press(Direction.LEFT)
        elif event.char == 'w' or event.keysym == 'Up':
            self.model.key_press(Direction.UP)
        elif event.char == 's' or event.keysym == 'Down':
            self.model.key_press(Direction.DOWN)
        elif event.char == 'd' or event.keysym == 'Right':
            self.model.key_press(Direction.RIGHT)
        elif event.char == 'q':
            self.running = False
        elif event.char == 'r':
            for view in self.views:
                view.clear_messages()
            self.model.restart()

    def keyrelease(self, event):
        if event.char == 'a' or event.keysym == 'Left':
            self.model.key_release()
        elif event.char == 'w' or event.keysym == 'Up':
            self.model.key_release()
        elif event.char == 's' or event.keysym == 'Down':
            self.model.key_release()
        elif event.char == 'd' or event.keysym == 'Right':
            self.model.key_release()

    def run(self):
        while self.running:
            now = time.time()
            self.model.update(now)
            for view in self.views:
                view.update(now)
            self.root.update()
        self.root.destroy()
