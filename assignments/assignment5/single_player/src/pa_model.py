# Pacman Game.  Mark Handley, UCL, 2018

from random import *
from enum import Enum
import time
from pa_settings import CANVAS_WIDTH, CANVAS_HEIGHT, GRID_SIZE, STARTUP_LIVES, Direction
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

class MovableObject():
    def __init__(self, x, y, width, height, direction, speed):
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__direction = direction
        self.move_speed = speed
        self.__original_speed = speed

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

    @property
    def speed(self):
        return self.move_speed

    @property
    def grid_position(self):
        return (int((self.__x + 0.5 * GRID_SIZE) //GRID_SIZE), int((self.__y + 0.5 * GRID_SIZE)//GRID_SIZE))

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

    def stop(self):
        self.move_speed = 0

    def set_speed(self, speed_factor):
        self.move_speed = self.__original_speed * speed_factor
        

    def move(self, maze):
        global speed
        prevx = self.__x
        prevy = self.__y
        if self.__direction == Direction.RIGHT:
            self.__x = self.__x + self.move_speed * speed
            if self.__x // GRID_SIZE != prevx // GRID_SIZE:
                if self.collides_with_wall(maze):
                    self.recentre()
                    self.stop()
                    return True
        elif self.__direction == Direction.LEFT:
            self.__x = self.__x - self.move_speed * speed
            if self.__x // GRID_SIZE != prevx // GRID_SIZE:
                if self.collides_with_wall(maze):
                    self.recentre()
                    self.stop()
                    return True
        elif self.__direction == Direction.UP:
            self.__y = self.__y - self.move_speed * speed
            if self.__y // GRID_SIZE != prevy // GRID_SIZE:
                if self.collides_with_wall(maze):
                    self.recentre()
                    self.stop()
                    return True
        elif self.__direction == Direction.DOWN:
            self.__y = self.__y + self.move_speed * speed
            if self.__y // GRID_SIZE != prevy // GRID_SIZE:
                if self.collides_with_wall(maze):
                    self.recentre()
                    self.stop()
                    return True
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
    def __init__(self, grid_x, grid_y, width, height, direction, speed):
        x = GRID_SIZE * grid_x
        y = GRID_SIZE * grid_y
        self.__start_position = (x, y)
        MovableObject.__init__(self, x, y, width, height, direction, speed)
        self.__previous_position = self.position
        self.__user_direction = Direction.NONE

    def reset_position(self):
        self.position = self.__start_position
        self.direction = Direction.LEFT
        self.move_speed = 1
        self.__user_direction = Direction.NONE

    ''' move due to user input '''
    def user_move(self, maze):
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
        if self.position != self.__previous_position:
            return True
        return False

    def collides_with_ghost(self, ghost):
        return closer_than(self.position, ghost.position,GRID_SIZE)

        
class GhostMode(Enum):
    SCATTER = 0
    CHASE = 1
    FRIGHTEN = 2
    FRIGHTEN_TRAPPED = 3
    EYES = 4
        
class Ghost(MovableObject):
    
    def __init__(self, x, y, width, height, direction, speed, ghostnum, maze):
        MovableObject.__init__(self, x, y, width, height, direction, speed)
        self.__ghostnum = ghostnum
        self.__maze = maze
        self.__mode = GhostMode.CHASE
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
        self.__mode = GhostMode.FRIGHTEN
        self.grid_target_x = x
        self.grid_target_y = y
        self.set_speed(0.5)
        self.shortest_path()
        self.frighten_ending = False

    def end_frighten_mode(self):
        if self.mode == GhostMode.FRIGHTEN:
            self.__mode = GhostMode.CHASE
            self.set_scatter_target()
            self.frighten_ending = False

    def warn_frighten_ending(self):
        if self.mode == GhostMode.FRIGHTEN:
            self.frighten_ending = True

    def died(self):
        self.__mode = GhostMode.EYES
        self.grid_target_x = 16
        self.grid_target_y = 14
        self.shortest_path()
        self.set_speed(1)

    def set_scatter_target(self):
        self.grid_target_x = ((self.__ghostnum % 2) * 15 + 6)
        self.grid_target_y = ((self.__ghostnum // 2) * 21 + 5)
        self.target_x = self.grid_target_x * GRID_SIZE
        self.target_y = self.grid_target_y * GRID_SIZE
        self.shortest_path()

    def shortest_path(self):
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

    def aim_for_target(self, maze, choice):
        x, y = self.grid_position
        if not self.centred():
            return
        current_dist = self.shortest_paths[y][x]
        if current_dist == 0:
            if self.mode == GhostMode.EYES:
                self.mode = GhostMode.CHASE
                self.set_scatter_target()
                self.shortest_path()
            elif x == self.grid_target_x:
                self.shortest_paths = self.__maze.shortest_path(1, 1)
            else:
                self.shortest_paths = self.__maze.shortest_path(self.grid_target_x, self.grid_target_y)
        current_dist = self.shortest_paths[y][x]
        neighbours = ((x, y-1), (x-1, y), (x+1, y), (x, y+1))
        olddir = self.direction
        directions = (Direction.UP, Direction.LEFT, Direction.RIGHT, Direction.DOWN)
        possible = []
        for i in range(0,4):
            nx, ny = neighbours[i]
            neighbour_dist = self.shortest_paths[ny][nx]
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
        prevdir = self.direction
        self.aim_for_target(maze, 1)
        result = MovableObject.move(self, maze)
        if result:
            #print("Collided1")
            self.aim_for_target(maze, 1)
            if self.__mode == GhostMode.FRIGHTEN or self.__mode == GhostMode.FRIGHTEN_TRAPPED:
                self.set_speed(0.5)
            else:
                self.set_speed(1.0)
            result = MovableObject.move(self, maze)
        if result:
            #print("Collided2")
            self.grid_target_x = 16
            self.grid_target_y = 17
            self.shortest_path()
            self.aim_for_target(maze, 2)
            if self.__mode == GhostMode.FRIGHTEN or self.__mode == GhostMode.FRIGHTEN_TRAPPED:
                self.set_speed(0.5)
            else:
                self.set_speed(1.0)
            result = MovableObject.move(self, maze)

    def update_pacman_position(self, pac_pos, direction, maze):
        if self.__mode == GhostMode.FRIGHTEN:
            # run away some more...
            self.grid_target_x, self.grid_target_y = pac_pos
            self.shortest_path()
            return
        if self.__mode == GhostMode.FRIGHTEN_TRAPPED:
            # run away again if pacman is close
            if closer_than(pac_pos, self.grid_position, 5):
                self.set_speed(0.5)
                self.__mode = GhostMode.FRIGHTEN
                self.grid_target_x, self.grid_target_y = pac_pos
                self.shortest_path()
            return
        if self.__mode == GhostMode.CHASE and self.__ghostnum == 0:
            self.grid_target_x, self.grid_target_y = pac_pos
            self.shortest_path()
        if self.__mode == GhostMode.CHASE and self.__ghostnum == 1:
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
    def __init__(self):
        self.__levels = []
        for i in range(1,3):
            leveltxt = []
            with open("maze" + str(i) + ".txt", "rt") as f:
                for line in f:
                    leveltxt.append(line)
            self.__levels.append(leveltxt)
        self.__current_level = 1
        self.__tunnel_exits = [None, None]
        self.__food_count = 0
        self.process_current_level()

    def reload(self, level):
        self.__current_level = level
        self.process_current_level()

    def process_current_level(self):
        self.use_level = self.__current_level - 1
        if self.use_level > len(self.__levels) - 1:
            self.use_level = len(self.__levels) - 1  # run out of different mazes
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
                elif c == "###":  # not really a wall, but unreachable
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
                    assert(False)
            self.walls.append(rowwalls)
            y += 1
        self.max_y = len(self.walls) - 1
        self.max_x = len(self.walls[0]) - 1
        #self.print_walls()

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
        if grid_x > self.max_x or grid_y > self.max_y:
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
        if grid_x < 0 or grid_x > self.max_x or grid_y < 0 or grid_y > self.max_y:
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
        dists[target_y][target_x] = 0
        path_squares = []
        self.add_neighbours_to_path(target_x, target_y, path_squares, dists, 1)
        self.explore_paths(path_squares, dists, 1)
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
    DYING = 3
    GAME_OVER = 4
    NEXT_LEVEL_WAIT = 5

class Model():
    def __init__(self, controller):
        global rand
        self.controller = controller
        self.lives = STARTUP_LIVES
        self.init_score()
        rand = Random()

        self.maze = Maze()

        #create game objects
        self.movables = []
        self.ghosts = []
        self.create_ghosts()
        self.pacman = Pacman(14,17, GRID_SIZE, GRID_SIZE,
                             Direction.LEFT, 1)
        #self.pacman = Pacman(GRID_SIZE*10, GRID_SIZE*10, GRID_SIZE, GRID_SIZE,
        #                     Direction.DOWN, 0)
        self.movables.append(self.pacman)
        controller.register_pacman(self.pacman)
        self.__game_mode = GameMode.STARTUP
        self.pause_speedcheck()
        self.won = False

        # initialized speed measurement (see checkspeed for use)
        now = time.time()
        self.lastframe = now
        self.start_time = now
        self.framecount = 0
        self.dont_update_speed = True

    def activate(self):
        self.controller.update_score(0)
        self.controller.update_level(self.level)
        self.controller.update_lives(self.lives)
        self.controller.update_maze(self.maze.current_level)
        self.create_food()
        self.mode_change(GameMode.STARTUP)
        self.won = False

    def init_score(self):
        self.score = 0
        self.level = 1
        self.controller.update_score(0)
        self.controller.update_level(self.level)
        self.controller.update_lives(self.lives)


    def create_ghosts(self):
        #remove any old ghosts
        self.ghosts.clear()
        self.movables.clear()

        y = GRID_SIZE*10
        speeds = [0.9,0.8,0.8,0.8,0]
        for ghostnum in range(0, 4):
            sx = 16
            sy = 15
            x = sx * GRID_SIZE
            y = sy * GRID_SIZE
            direction = Direction.UP
            ghost = Ghost(x, y, GRID_SIZE, GRID_SIZE, direction, speeds[ghostnum], ghostnum, self.maze)
            self.ghosts.append(ghost)
            self.movables.append(ghost)
            self.controller.register_ghost(ghost)

    def create_food(self):
        food_coords, powerpill_coords = self.maze.create_food()
        self.controller.register_food(food_coords)
        self.controller.register_powerpills(powerpill_coords)

    def level_finished(self):
        print("level_finished")
        self.mode_change(GameMode.NEXT_LEVEL_WAIT)

    def died(self):
        self.mode_change(GameMode.DYING)
        self.controller.died(self.pacman)

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
        self.lives -= 1
        if self.lives == 0:
            self.game_over()
            return
        self.__game_mode = GameMode.CHASE
        self.pacman.reset_position()
        self.create_ghosts()
        self.movables.append(self.pacman)
        self.controller.update_lives(self.lives)
        self.controller.unregister_pacman(self.pacman)
        self.controller.register_pacman(self.pacman)
        self.resume_speedcheck()

    def game_over(self):
        self.__game_mode = GameMode.GAME_OVER
        self.won = False
        self.controller.game_over()

    def restart(self):
        self.level = 1
        self.score = 0
        self.reset_level()
        self.dont_update_speed = True

    def next_level(self):
        self.level = self.level + 1
        self.reset_level()

    def reset_level(self):
        self.maze.reload(self.level)
        self.controller.update_level(self.level)
        self.pacman.reset_position()
        self.lives = STARTUP_LIVES
        self.controller.update_lives(self.lives)
        self.controller.unregister_objects()
        self.create_ghosts()
        self.movables.append(self.pacman)
        self.controller.unregister_pacman(self.pacman)
        self.controller.register_pacman(self.pacman)
        self.activate()

    def move_objects(self):
        level_finished = False
        for obj in self.movables:
            obj.move(self.maze)
        self.check_collisions()
        if self.pacman.in_new_square():
            pos = self.pacman.grid_position
            for ghost in self.ghosts:
                ghost.update_pacman_position(pos, self.pacman.direction, self.maze)
            if self.maze.is_food(pos):
                level_finished = self.maze.eat_food(pos)
                self.controller.eat_food(pos)
                self.score += 10
                self.controller.update_score(self.score)
            elif self.maze.is_powerpill(pos):
                level_finished = self.maze.eat_food(pos)  # same code for food and powerpills
                self.controller.eat_powerpill(pos)
                self.mode_change(GameMode.FRIGHTEN)
            elif self.maze.is_tunnel(pos, self.pacman.direction):
                newpos = self.maze.tunnel_exit(pos)
                self.pacman.grid_position = newpos
        if level_finished:
            print("level_finished")
            self.level_finished()

    def check_collisions(self):
        for ghost in self.ghosts:
            if self.pacman.collides_with_ghost(ghost):
                mode = ghost.mode
                if mode == GhostMode.FRIGHTEN:
                    self.ghost_died(ghost)
                    self.controller.ghost_died()
                elif mode == GhostMode.CHASE:
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
            self.move_objects()
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
        elif self.__game_mode == GameMode.DYING:
            if now - self.start_time > 2:
                self.new_life()
        elif self.__game_mode == GameMode.NEXT_LEVEL_WAIT:
            if now - self.start_time > 2:
                self.next_level()


