# Simple Frogger Game.  Mark Handley, UCL, 2018

from fr_controller import Controller
import ctypes
 
ctypes.windll.shcore.SetProcessDpiAwareness(1)
game = Controller()
game.run()
