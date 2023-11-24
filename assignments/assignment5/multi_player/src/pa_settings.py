# Pacman Game.  Mark Handley, UCL, 2018

from enum import IntEnum

CANVAS_WIDTH = 650
CANVAS_HEIGHT = 800
GRID_SIZE = 20
STARTUP_LIVES = 5

PAUSETIME = 0
#PAUSETIME = 0.01
LOGTIME = False
PARTIAL_UPDATE = False

# debugging feature
DONT_DIE = False

# enable sound
USE_SOUND = True 

class Direction(IntEnum):
    UP = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3
    NONE = 4

    def next_dir(self):
        if self is Direction.LEFT:
            self = Direction.DOWN
        elif self is Direction.DOWN:
            self = Direction.RIGHT
        elif self is Direction.RIGHT:
            self = Direction.UP
        elif self is Direction.UP:
            self = Direction.LEFT
        return self

    def opposite(self):
        if self is Direction.LEFT:
            return Direction.RIGHT
        elif self is Direction.RIGHT:
            return Direction.LEFT
        elif self is Direction.UP:
            return Direction.DOWN
        elif self is Direction.DOWN:
            return Direction.UP
        else:
            return Direction.NONE

