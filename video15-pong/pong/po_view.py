# Simple Pong Game.  Mark Handley, UCL, 2019

from tkinter import *
from tkinter import font
import time
from po_settings import CANVAS_WIDTH, CANVAS_HEIGHT, BAT_HEIGHT, BAT_WIDTH, BALL_SIZE

'''GameObjectView is a generic view of a game object.  All it does is
   handle moving of the object - it just saves replicating this code into
   LogView, CarView, etc.  Everything else needs to be handled by the
   subclasses themselves.'''

bitmaps = [
["####",
 "#  #",
 "#  #",
 "#  #",
 "####"],

["   #",
 "   #",
 "   #",
 "   #",
 "   #"],

["####",
 "   #",
 "####",
 "#   ",
 "####"],

["####",
 "   #",
 "####",
 "   #",
 "####"],

["#  #",
 "#  #",
 "####",
 "   #",
 "   #"],

["####",
 "#   ",
 "####",
 "   #",
 "####"],

["####",
 "#   ",
 "####",
 "#  #",
 "####"],

["####",
 "   #",
 "   #",
 "   #",
 "   #"],

["####",
 "#  #",
 "####",
 "#  #",
 "####"],

["####",
 "#   #",
 "####",
 "   #",
 "####"]]

    
class NumView():
    def __init__(self, canvas, pos):
        self.canvas = canvas
        self.value = -1
        self.items = []
        self.x = pos[0]
        self.y = pos[1]

    def set(self, num):
        bitmap = bitmaps[num]
        if num == self.value:
            return
        self.cleanup()
        blob_size = CANVAS_HEIGHT/40
        colour = "grey"
        for col in range(0,4):
            for row in range(0,5):
                if bitmap[row][col] == "#":
                    x = self.x + col*blob_size
                    y = self.y + row*blob_size
                    rect = self.canvas.create_rectangle(x, y, x+blob_size, y + blob_size, fill=colour, outline=colour)
                    self.items.append(rect)                    

    def cleanup(self):
        for item in self.items:
            self.canvas.delete(item)
    
class GameObjectView():
    def __init__(self, canvas, rotated):
        self.canvas = canvas
        self.items = []
        self.x = 0
        self.y = 0
        self.rotated = rotated

    def moveto(self, x, y):
        if self.rotated:
            x, y = self.rotate(x, y)
        for item in self.items:
            self.canvas.move(item, x - self.x, y - self.y)
        self.x = x
        self.y = y

    def cleanup(self):
        for item in self.items:
            self.canvas.delete(item)

    def rotate(self, x, y):
        return CANVAS_WIDTH - x, CANVAS_HEIGHT - y

    
class BatView(GameObjectView):
    def __init__(self, canvas, bat, rotated):
        GameObjectView.__init__(self, canvas, rotated)
        self.bat = bat
        colour = "white"
        if bat.autoplay:
            colour = "yellow"
        if bat.is_remote:
            colour = "grey"
        if self.rotated:
            rect = self.canvas.create_rectangle(0, 0, -BAT_WIDTH, -BAT_HEIGHT, fill=colour, outline=colour)
        else:
            rect = self.canvas.create_rectangle(0, 0, BAT_WIDTH, BAT_HEIGHT, fill=colour, outline=colour)
        self.items.append(rect)

    def redraw(self, time_now, rotated):
        (x,y) = self.bat.position
        self.moveto(x, y)

class BallView(GameObjectView):
    def __init__(self, canvas, ball, rotated):
        GameObjectView.__init__(self, canvas, rotated)
        self.ball = ball
        if self.rotated:
            rect = self.canvas.create_rectangle(0, 0, -BALL_SIZE, -BALL_SIZE, fill="white", outline="white")
        else:
            rect = self.canvas.create_rectangle(0, 0, BALL_SIZE, BALL_SIZE, fill="white", outline="white")
        self.items.append(rect)

    def redraw(self, time_now, rotated):
        (x,y) = self.ball.position
        self.moveto(x, y)


            
class View(Frame):
    def __init__(self, root, controller):
        self.controller = controller
        root.wm_title("Pong")
        self.windowsystem = root.call('tk', 'windowingsystem')
        self.frame = root
        self.canvas = Canvas(self.frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#101010")
        self.canvas.pack(side = LEFT, fill=BOTH, expand=FALSE)
        self.init_fonts()
        self.init_scores()
        self.messages_displayed = False
        self.bat_views = []
        self.rotated = False
        self.init_scenery()

    def rotate_view(self):
        self.rotated = True

    def init_scenery(self):
        # the game objects are aligned so their vertical centres are
        # on the grid boundaries, so the scenery needs to be offset by
        # half a square
        blobs = 20
        blob_size = CANVAS_HEIGHT/(blobs*2)
        x = (CANVAS_WIDTH - blob_size) //2
        y = 0
        for i in range(0,blobs):
            self.canvas.create_rectangle(x, y, x + blob_size, y + blob_size, fill="grey", outline="grey")
            y += 2 * blob_size
        return
            
    def init_fonts(self):
        self.bigfont = font.nametofont("TkDefaultFont")
        self.bigfont.configure(size=48)
        self.scorefont = font.nametofont("TkDefaultFont")
        self.scorefont.configure(size=20)

    def init_scores(self):
        self.scores = (-1,-1)
        mid_x = CANVAS_WIDTH//2
        y = CANVAS_HEIGHT//20
        self.sc1 = NumView(self.canvas, (mid_x - CANVAS_WIDTH/10, y))
        self.sc2 = NumView(self.canvas, (mid_x + CANVAS_WIDTH/40, y))
        #self.score_text = self.canvas.create_text(5, 5, anchor="nw")
        #self.canvas.itemconfig(self.score_text, text="Score:", font=self.scorefont, fill="white")

    def register_bat(self, bat_model):
        self.bat_views.append(BatView(self.canvas, bat_model, self.rotated))

    def register_ball(self, ball_model):
        self.ball_view = BallView(self.canvas, ball_model, self.rotated)

    def unregister_objects(self):
        for view in self.bat_views:
            view.cleanup()
        self.ball_view.cleanup()

    def display_score(self):
        scores = self.controller.get_scores()
        if scores[0] != self.scores[0] or scores[1] != self.scores[1]:
            self.sc1.set(scores[0])
            self.sc2.set(scores[1])
            self.scores = (scores[0], scores[1]) 
            
    def reset_level(self):
        for bat_view in self.bat_views:
            frog_view.cleanup()
        self.clear_messages()

    def game_over(self):
        self.text = self.canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 10, anchor="c")
        self.canvas.itemconfig(self.text, text="GAME OVER!", font=self.bigfont,
                               fill="white")
        self.text2 = self.canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 110, anchor="c")
        self.canvas.itemconfig(self.text2, text="Press r to play again.", font=self.scorefont,
                               fill="white")
        self.messages_displayed = True

    def clear_messages(self):
        if self.messages_displayed:
            self.canvas.delete(self.text)
            self.canvas.delete(self.text2)
            self.messages_displayed = False

    def update(self):
        now = time.time()
        for view in self.bat_views:
            view.redraw(now, self.rotated)
        self.ball_view.redraw(now, self.rotated)
        self.display_score()

