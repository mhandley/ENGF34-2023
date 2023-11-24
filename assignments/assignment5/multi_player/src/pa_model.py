# Pacman Game.  Mark Handley, UCL, 2018

from random import *
from enum import Enum
import time
from pa_settings import CANVAS_WIDTH, CANVAS_HEIGHT, GRID_SIZE, STARTUP_LIVES, DONT_DIE, Direction, PAUSETIME, LOGTIME
import sys

speed = 0.0

def closer_than(pos1, pos2, thresh):
    x1, y1 = pos1
    x2, y2 = pos2
    dx = x1 - x2
    dy = y1 - y2
    # compare squares, rather than calling slow sqrt function
    dist2 = dx*dx + dy*dy
    if dist2 < thresh*thresh:
        return True
    return False

def next_square(pos, direction, distance):
    x, y = pos
    if direction == Direction.UP:
        y += distance
    elif direction == Direction.LEFT:
        x -= distance
    elif direction == Direction.RIGHT:
        x += distance
    elif direction == Direction.DOWN:
        y += distance
    else:
        x += distance
        y += distance
    return x, y

class Status(Enum):
    LOCAL = 0   # local object, currently local
    AWAY = 1    # local object, currently on vacation
    FOREIGN = 2 # foreign object visiting us, needs displaying
    REMOTE = 3  # foreign object on their screen, we don't display
    LOCAL_DYING = 4   # dying locally
    AWAY_DYING = 5   # dying while on vacation
    REMOTE_DYING = 6   # foreign object dying there

class MovableObject():
    def __init__(self, x, y, width, height, direction, speed, status, name):
        self.__x = x
        self.__y = y
        self.__start_position = (x, y)
        self.__width = width
        self.__height = height
        self.__direction = direction
        self.move_speed = speed
        self.__frozen = False
        self.__original_speed = speed
        self.__status = status
        self.__name = name

    @property
    def name(self):
        return self.__name

    @property
    def size(self):
        return (self.__width, self.__height)

    @property
    def position(self):
        return (self.__x, self.__y)

    @position.setter
    def position(self, value):
        self.__x = value[0]
        self.__y = value[1]

    def reset_position(self):
        self.position = self.__start_position

    @property
    def speed(self):
        return self.move_speed

    @speed.setter
    def speed(self, value):
        if not self.__frozen:
            self.move_speed = value

    @property
    def grid_position(self):
        return (int((self.__x + 0.5 * GRID_SIZE) //GRID_SIZE), int((self.__y + 0.5 * GRID_SIZE)//GRID_SIZE))

    # we shouldn't need this; needing it is a sign of some other bug.
    # This will hopefully allow that bug to be tracked down.
    def fix_if_outside_grid(self, tag):
        gx, gy = self.grid_position
        if gx >= 0 and gy >= 0 and gx <= max_x and gy <= max_y:
            return
        #print(tag, self.__name, "Outside grid at position", self.__x, self.__y, "grid position", gx, gy)
        if gx < 0:
            gx = 0
        if gy < 0:
            gy = 0
        if gx > max_x:
            gx = max_x
        if gy > max_y:
            gy = max_y
        self.grid_position = gx, gy
    

    @grid_position.setter
    def grid_position(self, value):
        self.__x = value[0] * GRID_SIZE
        self.__y = value[1] * GRID_SIZE

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, direction):
        self.__direction = direction

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def on_our_screen(self):
        return self.__status == Status.LOCAL or self.__status == Status.FOREIGN \
            or self.__status == Status.LOCAL_DYING

    def stop(self):
        self.move_speed = 0

    def freeze(self):
        self.move_speed = 0
        self.__frozen = True

    def unfreeze(self):
        self.__frozen = False

    @property
    def frozen(self):
        return self.__frozen

    def set_speed(self, speed_factor):
        if not self.__frozen:
            self.move_speed = self.__original_speed * speed_factor

    def move(self, maze):
        global speed
        prevx = self.__x
        prevy = self.__y
        if self.__direction == Direction.RIGHT:
            self.__x = self.__x + self.move_speed * speed
            if self.__x // GRID_SIZE != prevx // GRID_SIZE:
                if self.collides_with_wall(maze):
                    self.position = prevx, prevy
                    self.recentre()
                    self.stop()
                    return True
        elif self.__direction == Direction.LEFT:
            self.__x = self.__x - self.move_speed * speed
            if self.__x // GRID_SIZE != prevx // GRID_SIZE:
                if self.collides_with_wall(maze):
                    self.position = prevx, prevy
                    self.recentre()
                    self.stop()
                    return True
        elif self.__direction == Direction.UP:
            self.__y = self.__y - self.move_speed * speed
            if self.__y // GRID_SIZE != prevy // GRID_SIZE:
                if self.collides_with_wall(maze):
                    self.position = prevx, prevy
                    self.recentre()
                    self.stop()
                    return True
        elif self.__direction == Direction.DOWN:
            self.__y = self.__y + self.move_speed * speed
            if self.__y // GRID_SIZE != prevy // GRID_SIZE:
                if self.collides_with_wall(maze):
                    self.position = prevx, prevy
                    self.recentre()
                    self.stop()
                    return True
        self.fix_if_outside_grid("move")
        return False

    def recentre(self):
        newx = (self.__x // GRID_SIZE) * GRID_SIZE
        if self.__x - newx > GRID_SIZE//2:
            newx += GRID_SIZE
        newy = (self.__y // GRID_SIZE) * GRID_SIZE
        if self.__y - newy > GRID_SIZE//2:
            newy += GRID_SIZE
        self.__x = newx
        self.__y = newy

    def centred(self):
        newx = (self.__x // GRID_SIZE) * GRID_SIZE
        newy = (self.__y // GRID_SIZE) * GRID_SIZE
        if abs(self.__x - newx) < GRID_SIZE/10 and abs(self.__y - newy) < GRID_SIZE/10:
            return True
        return False

    def collides_with_wall(self, maze):
        x = int(self.__x) // GRID_SIZE
        y = int(self.__y) // GRID_SIZE
        if self.direction == Direction.RIGHT:
            x += 1
        if self.direction == Direction.DOWN:
            y += 1
        if maze.collides(x, y):
            return True
        return False

    def collides(self, obj):
        obj_x, obj_y = obj.position
        obj_w, obj_h = obj.size
        if obj_y == self.y:
            if abs(obj_x - self.x) <  self.width//2 + obj_width//2:
                return True
        if obj_x == self.x:
            if abs(obj_y - self.y) <  self.height//2 + obj_height//2:
                return True
        return False
            
#logs and turtles are both river objects - they move and act mostly the same
class Pacman(MovableObject):
    def __init__(self, grid_x, grid_y, width, height, direction, speed, status, name):
        x = GRID_SIZE * grid_x
        y = GRID_SIZE * grid_y
        MovableObject.__init__(self, x, y, width, height, direction, speed, status, name)
        self.__previous_grid_position = self.grid_position
        self.__user_direction = Direction.NONE

    def reset_position(self):
        MovableObject.reset_position(self)
        self.direction = Direction.LEFT
        self.move_speed = 1
        self.__user_direction = Direction.NONE

    ''' move due to user input '''
    def user_move(self, maze):
        if self.frozen:
            return
        if self.__user_direction == self.direction:
            return
        elif self.__user_direction == self.direction.opposite():
            self.direction = self.__user_direction
            self.move_speed = 1
            return

        # if we're here, we're trying to turn 90 degrees.  Need to
        # check if the way is clear.
        if self.centred():
            grid_x, grid_y = self.next_user_square()
            if maze.square_is_empty(grid_x, grid_y):
                self.direction = self.__user_direction
                self.move_speed = 1

    def next_user_square(self):
        grid_x, grid_y = self.grid_position
        if self.__user_direction == Direction.NONE:
            return grid_x, grid_y
        elif self.__user_direction == Direction.LEFT:
            return grid_x - 1, grid_y
        elif self.__user_direction == Direction.RIGHT:
            return grid_x + 1, grid_y
        elif self.__user_direction == Direction.UP:
            return grid_x, grid_y - 1
        else:
            return grid_x, grid_y + 1

    def key_press(self, direction):
        self.__user_direction = direction
        self.__key_up_time = 0

    def key_release(self):
        self.__key_up_time = time.time()
        #self.__user_direction = Direction.NONE

    def move(self, maze):
        if self.is_dying:
            return   # can't move while dying
        if self.__user_direction != Direction.NONE:
            # allow key press to register for half a second
            if self.__key_up_time != 0 and time.time() - self.__key_up_time > 0.5:
                self.__user_direction = Direction.NONE
            else:
                self.user_move(maze)
        result = MovableObject.move(self, maze)
        if result:
            self.stop()

    def in_new_square(self):
        if self.grid_position != self.__previous_grid_position:
            self.__previous_grid_position = self.grid_position
            return True
        return False

    def collides_with_ghost(self, ghost):
        return closer_than(self.position, ghost.position, GRID_SIZE)

    def died(self):
        if self.status == Status.LOCAL:
            self.status = Status.LOCAL_DYING
        elif self.status == Status.AWAY:
            self.status = Status.AWAY_DYING
        self.time_of_death = time.time()
        self.stop()

    @property
    def is_dying(self):
        if self.status == Status.LOCAL_DYING or self.status == Status.AWAY_DYING:
            return True
        return False
        
class GhostMode(Enum):
    SCATTER = 0
    CHASE = 1
    FRIGHTEN = 2
    FRIGHTEN_TRAPPED = 3
    EYES = 4
        
class Ghost(MovableObject):
    
    def __init__(self, x, y, width, height, direction, speed, ghostnum, maze, status):
        name = "Ghost" + str(ghostnum)
        MovableObject.__init__(self, x, y, width, height, direction, speed, status, name)
        self.__ghostnum = ghostnum
        self.__maze = maze
        self.__status = status
        self.__mode = GhostMode.CHASE
        self.frighten_ending = False
        if status == Status.REMOTE:
            self.__remote = True
        else:
            self.__remote = False
            self.set_scatter_target()

    @property
    def mode(self):
        if self.__mode == GhostMode.FRIGHTEN or self.__mode == GhostMode.FRIGHTEN_TRAPPED:
            return GhostMode.FRIGHTEN
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = value

    @property
    def ghostnum(self):
        return self.__ghostnum

    def start_frighten_mode(self, x, y):
        assert(not self.__remote)
        self.__mode = GhostMode.FRIGHTEN
        self.grid_target_x = x
        self.grid_target_y = y
        self.set_speed(0.5)
        self.shortest_path()
        self.frighten_ending = False

    def end_frighten_mode(self):
        assert(not self.__remote)
        if self.mode == GhostMode.FRIGHTEN:
            self.__mode = GhostMode.CHASE
            self.set_scatter_target()
            self.frighten_ending = False

    def warn_frighten_ending(self):
        assert(not self.__remote)
        if self.mode == GhostMode.FRIGHTEN:
            self.frighten_ending = True

    def died(self):
        self.__mode = GhostMode.EYES
        self.grid_target_x = 16
        self.grid_target_y = 14
        self.shortest_path()
        self.set_speed(1)

    def set_scatter_target(self):
        assert(not self.__remote)
        self.grid_target_x = ((self.__ghostnum % 2) * 15 + 6)
        self.grid_target_y = ((self.__ghostnum // 2) * 21 + 5)
        self.target_x = self.grid_target_x * GRID_SIZE
        self.target_y = self.grid_target_y * GRID_SIZE
        self.shortest_path()

    def shortest_path(self):
        assert(not self.__remote)
        # Find shortest path to target.  Basically, run a shortest
        # path algorithm to calculate distances from the target.
        # Follow reducing distances.
        self.shortest_paths = self.__maze.shortest_path(self.grid_target_x, self.grid_target_y)

    def print_shortest_path(self):
        s = "Ghost " + str(self.__ghostnum) + "\n"
        for row in self.shortest_paths:
            for sq in row:
                if sq == 1000:
                    s += " ? "
                elif sq == -1:
                    s += "###"
                elif sq < 10:
                    s += " " + str(sq) + " "
                elif sq < 100:
                    s += str(sq) + " "
                else:
                    s += "***"
            s += "\n"
        print(s)

    def get_current_dist(self, x, y, tag):
        current_dist = 0
        try:
            current_dist = self.shortest_paths[y][x]
        except IndexError as e:
            print("ERROR: ", self.name, "outside grid?", e)
            print("x, y =", x, y)
            print("tag: ", tag)
            print("position = ", self.position)
            self.print_shortest_path()
        return current_dist

    def aim_for_target(self, maze, choice):
        assert(not self.__remote)
        x, y = self.grid_position
        self.fix_if_outside_grid("aim_for_target")
        if not self.centred():
            return
        current_dist = self.get_current_dist(x, y, "1")
        if current_dist == 0:
            if self.mode == GhostMode.EYES:
                self.mode = GhostMode.CHASE
                self.set_scatter_target()
                self.shortest_path()
            elif x == self.grid_target_x:
                self.shortest_paths = self.__maze.shortest_path(1, 1)
            else:
                self.shortest_paths = self.__maze.shortest_path(self.grid_target_x, self.grid_target_y)
        current_dist = self.get_current_dist(x, y, "2")
        neighbours = ((x, y-1), (x-1, y), (x+1, y), (x, y+1))
        olddir = self.direction
        directions = (Direction.UP, Direction.LEFT, Direction.RIGHT, Direction.DOWN)
        possible = []
        for i in range(0,4):
            nx, ny = neighbours[i]
            if nx < 0 or nx > max_x or ny < 0 or ny > max_y:
                neighbour_dist = -1  # can happen near tunnel
            else:
                neighbour_dist = self.get_current_dist(nx, ny, "3")
            if self.__mode == GhostMode.FRIGHTEN:
                # run away, run away!
                if neighbour_dist >= 0 and neighbour_dist > current_dist:
                    possible.append(i)
            else:
                if neighbour_dist >= 0 and neighbour_dist < current_dist:
                    possible.append(i)
        if len(possible) == 0:
            # do anything
            self.set_scatter_target()
            if self.__mode == GhostMode.FRIGHTEN:
                self.__mode = GhostMode.FRIGHTEN_TRAPPED
            return
        randi = possible[rand.randint(0, len(possible)-1)]
        self.direction = directions[randi]
        if self.direction != olddir:
            self.recentre()
        return

    def move(self, maze):
        assert(not self.__remote)
        prevdir = self.direction
        self.aim_for_target(maze, 1)
        result = MovableObject.move(self, maze)
        if result:
            self.aim_for_target(maze, 1)
            if self.__mode == GhostMode.FRIGHTEN or self.__mode == GhostMode.FRIGHTEN_TRAPPED:
                self.set_speed(0.5)
            else:
                self.set_speed(1.0)
            result = MovableObject.move(self, maze)
        if result:
            self.grid_target_x = 16
            self.grid_target_y = 17
            self.shortest_path()
            self.aim_for_target(maze, 2)
            if self.__mode == GhostMode.FRIGHTEN or self.__mode == GhostMode.FRIGHTEN_TRAPPED:
                self.set_speed(0.5)
            else:
                self.set_speed(1.0)
            result = MovableObject.move(self, maze)

    def update_pacman_position(self, pac_pos, direction, maze, \
                               have_local, have_foreign, this_is_foreign):
        # pacman 0 and 1 prefer to react to local pacman
        # pacman 2 and 3 prefer to react to foreign pacman
        # but all will react if they're frightened and pacman is close
        react_to_pacman = this_is_foreign and (self.__ghostnum >= 2 or (not have_local)) \
                           or ((not this_is_foreign) \
                               and (self.__ghostnum < 2 or (not have_foreign)))
                           
        if self.__mode == GhostMode.FRIGHTEN_TRAPPED:
            # run away again if pacman is close
            if closer_than(pac_pos, self.grid_position, 5):
                self.set_speed(0.5)
                self.__mode = GhostMode.FRIGHTEN
                self.grid_target_x, self.grid_target_y = pac_pos
                self.shortest_path()
            return

        if not react_to_pacman:
            # ghosts 2 and 3:
            # there's a foreign pacman about, and this isn't it.
            # run away if it's close, but otherwise ignore it
            if self.__mode == GhostMode.FRIGHTEN \
               and closer_than(pac_pos, self.grid_position, 5):
                self.set_speed(0.5)
                self.grid_target_x, self.grid_target_y = pac_pos
                self.shortest_path()
            return

        if self.__mode == GhostMode.FRIGHTEN:
            # run away some more...
            self.grid_target_x, self.grid_target_y = pac_pos
            self.shortest_path()
            return
        if (self.__mode == GhostMode.CHASE and 
            ((self.__ghostnum == 0 and (not this_is_foreign)) 
             or (self.__ghostnum == 2 and (this_is_foreign)))):
            self.grid_target_x, self.grid_target_y = pac_pos
            self.shortest_path()
        if (self.__mode == GhostMode.CHASE and 
            ((self.__ghostnum == 1 and (not this_is_foreign)) 
             or (self.__ghostnum == 3 and (this_is_foreign)))):
            # try to aim ahead of pacman if that's possible
            pos = next_square(pac_pos, direction, 4)
            if (maze.is_wall(pos)):
                pos = next_square(pac_pos, direction, 5)
            if (maze.is_wall(pos)):
                pos = next_square(pac_pos, direction, 3)
            if (maze.is_wall(pos)):
                pos = pac_pos
            self.grid_target_x, self.grid_target_y = pos
            self.shortest_path()
            
        
class Maze():
    def __init__(self, mazenum):
        self.__levels = []
        for i in range(0,3):
            leveltxt = []
            with open("maze" + str(i) + ".txt", "rt") as f:
                for line in f:
                    leveltxt.append(line)
            self.__levels.append(leveltxt)

        #XXX
        #if serv:
        #    self.__levels[0] = self.__levels[1]
        self.__current_level = mazenum
        self.__tunnel_exits = [None, None]
        self.__food_count = 0
        self.process_current_level()

    def reload(self, level):
        self.__food_count = 0
        self.__current_level = level
        self.process_current_level()

    def process_current_level(self):
        global max_x, max_y
        self.use_level = self.__current_level % len(self.__levels)
        level = self.__levels[self.use_level]
        self.walls = []
        self.__tunnel_exits = [None, None]
        y = 0
        for row in level:
            rowwalls = []
            for x in range(0, len(row)//3):
                c = row[x*3:(x+1)*3]
                if c == " /-":
                    rowwalls.append(1)
                elif c == "-/ ":
                    rowwalls.append(1)
                elif c == "---":
                    rowwalls.append(1)
                elif c == "-\\ ":
                    rowwalls.append(1)
                elif c == " \\-":
                    rowwalls.append(1)
                elif c == " | ":
                    rowwalls.append(1)
                elif c == "###":
                    rowwalls.append(1)
                elif c == "   ":
                    rowwalls.append(0)
                elif c == " . ":
                    self.__food_count += 1
                    rowwalls.append(2)
                elif c == " * ":
                    self.__food_count += 1
                    rowwalls.append(3)
                elif c == " A ":
                    rowwalls.append(4)
                    self.__tunnel_exits[0] = (x,y)
                elif c == " B ":
                    rowwalls.append(5)
                    self.__tunnel_exits[1] = (x,y)
                else:
                    print(c)
                    assert(False)
            self.walls.append(rowwalls)
            y += 1
        max_y = len(self.walls) - 1
        max_x = len(self.walls[0]) - 1

    def print_walls(self):
        s = ""
        for row in self.walls:
            for square in row:
                if square == 0:
                    s += " "
                elif square == 1:
                    s += "#"
                elif square == 2:
                    s += "."
                elif square == 3:
                    s += "*"
                elif square == 4:
                    s += "A"
                elif square == 5:
                    s += "B"
            s += "\n"
        print(s)

    @property
    def current_level(self):
        return self.__levels[self.use_level]

    def collides(self, grid_x, grid_y):
        if grid_x < 0 or grid_y < 0 or grid_x > max_x or grid_y > max_y:
            return False
        square = self.walls[grid_y][grid_x]
        if square == 1:
            return True
        return False

    def create_food(self):
        food_coords = []
        powerpill_coords = []
        y =0
        for row in self.walls:
            x = 0
            for square in row:
                if square == 2:
                    food_coords.append((x,y))
                elif square == 3:
                    powerpill_coords.append((x, y))
                x += 1
            y += 1
        return food_coords, powerpill_coords

    def is_food(self, coords):
        grid_x, grid_y = coords
        if self.walls[grid_y][grid_x] == 2:
            return True
        return False
    
    def is_powerpill(self, coords):
        grid_x, grid_y = coords
        if self.walls[grid_y][grid_x] == 3:
            return True
        return False

    def is_tunnel(self, coords, direction):
        grid_x, grid_y = coords
        if (self.walls[grid_y][grid_x] == 4 and direction == Direction.LEFT) \
           or (self.walls[grid_y][grid_x] == 5 and direction == Direction.RIGHT) :
            return True
        return False

    def is_wall(self, coords):
        grid_x, grid_y = coords
        if grid_x < 0 or grid_x > max_x or grid_y < 0 or grid_y > max_y:
            return True
        if self.walls[grid_y][grid_x] == 1:
            return True
        return False
    
    def eat_food(self, coords):
        grid_x, grid_y = coords
        if self.walls[grid_y][grid_x] == 2 or self.walls[grid_y][grid_x] == 3:
            self.walls[grid_y][grid_x] = 0
            self.__food_count -= 1
        if self.__food_count <= 0:
            return True
        return False

    def shortest_path(self, target_x, target_y):
        dists = []
        y = 0
        for row in self.walls:
            rowdists = []
            x = 0
            for square in row:
                if square == 1 or square == 4 or square == 5:
                    rowdists.append(-1) #it's a wall, so unreachable (or a tunnel)
                elif square == 0 or square == 2 or square == 3:
                    rowdists.append(1000) # large number, dist not yet known
                x += 1
            dists.append(rowdists)
            y += 1
        if target_x < 0 or target_y < 0 or target_x > max_x or target_y > max_y:
            print(target_x, target_y, max_x, max_y)
        dists[target_y][target_x] = 0
        path_squares = []
        self.add_neighbours_to_path(target_x, target_y, path_squares, dists, 1)
        self.explore_paths(path_squares, dists, 1)
        assert(len(dists) - 1 == max_y)
        return dists


    def explore_paths(self, path_squares, dists, current_dist):
        new_path_squares = []
        for sx,sy in path_squares:
            if dists[sy][sx] > current_dist:
                dists[sy][sx] = current_dist
                self.add_neighbours_to_path(sx, sy, new_path_squares, dists, current_dist+1)
        if len(new_path_squares) > 0:
            self.explore_paths(new_path_squares, dists, current_dist+1)

    def add_neighbours_to_path(self, x, y, path_squares, dists, mindist):
        neighbours = ((x, y-1), (x-1, y), (x+1, y), (x, y+1))
        for nx,ny in neighbours:
            if nx > 0 and nx < 28 and self.walls[ny][nx] != 1 and dists[ny][nx] >= mindist:
                path_squares.append((nx,ny))

    def square_is_empty(self, x, y):
        if self.walls[y][x] != 1:
            return True
        return False

    def tunnel_exit(self, pos):
        for i in range(0,2):
            if self.__tunnel_exits[i] == pos:
                return self.__tunnel_exits[1-i]
        # shouldn't happen
        return None
            
    
class GameMode(Enum):
    STARTUP = 0
    CHASE = 1
    FRIGHTEN = 2
    DYING = 3  # not used in multi-player
    GAME_OVER = 4
    NEXT_LEVEL_WAIT = 5
    READY_TO_RESTART = 6

class Model():
    def __init__(self, controller, mazenum):
        global rand
        self.controller = controller
        self.mylives = STARTUP_LIVES
        self.init_score()
        rand = Random()
        self.__mazenum = mazenum
        self.__maze = Maze(mazenum)
        self.__remote_maze = None

        #create game objects
        self.movables = []
        self.ghosts = []
        self.remote_ghosts = []  # ghosts on remote machine, controlled by remote machine 
        self.create_ghosts()
        self.pacman = Pacman(14,17, GRID_SIZE, GRID_SIZE,
                             Direction.LEFT, 1, Status.LOCAL, "Pacman1")
        self.foreign_pacman = None
        self.movables.append(self.pacman)
        controller.register_pacman(self.pacman, 0)
        self.__game_mode = GameMode.STARTUP
        self.pause_speedcheck()
        self.they_are_ready_to_restart = False
        self.won = False
        self.controller.update_score(0)
        self.controller.update_level(self.level, 0)
        self.controller.update_lives(self.mylives)
        self.controller.update_maze(self.__maze.current_level, 0)

        # initialized speed measurement (see checkspeed for use)
        now = time.time()
        self.lastframe = now
        self.start_time = now
        self.framecount = 0
        self.dont_update_speed = True

    def activate(self):
        self.controller.send_maze(self.__maze)
        self.controller.update_score(0)
        self.controller.update_level(self.level, 0)
        self.controller.update_lives(self.mylives)
        self.controller.update_maze(self.__maze.current_level, 0)
        self.create_food(self.__maze, 0)
        self.mode_change(GameMode.STARTUP)
        self.won = False

    def init_score(self):
        self.score = 0
        self.level = 1
        self.controller.update_score(0)
        self.controller.update_level(self.level, 0)
        self.controller.update_lives(self.mylives)


    def create_ghosts(self):
        #remove any old ghosts
        self.ghosts.clear()
        self.remote_ghosts.clear()
        self.controller.unregister_ghosts()
        self.movables.clear()

        y = GRID_SIZE*10
        speeds = [0.9,0.8,0.8,0.8,0]
        for ghostnum in range(0, 4):
            sx = 16
            sy = 15
            x = sx * GRID_SIZE
            y = sy * GRID_SIZE
            direction = Direction.UP
            ghost = Ghost(x, y, GRID_SIZE, GRID_SIZE, direction, speeds[ghostnum], ghostnum, self.__maze, Status.LOCAL)
            self.ghosts.append(ghost)
            self.movables.append(ghost)
            self.controller.register_ghost(ghost, 0)

            remote_ghost = Ghost(x, y, GRID_SIZE, GRID_SIZE, direction, speeds[ghostnum], ghostnum, self.__maze, Status.REMOTE)
            self.remote_ghosts.append(remote_ghost)
            self.controller.register_ghost(remote_ghost, 1)

    def reset_ghosts(self):
        for ghost in self.ghosts:
            ghost.reset_position()
            ghost.status = GhostMode.CHASE

    def create_food(self, maze, screen):
        food_coords, powerpill_coords = maze.create_food()
        self.controller.register_food(food_coords, screen)
        self.controller.register_powerpills(powerpill_coords, screen)

    def level_finished(self):
        self.controller.send_status_update(GameMode.NEXT_LEVEL_WAIT)
        self.mode_change(GameMode.NEXT_LEVEL_WAIT)

    def died(self):
        if DONT_DIE:
            return
        if self.pacman.on_our_screen:
            #we'll need to clear out the ghosts
            clear_ghosts = True
            screen = 0
            #in the model, get the ghosts out of the way,
            # so they don't kill any foreign pacman
            for ghost in self.ghosts:
                ghost.reset_position()
                ghost.freeze()
        else:
            clear_ghosts = False
            screen = 1
        self.pacman.died()
        self.pacman.move_speed = 0
        self.controller.died(self.pacman, clear_ghosts, screen)

    def ghost_died(self, ghost):
        ghost.died()
        self.score += 200

    def mode_change(self, mode):
        if mode == GameMode.DYING \
           or mode == GameMode.NEXT_LEVEL_WAIT \
           or mode == GameMode.GAME_OVER:
            self.pause_start()
        elif mode == GameMode.CHASE:
            self.pause_end()
        elif mode == GameMode.STARTUP:
            self.start_time = time.time()
        elif mode == GameMode.FRIGHTEN:
            self.start_time = time.time()
            self.start_frighten_mode()
        self.__game_mode = mode

    def start_frighten_mode(self):
        x, y = self.pacman.grid_position
        for ghost in self.ghosts:
            ghost.start_frighten_mode(x, y)

    def warn_frighten_ending(self):
        for ghost in self.ghosts:
            ghost.warn_frighten_ending()

    def end_frighten_mode(self):
        for ghost in self.ghosts:
            ghost.end_frighten_mode()

    def pause_start(self):
        self.start_time = time.time()
        self.pause_speedcheck()

    def pause_end(self):
        self.resume_speedcheck()
            
    def new_life(self):
        self.mylives -= 1
        if self.mylives == 0:
            self.game_over()
            return
        self.__game_mode = GameMode.CHASE
        self.pacman.move_speed = 1
        self.pacman.reset_position()
        self.controller.send_pacman_update(self.pacman.position,
                                           self.pacman.direction,
                                           self.pacman.speed)
        recreate_ghosts = False
        if self.pacman.status == Status.AWAY_DYING:
            self.controller.unregister_pacman(self.pacman, 1)
            self.controller.register_pacman(self.pacman, 0)
            self.controller.send_foreign_pacman_left()
        else:
            recreate_ghosts = True
            assert(self.pacman.status == Status.LOCAL_DYING)
        self.pacman.status = Status.LOCAL
        for ghost in self.ghosts:
            ghost.unfreeze()
        if recreate_ghosts:
            self.create_ghosts()
            self.movables.append(self.pacman)
        else:
            self.reset_ghosts()
        self.controller.update_lives(self.mylives)
        self.controller.unregister_pacman(self.pacman, 0)
        self.controller.register_pacman(self.pacman, 0)
        self.resume_speedcheck()

    def game_over(self):
        self.__game_mode = GameMode.GAME_OVER
        self.won = False
        self.controller.game_over()
        self.controller.send_status_update(GameMode.GAME_OVER)
        self.they_are_ready_to_restart = False

    def remote_game_over(self):
        self.__game_mode = GameMode.GAME_OVER
        self.won = False
        self.controller.game_over()
        self.they_are_ready_to_restart = False

    def ready_to_restart(self):
        if self.__game_mode != GameMode.GAME_OVER:
            return
        self.__game_mode = GameMode.READY_TO_RESTART
        self.controller.send_status_update(GameMode.READY_TO_RESTART)
        if self.they_are_ready_to_restart:
            self.restart()
        else:
            self.controller.display_msg("Waiting for player 2...", 0)

    def restart(self):
        self.level = 1
        self.score = 0
        self.reset_level()
        self.dont_update_speed = True

    def next_level(self):
        if self.foreign_pacman is not None:
            self.controller.send_pacman_go_home()
        self.level = self.level + 1
        self.reset_level()

    def reset_level(self):
        self.__maze.reload(self.level+self.__mazenum)
        self.controller.update_level(self.level, 0)
        self.pacman.reset_position()
        if not self.pacman.on_our_screen:
            self.controller.send_foreign_pacman_left()
            self.pacman.status = Status.LOCAL
        self.controller.send_pacman_update(self.pacman.position,
                                           self.pacman.direction,
                                           self.pacman.speed)
        self.mylives = STARTUP_LIVES
        self.controller.update_lives(self.mylives)
        self.controller.unregister_objects()
        self.create_ghosts()
        self.movables.append(self.pacman)
        self.controller.unregister_pacman(self.pacman, 0)
        self.controller.register_pacman(self.pacman, 0)
        self.activate()

    def update_objects(self, now):
        if self.pacman.is_dying:
            if now - self.pacman.time_of_death > 2:
                self.new_life()
        
        level_finished = False
        for obj in self.movables:
            if obj.on_our_screen:
                obj.move(self.__maze)
            else:
                obj.move(self.__remote_maze)
        self.check_collisions()
        if self.pacman.on_our_screen:
            maze = self.__maze
        else:
            maze = self.__remote_maze
        if self.pacman.in_new_square():
            pos = self.pacman.grid_position
            for ghost in self.ghosts:
                have_local = self.pacman.on_our_screen
                have_foreign = (self.foreign_pacman is not None)
                this_is_foreign = False
                ghost.update_pacman_position(pos, self.pacman.direction, self.__maze,
                                             have_local, have_foreign, this_is_foreign)
            if maze.is_food(pos):
                level_finished = maze.eat_food(pos)
                maze_finished = maze
                self.notify_eat_food(pos)
                self.score += 10
                self.controller.update_score(self.score)
            elif maze.is_powerpill(pos):
                # same code for food and powerpills
                level_finished = maze.eat_food(pos)
                maze_finished = maze
                self.notify_eat_powerpill(pos)
                if maze is self.__maze:
                    self.mode_change(GameMode.FRIGHTEN)
            elif maze.is_tunnel(pos, self.pacman.direction):
                #newpos = self.__maze.tunnel_exit(pos)
                #self.pacman.grid_position = newpos
                self.go_to_other_maze(pos)
                return
        if self.foreign_pacman is not None and self.foreign_pacman.in_new_square:
            for ghost in self.ghosts:
                have_local = self.pacman.on_our_screen
                have_foreign = True
                this_is_foreign = True
                pos = self.foreign_pacman.grid_position
                dirn = self.foreign_pacman.direction
                ghost.update_pacman_position(pos, dirn, self.__maze,
                                             have_local, have_foreign, this_is_foreign)
            
        if level_finished and maze_finished is self.__maze:
            self.level_finished()

        self.controller.send_pacman_update(self.pacman.position,
                                           self.pacman.direction,
                                           self.pacman.speed)
        if self.foreign_pacman != None:
            for ghost in self.ghosts:
                self.controller.send_ghost_update(ghost.ghostnum, ghost.position,
                                                  ghost.direction, ghost.speed,
                                                  ghost.mode)

    def notify_eat_food(self, pos):
        self.notify_eat(pos, False)

    def notify_eat_powerpill(self, pos):
        self.notify_eat(pos, True)

    def notify_eat(self, pos, is_powerpill):
        if self.pacman.on_our_screen:
            self.controller.eat(pos, is_powerpill, 0)
            self.controller.send_eat(pos, is_powerpill)
        else:
            self.controller.eat(pos, is_powerpill, 1)
            self.controller.send_foreign_eat(pos, is_powerpill)

    def go_to_other_maze(self, pos):
        # we'll assume the entrance is always in the same place
        newpos = self.__maze.tunnel_exit(pos)
        self.pacman.grid_position = newpos
        if self.pacman.status == Status.LOCAL:
            self.pacman.status = Status.AWAY
            self.controller.send_foreign_pacman_arrived()
            self.controller.unregister_pacman(self.pacman, 0)
            self.controller.register_pacman(self.pacman, 1)
        elif self.pacman.status == Status.AWAY:
            self.pacman.status = Status.LOCAL
            self.controller.send_foreign_pacman_left()
            self.controller.unregister_pacman(self.pacman, 1)
            self.controller.register_pacman(self.pacman, 0)
                
    def check_collisions(self):
        if self.pacman.is_dying:
            return   # can't die, we're dead

        if self.pacman.status == Status.AWAY:
            ghosts = self.remote_ghosts
        else:
            ghosts = self.ghosts
            
        for ghost in ghosts:
            if self.pacman.collides_with_ghost(ghost):
                mode = ghost.mode
                if mode == GhostMode.FRIGHTEN:
                    if self.pacman.status == Status.LOCAL:
                        self.ghost_died(ghost)
                        self.controller.ghost_died(0)
                    elif self.pacman.status == Status.AWAY:
                        self.controller.send_foreign_pacman_ate_ghost(ghost.ghostnum)
                        self.controller.ghost_died(1)
                elif mode == GhostMode.CHASE:
                    if self.pacman.status == Status.LOCAL:
                        self.died()
                    elif self.pacman.status == Status.AWAY:
                        self.died()
            

    def key_press(self, direction):
        '''move_pacman is called when the user requests the pacman moves in a
           particular direction
        '''
        self.pacman.key_press(direction)

    def key_release(self):
        '''move_pacman is called when the user requests the pacman moves in a
           particular direction
        '''
        self.pacman.key_release()

    def received_maze(self, maze):
        self.__remote_maze = maze
        self.controller.update_maze(self.__remote_maze.current_level, 1)
        self.create_food(self.__remote_maze, 1)

    def foreign_pacmac_init(self):
        self.foreign_pacman = Pacman(0,17, GRID_SIZE, GRID_SIZE,
                                     Direction.UP, 1, Status.REMOTE, "Pacman2")
        self.controller.register_pacman(self.foreign_pacman, 1)

    ''' the pacman from the remote system came through the tunnel and is now on our screen'''
    def foreign_pacman_arrived(self):
        self.foreign_pacman.status = Status.FOREIGN
        self.controller.unregister_pacman(self.foreign_pacman, 1)
        self.controller.register_pacman(self.foreign_pacman, 0)

    ''' the pacman from the remote system came through the tunnel and is now on our screen'''
    def foreign_pacman_left(self):
        self.foreign_pacman.status = Status.REMOTE
        self.controller.unregister_pacman(self.foreign_pacman, 0)
        self.controller.register_pacman(self.foreign_pacman, 1)
        # make sure the ghosts following the foreign pacman don't keep following!
        self.ghosts[2].set_scatter_target()
        self.ghosts[3].set_scatter_target()

    def foreign_pacman_died(self):
        if self.foreign_pacman.on_our_screen:
            screen = 0
        else:
            screen = 1
        self.foreign_pacman.speed = 0
        self.foreign_pacman.died()
        clear_ghosts = False
        self.controller.died(self.foreign_pacman, clear_ghosts,screen)
        self.foreign_pacman.status = Status.REMOTE_DYING

    def foreign_pacman_update(self, pos, dir, speed):
        if self.foreign_pacman is None:
            self.foreign_pacmac_init()
        if self.foreign_pacman.status == Status.REMOTE_DYING and speed > 0:
            self.controller.unregister_pacman(self.foreign_pacman, 1)
            self.controller.register_pacman(self.foreign_pacman, 1)
            self.foreign_pacman.status = Status.REMOTE
        if self.foreign_pacman is not None and self.foreign_pacman.frozen == False:
            self.foreign_pacman.position = pos
            self.foreign_pacman.direction = dir
            self.foreign_pacman.speed = speed

    def foreign_pacman_ate_ghost(self, ghostnum):
        for ghost in self.ghosts:
            if ghost.ghostnum == ghostnum:
                if ghost.mode == GhostMode.FRIGHTEN:
                    ghost.died()

    def pacman_go_home(self):
        self.controller.send_foreign_pacman_left()
        self.controller.unregister_pacman(self.pacman, 1)
        self.controller.register_pacman(self.pacman, 0)
        self.pacman.status = Status.LOCAL
        self.pacman.reset_position()
        self.controller.send_pacman_update(self.pacman.position,
                                           self.pacman.direction,
                                           self.pacman.speed)
        self.pacman.unfreeze()
        
    def remote_ghost_update(self, ghostnum, pos, dir, speed, mode):
        ghost = self.remote_ghosts[ghostnum]
        ghost.position = pos
        ghost.directon = dir
        ghost.speed = speed
        ghost.mode = mode

    def remote_status_update(self, remote_status):
        if remote_status == GameMode.NEXT_LEVEL_WAIT:
            if not self.pacman.on_our_screen:
                self.pacman.freeze()
            return
        if remote_status == GameMode.GAME_OVER:
            self.remote_game_over()
        if self.__game_mode == GameMode.GAME_OVER \
           and remote_status == GameMode.READY_TO_RESTART:
            self.they_are_ready_to_restart = True
        elif self.__game_mode == GameMode.READY_TO_RESTART \
             and remote_status == GameMode.READY_TO_RESTART:
            self.restart()
                
    ''' adjust game speed so it's more or less the same on different machines '''
    def checkspeed(self, now):
        global speed
        self.framecount = self.framecount + 1
        # only check every ten frames                                                        
        if self.framecount == 10:
            elapsed = now - self.lastframe
            self.lastframe = now
            self.framecount = 0
            # if we've just started, or just unpaused, don't update
            # the speed as it will end up wrong
            if self.dont_update_speed == True:
                self.dont_update_speed = False  
                return
            # speed will be 1.0 if we're achieving 60 fps                                    
            if speed == 0:
                #initial speed value                                                         
		# At 60fps, 10 frames take 1/6 of a second.                                  
                speed = 12 * elapsed
            else:
                # use an EWMA to damp speed changes and avoid excessive jitter               
                speed = speed * 0.9 + 0.1 * 12 * elapsed
        time.sleep(PAUSETIME)

    def foreign_eat(self, pos, is_powerpill):
        # A foreign pacmac on our screen ate food or powerpill
        if is_powerpill:
            level_finished = self.__maze.eat_food(pos)
            self.mode_change(GameMode.FRIGHTEN)
        else:
            level_finished = self.__maze.eat_food(pos)
        self.controller.eat(pos, is_powerpill, 0)
        if level_finished:
            self.level_finished()
            if self.foreign_pacman is not None:
                self.foreign_pacman.freeze()


    def remote_eat(self, pos, is_powerpill):
        # A remote pacman ate remote food or powerpill.
        # We need to update our copy of their maze.
        if is_powerpill:
            level_finished = self.__remote_maze.eat_food(pos)
        else:
            level_finished = self.__remote_maze.eat_food(pos)
        self.controller.eat(pos, is_powerpill, 1)

    def pause_speedcheck(self):
        global speed
        self.previous_speed = speed

    def resume_speedcheck(self):
        global speed
        speed = self.previous_speed
        self.framecount = 0
        self.lastframe = time.time()
        
    def update(self, now):
        if self.__game_mode == GameMode.CHASE or self.__game_mode == GameMode.FRIGHTEN:
            self.update_objects(now)
            self.controller.update_score(self.score)
            self.checkspeed(now)
            if self.__game_mode == GameMode.FRIGHTEN:
                if now - self.start_time > 15:
                    self.end_frighten_mode()
                elif now - self.start_time > 10:
                    self.warn_frighten_ending()
        elif self.__game_mode == GameMode.STARTUP:
            if now - self.start_time > 5:
                self.mode_change(GameMode.CHASE)
        elif self.__game_mode == GameMode.NEXT_LEVEL_WAIT:
            if now - self.start_time > 2:
                self.next_level()
