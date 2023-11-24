# Networked Pacman Game.  Mark Handley, UCL, 2018

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
    def __init__(self, canvas, zoom):
        self.canvas = canvas
        self.items = []
        self.zoom = zoom
        self.div = 2//zoom
        self.x = 0
        self.y = 0

    def moveto(self, x, y):
        x = x//self.div
        y = y//self.div
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
    def __init__(self, canvas, pacman, pngs, dying_pngs, zoom):
        GameObjectView.__init__(self, canvas, zoom)
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
        x, y = self.pacman.position
        if self.__dying:
            if self.__pngnum >= len(self.__dying_pngs):
                return
            self.moveto(0, 0)
            image = self.canvas.create_image(L_OFF, T_OFF, image=self.__dying_pngs[self.__pngnum], anchor="c")
        else:
            self.moveto(0, 0)
            d = self.pointing_direction
            image = self.canvas.create_image(L_OFF, T_OFF, image=self.__pngs[d][self.__pngnum], anchor="c")
        self.items.append(image)
        self.moveto(x, y)

    def redraw(self, time_now, root):
        #if not self.pacman.on_our_screen:
        #    #print("our pacman on their screen, status", self.pacman.status)
        #    self.cleanup()
        #    return
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
    def __init__(self, canvas, ghost, pngs, eyes_pngs, scared_pngs, mainview, zoom):
        GameObjectView.__init__(self, canvas, zoom)
        self.ghost = ghost
        self.__mainview = mainview
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
        else:
            png = self.__eyes_pngs[self.ghost.direction]
            print("Fix:", self.ghost.mode)
            assert(False)
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
    def __init__(self, canvas, coords, food_png, zoom):
        x, y = coords  # x and y coords in grid squares, not pixels
        self.canvas = canvas
        gridsize = (GRID_SIZE * zoom)//2
        self.x = L_OFF + x * gridsize
        self.y = T_OFF + y * gridsize
        self.image = self.canvas.create_image(self.x, self.y, image=food_png, anchor="c")

    def eat(self):
        self.canvas.delete(self.image)

    def cleanup(self):
        self.eat()
            
class View(Frame):
    def __init__(self, root, controller, name, zoom):
        self.zoom = zoom
        self.controller = controller
        self.name = name
        root.wm_title("PacMan")
        self.windowsystem = root.call('tk', 'windowingsystem')
        self.frame = root
        div = 2//zoom
        self.canvas = Canvas(self.frame, width=(CANVAS_WIDTH-L_OFF)//div+L_OFF, height=CANVAS_HEIGHT//div, bg="black")
        self.canvas.pack(side = LEFT, fill=BOTH, expand=FALSE)
        self.__init_fonts()
        self.__init_score()
        self.__messages_displayed = [False, False]
        self.__text = [None, None]
        self.mylives = 0
        self.mylives_pacmen = []
        self.theirlives = 0
        self.theirlives_pacmen = []
        self.__ghost_views = []
        self.__pacman_views = []
        self.__food = {}  # we use a dict to store food, indexed by grid coordinates
        self.__powerpills = {} # also a dict
        self.__tags = []
        self.audio = Audio()

        #Load all the images from files
        self.__pacman_pngs = [[],[]]
        for i in range(0, 3):
            self.__pacman_pngs[0].append(PhotoImage(file = './assets/pacman' + str(i) + '.gif').zoom(self.zoom))
            self.__pacman_pngs[1].append(PhotoImage(file = './assets/pacman' + str(i) + 'p.gif').zoom(self.zoom))
        self.__pacman_dying_pngs = [[],[]]
        for i in range(1, 11):
            self.__pacman_dying_pngs[0].append(PhotoImage(file = './assets/pacman_dying' + str(i) + '.gif').zoom(self.zoom))
            self.__pacman_dying_pngs[1].append(PhotoImage(file = './assets/pacman_dying' + str(i) + 'p.gif').zoom(self.zoom))
        self.__ghost_left_pngs = []
        for i in range(0, 4):
            self.__ghost_left_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + '.gif').zoom(self.zoom))
        self.__ghost_up_pngs = []
        for i in range(0, 4):
            self.__ghost_up_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + 'up.gif').zoom(self.zoom))
        self.__ghost_down_pngs = []
        for i in range(0, 4):
            self.__ghost_down_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + 'down.gif').zoom(self.zoom))
        self.__ghost_scared_pngs = []
        self.__ghost_scared_pngs.append(PhotoImage(file = './assets/ghostscared.gif').zoom(self.zoom))
        self.__ghost_scared_pngs.append(PhotoImage(file = './assets/ghostscaredending.gif').zoom(self.zoom))
        self.__ghost_eyes_pngs = []
        for i in range(0,4):
            self.__ghost_eyes_pngs.append(PhotoImage(file = './assets/eyes' + str(i) + '.gif').zoom(self.zoom))
            
        self.__food_png = PhotoImage(file = './assets/food.gif').zoom(self.zoom)
        self.__powerpill_png = PhotoImage(file = './assets/powerpill.gif').zoom(self.zoom)

    def __str__(self):
        return "view-"+self.name

    def __init_fonts(self):
        # fonts are global, so don't set font in small window
        if self.name == "local":
            self.__bigfont = font.nametofont("TkDefaultFont")
            self.__bigfont.configure(size=24*self.zoom)
            self.__scorefont = font.nametofont("TkDefaultFont")
            self.__scorefont.configure(size=10*self.zoom)

    def __init_score(self):
        if self.name == "local":
            self.__score_text = self.canvas.create_text(5, 5, anchor="nw")
            self.canvas.itemconfig(self.__score_text, text="", font=self.__scorefont, fill="white")

    def update_maze(self, maze):
        s = ""
        y = 0
        for tag in self.__tags:
            self.canvas.delete(tag)
        self.__tags.clear()
        gridsize = (GRID_SIZE *self.zoom)//2
        for row in maze:
            for x in range(0, len(row)//3):
                c = row[x*3:(x+1)*3]
                sx = x + 0.5  # x and y give the middle of the square,
                              # so sx, sy give the top left corner
                sy = y - 0.5
                if c == " /-":
                    tag = self.canvas.create_arc(L_OFF + x * gridsize,
                                                  T_OFF + y * gridsize,
                                                  L_OFF + (x+1) * gridsize,
                                                  T_OFF + (y+1) * gridsize,
                                                  start=90, extent=90, style=ARC, width=2,
                                                  outline = "blue")
                    s += " /-"
                elif c == "-/ ":
                    tag = self.canvas.create_arc(L_OFF + (x-1) * gridsize,
                                                  T_OFF + (y-1) * gridsize,
                                                  L_OFF + x * gridsize,
                                                  T_OFF + y * gridsize,
                                                  start=270, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += "-/ "
                elif c == "---":
                    tag = self.canvas.create_line(L_OFF + (x-0.5) * gridsize,
                                                  T_OFF + y * gridsize,
                                                  L_OFF + (x+0.5) * gridsize,
                                                  T_OFF + y * gridsize,
                                                  width = 2, fill= "blue")
                    s += "---"
                elif c == "-\\ ":
                    tag = self.canvas.create_arc(L_OFF + (x-1) * gridsize,
                                                  T_OFF + y * gridsize,
                                                  L_OFF + x * gridsize,
                                                  T_OFF + (y+1) * gridsize,
                                                  start=0, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += "-\\ "
                elif c == " \\-":
                    tag = self.canvas.create_arc(L_OFF + x * gridsize,
                                                  T_OFF + (y-1) * gridsize,
                                                  L_OFF + (x+1) * gridsize,
                                                  T_OFF + y * gridsize,
                                                  start=180, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += " \\-"
                elif c == " | ":
                    tag = self.canvas.create_line(L_OFF + x * gridsize,
                                                  T_OFF + (y-0.5) * gridsize,
                                                  L_OFF + x * gridsize,
                                                  T_OFF + (y+0.5) * gridsize,
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

    def register_pacman(self, pacman_model):
        if pacman_model.name == "Pacman1":
            ix = 0
        else:
            ix = 1
        self.__pacman_views.append(PacmanView(self.canvas, pacman_model, self.__pacman_pngs[ix], self.__pacman_dying_pngs[ix], self.zoom))

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
        self.__ghost_views.append(GhostView(self.canvas, ghost_model, pngs, self.__ghost_eyes_pngs, self.__ghost_scared_pngs, self, self.zoom))

    def unregister_ghosts(self):
        for ghost in self.__ghost_views:
            ghost.cleanup()
        self.__ghost_views.clear()

    def register_food(self, coord_list):
        for coords in coord_list:
            food = Food(self.canvas, coords, self.__food_png, self.zoom)
            self.__food[coords] = food

    def register_powerpills(self, coord_list):
        for coords in coord_list:
            # we use a Food object with a powerpill image
            powerpill = Food(self.canvas, coords, self.__powerpill_png, self.zoom)
            self.__powerpills[coords] = powerpill

    def eat(self, coords, is_powerpill):
        if is_powerpill:
            self.eat_powerpill(coords)
        else:
            self.eat_food(coords)

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
        if self.name == "remote":
            return
        myscore, theirscore = self.controller.get_scores()
        self.canvas.itemconfig(self.__score_text, text="Level: "
                               + str(self.controller.get_level())
                               + "  Player 1: " + str(myscore)
                               + "  Player 2: " + str(theirscore),
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
        mylives, theirlives = self.controller.get_lives()
        if mylives != self.mylives:
            self.mylives = mylives
            for pacman_view in self.mylives_pacmen:
                pacman_view.cleanup()
            self.mylives_pacmen.clear()
            y = GRID_SIZE * 32  # 16 rows down is where we show the lives remaining
            life_pngs = [self.__pacman_pngs[0][2]]
            for i in range(0, self.mylives - 1):
                x = 2 * GRID_SIZE * (i + 1)
                dummy = DummyPacman(x, y)
                self.mylives_pacmen.append(PacmanView(self.canvas, dummy, life_pngs, [], self.zoom))
        if theirlives != self.theirlives:
            self.theirlives = theirlives
            for pacman_view in self.theirlives_pacmen:
                pacman_view.cleanup()
            self.theirlives_pacmen.clear()
            y = (GRID_SIZE + 1) * 32  # 16 rows down is where we show the lives remaining
            life_pngs = [self.__pacman_pngs[1][2]]
            for i in range(0, self.theirlives - 1):
                x = 2 * GRID_SIZE * (i + 1)
                dummy = DummyPacman(x, y)
                self.theirlives_pacmen.append(PacmanView(self.canvas, dummy, life_pngs, [], self.zoom))

    def died(self, pacman, clear_ghosts):
        for view in self.__pacman_views:
            if view.pacman == pacman:
                view.died()
                self.audio.play(2)
        if clear_ghosts:
            for ghost in self.__ghost_views:
                ghost.cleanup()
            self.__ghost_views.clear()

    def reset_level(self):
        self.clear_messages()
        self.audio.play(1)

    def game_over(self):
        self.display_msg_line1("GAME OVER!")
        self.display_msg_line2("Press r to play again.")

    def display_msg(self, msg):
        self.clear_messages()
        self.display_msg_line1(msg)

    def display_msg_line1(self, msg):
        x = 14 * GRID_SIZE + L_OFF
        y = 11 * GRID_SIZE + T_OFF
        self.__text[0] = self.canvas.create_text(x, y, anchor="c")
        self.canvas.itemconfig(self.__text[0], text=msg, font=self.__bigfont, fill="white")
        self.__messages_displayed[0] = True

    def display_msg_line2(self, msg):
        x = 14 * GRID_SIZE + L_OFF
        y = 17 * GRID_SIZE + T_OFF
        self.__text[1] = self.canvas.create_text(x, y, anchor="c")
        self.canvas.itemconfig(self.__text[1], text=msg, font=self.__scorefont, fill="white")
        self.__messages_displayed[1] = True

    def clear_messages(self):
        for line in range(0, 2):
            if self.__messages_displayed[line]:
                self.canvas.delete(self.__text[line])
            self.__messages_displayed[line] = False

    def update(self, now):
        for view in self.__pacman_views:
            view.redraw(now, self.frame)
        for view in self.__ghost_views:
            view.redraw(now, self.frame)
        self.display_score()

