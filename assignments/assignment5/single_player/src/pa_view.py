# Simple Frogger Game.  Mark Handley, UCL, 2018

from tkinter import *
from tkinter import font
import time
from pa_settings import CANVAS_WIDTH, CANVAS_HEIGHT, GRID_SIZE, Direction, PARTIAL_UPDATE
from pa_audio import Audio
from pa_model import GhostMode

L_OFF = 50
T_OFF = 50

'''GameObjectView is a generic view of a game object.  All it does is
   handle moving of the object - it just saves replicating this code into
   PacmanView, GhostView, etc.  Everything else needs to be handled by the
   subclasses themselves.'''

class GameObjectView():
    def __init__(self, canvas):
        self.canvas = canvas
        self.items = []
        self.x = 0
        self.y = 0

    def moveto(self, x, y):
        for item in self.items:
            self.canvas.move(item, x - self.x, y - self.y)
        self.x = x
        self.y = y

    def cleanup(self):
        for item in self.items:
            self.canvas.delete(item)

def get_tuple(x):
    if type(x) is tuple:
        return x
    elif type(x) is str:
        lst = x.split(" ")
        t = (int(lst[0]), int(lst[1]), int(lst[2]))
        return t
    
class PacmanView(GameObjectView):
    def __init__(self, canvas, pacman, pngs, dying_pngs):
        GameObjectView.__init__(self, canvas)
        self.pacman = pacman
        self.__pngs = [[],[],[],[]]
        self.__dying_pngs = dying_pngs
        self.__pngs[Direction.LEFT] = pngs
        self.pointing_direction = Direction.LEFT

        # rotate the image to create a PacMan facing each direction
        prevlist = pngs
        for dir in [Direction.UP, Direction.RIGHT, Direction.DOWN]:
            pnglist = []
            for image in prevlist:
                newimage = self.__rotate_image(image, Direction.RIGHT)
                pnglist.append(newimage)
            self.__pngs[dir] = pnglist
            prevlist = pnglist
            
        self.__pngnum = 0
        self.__pngcounter = 0
        self.__last_change = 0
        self.__dying = False
        self.draw()

    def __rotate_image(self, img, dir):
        w, h = img.width(), img.height()
        if dir in [Direction.LEFT, Direction.RIGHT]:
            newimg = PhotoImage(width=h, height=w)
        else: # 180 degree
            newimg = PhotoImage(width=w, height=h)
        for x in range(w):
            for y in range(h):
                rgb = '#%02x%02x%02x' % get_tuple(img.get(x, y))
                if dir == Direction.RIGHT: # 90 degrees
                    newimg.put(rgb, (h-y,x))
                elif dir == Direction.LEFT: # -90 or 270 degrees
                    newimg.put(rgb, (y,w-x))
                else: # 180 degrees
                    newimg.put(rgb, (w-x,h-y))
        return newimg

    def draw(self):
        if self.__dying:
            if self.__pngnum >= len(self.__dying_pngs):
                return
            x, y = self.pacman.position
            image = self.canvas.create_image(L_OFF + x, T_OFF + y, image=self.__dying_pngs[self.__pngnum], anchor="c")
            self.items.append(image)
        else:
            x, y = self.pacman.position
            self.moveto(0, 0)
            d = self.pointing_direction
            image = self.canvas.create_image(L_OFF, T_OFF, image=self.__pngs[d][self.__pngnum], anchor="c")
            self.items.append(image)
            self.moveto(x, y)

    def redraw(self, time_now, root):
        if time_now - self.__last_change > 0.1:
            self.__last_change = time_now
            self.__next_png()
            self.cleanup()
            self.draw()
        else:
            x, y = self.pacman.position
            self.moveto(x, y)
        if PARTIAL_UPDATE:
            root.update_idletasks()

    def __next_png(self):
        if self.__dying:
            self.__pngnum = self.__pngnum + 1
            return
        if self.pacman.speed == 0:
            # Pacman stops with his mouth open
            self.__pngnum = 2
        else:
            self.__pngcounter = (self.__pngcounter + 1) % 4
            self.__pngnum = self.__pngcounter
            if self.__pngcounter == 3:
                self.__pngnum = 1
            self.pointing_direction = self.pacman.direction

    def died(self):
        self.pointing_direction = Direction.UP
        self.__pngcounter = 2
        self.__pngnum = -1
        self.__dying = True
        self.__last_change = 0
        #self.redraw(time.time())
            
class DummyPacman():
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.direction = Direction.LEFT

    @property
    def position(self):
        return (self.__x, self.__y)
    

class GhostView(GameObjectView):
    def __init__(self, canvas, ghost, pngs, eyes_pngs, scared_pngs):
        GameObjectView.__init__(self, canvas)
        self.ghost = ghost
        self.__pngs = pngs
        self.__eyes_pngs = eyes_pngs
        self.__scared_pngs = scared_pngs
        self.__prev_direction = Direction.LEFT
        self.__prev_mode = self.ghost.mode
        self.draw()

    def draw(self):
        x,y = self.ghost.position
        self.moveto(0, 0)
        if self.ghost.mode == GhostMode.CHASE:
            png = self.__pngs[self.ghost.direction]
        elif self.ghost.mode == GhostMode.FRIGHTEN:
            if self.ghost.frighten_ending:
                png = self.__scared_pngs[1]
            else:
                png = self.__scared_pngs[0]
        elif self.ghost.mode == GhostMode.EYES:
            png = self.__eyes_pngs[self.ghost.direction]
        image = self.canvas.create_image(L_OFF, T_OFF, image=png, anchor="c")
        self.items.append(image)
        self.moveto(x, y)
        self.__prev_mode = self.ghost.mode

    def redraw(self, time_now, root):
        if self.ghost.direction == self.__prev_direction \
           and self.ghost.mode == self.__prev_mode:
            x, y = self.ghost.position
            self.moveto(x, y)
        else:
            self.cleanup()
            self.draw()
            self.__prev_direction = self.ghost.direction
        if PARTIAL_UPDATE:
            root.update_idletasks()

class Food():
    def __init__(self, canvas, coords, food_png):
        x, y = coords  # x and y coords in grid squares, not pixels
        self.canvas = canvas
        self.x = L_OFF + x * GRID_SIZE
        self.y = T_OFF + y * GRID_SIZE
        self.image = self.canvas.create_image(self.x, self.y, image=food_png, anchor="c")

    def eat(self):
        self.canvas.delete(self.image)

    def cleanup(self):
        self.eat()
            
class View(Frame):
    def __init__(self, root, controller):
        self.controller = controller
        root.wm_title("PacMan")
        self.windowsystem = root.call('tk', 'windowingsystem')
        self.frame = root
        self.canvas = Canvas(self.frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="black")
        self.canvas.pack(side = LEFT, fill=BOTH, expand=FALSE)
        self.__init_fonts()
        self.__init_score()
        self.__messages_displayed = False
        self.lives = 0
        self.lives_pacmen = []
        self.__ghost_views = []
        self.__pacman_views = []
        self.__food = {}  # we use a dict to store food, indexed by grid coordinates
        self.__powerpills = {} # also a dict
        self.__tags = []
        self.audio = Audio()

        #Load all the images from files
        self.__pacman_pngs = []
        for i in range(0, 3):
            self.__pacman_pngs.append(PhotoImage(file = './assets/pacman' + str(i) + '.gif').zoom(2))
        self.__pacman_dying_pngs = []
        for i in range(1, 11):
            self.__pacman_dying_pngs.append(PhotoImage(file = './assets/pacman_dying' + str(i) + '.gif').zoom(2))
        self.__ghost_left_pngs = []
        for i in range(0, 4):
            self.__ghost_left_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + '.gif').zoom(2))
        self.__ghost_up_pngs = []
        for i in range(0, 4):
            self.__ghost_up_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + 'up.gif').zoom(2))
        self.__ghost_down_pngs = []
        for i in range(0, 4):
            self.__ghost_down_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + 'down.gif').zoom(2))
        self.__ghost_scared_pngs = []
        self.__ghost_scared_pngs.append(PhotoImage(file = './assets/ghostscared.gif').zoom(2))
        self.__ghost_scared_pngs.append(PhotoImage(file = './assets/ghostscaredending.gif').zoom(2))
        self.__ghost_eyes_pngs = []
        for i in range(0,4):
            self.__ghost_eyes_pngs.append(PhotoImage(file = './assets/eyes' + str(i) + '.gif').zoom(2))
            
        self.__food_png = PhotoImage(file = './assets/food.gif').zoom(2)
        self.__powerpill_png = PhotoImage(file = './assets/powerpill.gif').zoom(2)

    def __init_fonts(self):
        self.__bigfont = font.nametofont("TkDefaultFont")
        self.__bigfont.configure(size=48)
        self.__scorefont = font.nametofont("TkDefaultFont")
        self.__scorefont.configure(size=20)

    def __init_score(self):
        self.__score_text = self.canvas.create_text(5, 5, anchor="nw")
        self.canvas.itemconfig(self.__score_text, text="Score:", font=self.__scorefont, fill="white")

    def update_maze(self, maze):
        s = ""
        y = 0
        for tag in self.__tags:
            self.canvas.delete(tag)
        self.__tags.clear()
        for row in maze:
            for x in range(0, len(row)//3):
                c = row[x*3:(x+1)*3]
                sx = x + 0.5  # x and y give the middle of the square,
                              # so sx, sy give the top left corner
                sy = y - 0.5
                if c == " /-":
                    tag = self.canvas.create_arc(L_OFF + x * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  L_OFF + (x+1) * GRID_SIZE,
                                                  T_OFF + (y+1) * GRID_SIZE,
                                                  start=90, extent=90, style=ARC, width=2,
                                                  outline = "blue")
                    s += " /-"
                elif c == "-/ ":
                    tag = self.canvas.create_arc(L_OFF + (x-1) * GRID_SIZE,
                                                  T_OFF + (y-1) * GRID_SIZE,
                                                  L_OFF + x * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  start=270, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += "-/ "
                elif c == "---":
                    tag = self.canvas.create_line(L_OFF + (x-0.5) * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  L_OFF + (x+0.5) * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  width = 2, fill= "blue")
                    s += "---"
                elif c == "-\\ ":
                    tag = self.canvas.create_arc(L_OFF + (x-1) * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  L_OFF + x * GRID_SIZE,
                                                  T_OFF + (y+1) * GRID_SIZE,
                                                  start=0, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += "-\\ "
                elif c == " \\-":
                    tag = self.canvas.create_arc(L_OFF + x * GRID_SIZE,
                                                  T_OFF + (y-1) * GRID_SIZE,
                                                  L_OFF + (x+1) * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  start=180, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += " \\-"
                elif c == " | ":
                    tag = self.canvas.create_line(L_OFF + x * GRID_SIZE,
                                                  T_OFF + (y-0.5) * GRID_SIZE,
                                                  L_OFF + x * GRID_SIZE,
                                                  T_OFF + (y+0.5) * GRID_SIZE,
                                                  width = 2, fill= "blue")
                    s += " | "
                elif c == "   ":
                    s += "   "
                elif c == "###":
                    s += "   "
                elif c == " . ":
                    s += " . "
                elif c == " * ":
                    s += " * "
                elif c == " A ":
                    s += " A "
                elif c == " B ":
                    s += " B "
                else:
                    s += "ERROR>>>" + c + "<<<"
                self.__tags.append(tag)
            s += "\n"
            y += 1
        #print(s)

    def register_pacman(self, pacman_model):
        self.__pacman_views.append(PacmanView(self.canvas, pacman_model, self.__pacman_pngs, self.__pacman_dying_pngs))

    def unregister_pacman(self, pacman_model):
        for view in self.__pacman_views:
            if view.pacman == pacman_model:
                view.cleanup()
            self.__pacman_views.remove(view)
            return

    def register_ghost(self, ghost_model):
        ghostnum = ghost_model.ghostnum
        pngs = []
        pngs.append(self.__ghost_up_pngs[ghostnum])
        pngs.append(self.__ghost_left_pngs[ghostnum])
        pngs.append(self.__reflect_image(self.__ghost_left_pngs[ghostnum]))
        pngs.append(self.__ghost_down_pngs[ghostnum])
        self.__ghost_views.append(GhostView(self.canvas, ghost_model, pngs, self.__ghost_eyes_pngs, self.__ghost_scared_pngs))

    def register_food(self, coord_list):
        for coords in coord_list:
            food = Food(self.canvas, coords, self.__food_png)
            self.__food[coords] = food

    def register_powerpills(self, coord_list):
        for coords in coord_list:
            # we use a Food object with a powerpill image
            powerpill = Food(self.canvas, coords, self.__powerpill_png)
            self.__powerpills[coords] = powerpill

    def eat_food(self, coords):
        food = self.__food[coords]
        food.eat()
        self.__food.pop(coords)
        self.audio.play(0)

    def eat_powerpill(self, coords):
        powerpill = self.__powerpills[coords]
        powerpill.eat()
        self.__powerpills.pop(coords)
        self.audio.play(0)

    def ghost_died(self):
        self.audio.play(3)

    def unregister_objects(self):
        for view in self.__ghost_views:
            view.cleanup()
        self.__ghost_views.clear()
        for coords,food in self.__food.items():
            food.cleanup()
        self.__food.clear()
        for coords,pp in self.__powerpills.items():
            pp.cleanup()
        self.__powerpills.clear()

    def display_score(self):
        self.canvas.itemconfig(self.__score_text, text="Level: "
                               + str(self.controller.get_level())
                               + "  Score: " + str(self.controller.get_score()),
                               font=self.__scorefont)
        self.update_lives()

    def __reflect_image(self, img):
        w, h = img.width(), img.height()
        newimg = PhotoImage(width=w, height=h)
        for x in range(w):
            for y in range(h):
                rgb = '#%02x%02x%02x' % get_tuple(img.get(x, y))
                newimg.put(rgb, (w-x, y))
        return newimg

    def update_lives(self):
        lives = self.controller.get_lives()
        if lives != self.lives:
            self.lives = lives
            for pacman_view in self.lives_pacmen:
                pacman_view.cleanup()
            self.lives_pacmen.clear()
            y = GRID_SIZE * 32  # 16 rows down is where we show the lives remaining
            life_pngs = [self.__pacman_pngs[2]]
            for i in range(0, self.lives - 1):
                x = 2 * GRID_SIZE * (i + 1)
                dummy = DummyPacman(x, y)
                self.lives_pacmen.append(PacmanView(self.canvas, dummy, life_pngs, []))

    def died(self, pacman):
        if len(self.__pacman_views) == 1:
            # only one pacman - normal gameplay
            self.__pacman_views[0].died()
            self.audio.play(2)
            for ghost in self.__ghost_views:
                ghost.cleanup()
            self.__ghost_views.clear()
        else:
            # multiple pacmen - only one dies
            for view in self.__pacman_views:
                if view.pacman == pacman:
                    view.died()
                    self.audio.play(2)

    def reset_level(self):
        self.clear_messages()
        self.audio.play(1)

    def game_over(self):
        x = 14 * GRID_SIZE + L_OFF
        y = 11 * GRID_SIZE + T_OFF
        self.__text = self.canvas.create_text(x, y, anchor="c")
        self.canvas.itemconfig(self.__text, text="GAME OVER!", font=self.__bigfont,
                               fill="white")
        y = 17 * GRID_SIZE + T_OFF
        self.__text2 = self.canvas.create_text(x, y, anchor="c")
        self.canvas.itemconfig(self.__text2, text="Press r to play again.", font=self.__scorefont,
                               fill="white")
        self.__messages_displayed = True

    def clear_messages(self):
        if self.__messages_displayed:
            self.canvas.delete(self.__text)
            self.canvas.delete(self.__text2)
            self.__messages_displayed = False

    def update(self, now):
        for view in self.__pacman_views:
            view.redraw(now, self.frame)
        for view in self.__ghost_views:
            view.redraw(now, self.frame)
        self.display_score()

