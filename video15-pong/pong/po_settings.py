# Simple Pong Game.  Mark Handley, UCL, 2019

from enum import Enum

SCALE = 0.75
CANVAS_WIDTH = int(1000*SCALE)
CANVAS_HEIGHT = int(700*SCALE)
BAT_HEIGHT = int(100*SCALE)
BAT_WIDTH = int(20*SCALE)
BALL_SIZE = int(20*SCALE)
BALL_SPEED = int(8*SCALE)
BAT_SPEED = int(10*SCALE)

class Direction(Enum):
    NONE = 0
    UP = 1
    DOWN = 2

def reverse_direction(dirn):
    if dirn == Direction.UP:
        return Direction.DOWN
    elif dirn == Direction.DOWN:
        return Direction.UP
    else:
        return dirn
