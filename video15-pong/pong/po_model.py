# Simple Pong Game.  Mark Handley, UCL, 2019

from random import *
import time
import math
from po_settings import CANVAS_WIDTH, CANVAS_HEIGHT, BAT_HEIGHT, BAT_WIDTH, \
    BALL_SIZE, BALL_SPEED, BAT_SPEED, SCALE, Direction, reverse_direction

speed = 0.0

class Bat():
    def __init__(self, x, y, is_p1):
        self.start_position = (x, y)
        self.x = x
        self.y = y
        self.velocity = 0
        self.autoplay = False
        self.remote = False
        self.is_p1 = is_p1  # P1 is on the left in default coords

    @property
    def position(self):
        return (self.x, self.y)

    def reset_position(self):
        (self.x,self.y) = self.start_position

    @property
    def is_remote(self):
        return self.remote

    @is_remote.setter
    def is_remote(self, remote):
        self.remote = remote

    ''' move due to user input '''
    def user_move(self, dir):
        if dir == Direction.UP:
            self.velocity = -BAT_SPEED
        elif dir == Direction.DOWN:
            self.velocity = BAT_SPEED
        elif dir == Direction.NONE:
            self.velocity = 0

    def move(self, ball):
        if self.autoplay:
            # autoplay if ball is heading towards us
            if self.is_p1 == ball.going_left:  
                bat_mid = self.y + BAT_HEIGHT//2
                bx, by = ball.position
                ball_mid = by + BALL_SIZE//2
                diff = ball_mid - bat_mid
                if diff > 10:
                    diff = 10
                elif diff < -10:
                    diff = -10
                self.velocity = diff
            else:
                self.velocity = 0
        self.y = self.y + self.velocity
        if self.y < 0:
            self.y = 0
        if self.y > CANVAS_HEIGHT - BAT_HEIGHT:
            self.y = CANVAS_HEIGHT - BAT_HEIGHT

class Ball():
    def __init__(self, x, y, rand):
        self.start_position = (x, y)
        self.x = float(x)
        self.y = float(y)
        self.rand = rand
        self.moving = True
        self.random_direction()

    def random_direction(self):
        direction = self.rand.uniform(-math.pi/4, math.pi/4)
        self.vx = BALL_SPEED * math.cos(direction)
        self.vy = BALL_SPEED * math.sin(direction)

    @property
    def going_left(self):
        return self.vx < 0

    @property
    def position(self):
        return (int(self.x), int(self.y))

    @position.setter
    def position(self, pos):
        self.x,self.y = pos
        
    @property
    def velocity(self):
        return (self.vx, self.vy)

    @velocity.setter
    def velocity(self, vel):
        self.vx,self.vy = vel

    def reset_position(self, go_left):
        (self.x,self.y) = self.start_position
        self.random_direction()
        if go_left:
            self.vx = -self.vx

    def move(self):
        if self.moving:
            self.x += self.vx
            self.y += self.vy
            if self.y < 0:
                self.y = -self.y
                self.vy = -self.vy
            ymax = CANVAS_HEIGHT - BALL_SIZE
            if self.y > ymax:
                self.y = ymax - (self.y - ymax)
                self.vy = -self.vy

    def died(self):
        if self.x < -BALL_SIZE or self.x > CANVAS_WIDTH:
            return True
        return False

    def check_bat(self, bat):
        bx,by = bat.position
        if self.y + BALL_SIZE < by:
            return False
        if self.y > by + BAT_HEIGHT:
            return False
        if self.going_left:
            if self.x < bx + BAT_WIDTH and self.x > bx:
                self.vx = -self.vx
                return True
            return False
        else:
            right_side = self.x + BALL_SIZE
            if right_side > bx and right_side < bx + BAT_WIDTH:
                self.vx = -self.vx
                return True
            return False

class Model():
    def __init__(self, controller):
        self.controller = controller
        self.lives = 7
        self.paused = False
        self.init_scores()
        self.rand = Random()

        #create game objects
        self.p1_bat = Bat(50,300, True)
        self.p2_bat = Bat(CANVAS_WIDTH-50,300, False)
        self.ball = Ball(CANVAS_WIDTH//2, CANVAS_HEIGHT//2, self.rand)
        self.their_ball = False # do they control the ball at the moment
        self.send_theirs = False
        self.game_running = True
        self.paused = False
        self.won = False
        self.received_msg = False

        # initialized speed measurement (see checkspeed for use)
        self.lastframe = time.time()
        self.framecount = 0
        self.dont_update_speed = True

    def activate(self, serv, autoplay):
        self.starttime = time.time()
        if serv:
            self.our_bat = self.p1_bat
            self.remote_bat = self.p2_bat
            self.we_are_p1 = True
            self.rotate_scene = False
        else:
            self.our_bat = self.p2_bat
            self.remote_bat = self.p1_bat
            self.we_are_p1 = False
            self.rotate_scene = True
            self.controller.rotate_scene()
        self.remote_bat.is_remote = True
        if autoplay:
            self.our_bat.autoplay = True
        self.controller.register_bat(self.p1_bat)
        self.controller.register_bat(self.p2_bat)
        self.controller.register_ball(self.ball)

    def init_scores(self):
        self.scores = [0, 0]
        self.controller.update_scores(self.scores)

    def died(self):
        self.lives = self.lives - 1
        if self.lives == 0:
            self.game_over()
        else:
            self.pause_start(1, "self.new_life()")

    def new_life(self):
        self.ball.reset_position(self.next_ball_goes_left)

    def pause_start(self, pause_time, unpause_function):
        self.paused = True
        self.pause_end_time = time.time() + pause_time
        # register the function to call when we unpause
        self.unpause_function = unpause_function

    def check_pause(self):
        if time.time() > self.pause_end_time:
            self.paused = False
            self.dont_update_speed = True
            # evaluate the registered function
            exec(self.unpause_function)
            
    def game_over(self):
        self.game_running = False
        self.won = False
        self.controller.game_over()

    def restart(self):
        self.init_scores()
        self.reset_board()
        self.dont_update_speed = True
        self.their_ball = False
        self.send_theirs = False

    def reset_board(self):
        self.p1_bat.reset_position()
        self.p2_bat.reset_position()
        self.ball.reset_position(True)
        self.lives = 7
        #self.controller.update_lives(self.lives)
        #self.controller.unregister_objects()
        self.won = False
        self.game_running = True
        self.paused = False

    # moved by user
    def move_bat(self, direction):
        if self.rotate_scene:
            direction = reverse_direction(direction)
        self.our_bat.user_move(direction)

    def remote_bat_update(self, y, vy):
        self.remote_bat.y = y
        self.remote_bat.velocity = vy

    def remote_ball_update(self, pos, velocity):
        if self.their_ball:
            self.ball.position = pos
            self.ball.velocity = velocity
        else:
            if self.we_are_p1:
                # p1 is on the left in default orientation
                if not self.ball.going_left:
                    self.received_msg = True
            else:
                if self.ball.going_left:
                    self.received_msg = True
            

    def move_objects(self):
        self.p1_bat.move(self.ball)
        self.p2_bat.move(self.ball)
        if not self.their_ball:
            self.ball.move()

    def check_ball(self):
        if self.ball.died():
            if self.ball.going_left:
                self.next_ball_goes_left = False
            else:
                self.next_ball_goes_left = True

            if self.ball.going_left == self.we_are_p1:
                #their point
                self.scores[1] += 1
            else:
                #our point
                self.scores[0] += 1
            self.died()
            return
        if self.we_are_p1:
            # p1 is on the left in default orientation
            if self.ball.going_left:
                self.their_ball = False
                self.received_msg = False
            else:
                if self.received_msg:
                    self.their_ball = True
        else:
            # we are p2, on the right
            if not self.ball.going_left:
                # going right
                self.their_ball = False
                self.received_msg = False
            else:
                if self.received_msg:
                    self.their_ball = True

        if self.their_ball:
            return
        if self.ball.going_left:
            self.ball.check_bat(self.p1_bat)
        else:
            self.ball.check_bat(self.p2_bat)

    ''' adjust game speed so it's more or less the same on different machines '''
    def checkspeed(self):
        global speed
        speed = 1
        return
        self.framecount = self.framecount + 1
        # only check every ten frames                                                        
        if self.framecount == 1:
            now = time.time()
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
                speed = 60 * elapsed
            else:
                # use an EWMA to damp speed changes and avoid excessive jitter               
                speed = speed * 0.9 + 0.1 * 60 * elapsed
        
    def update(self):
        #xxx remote me
        #if time.time() - self.starttime < 10:
        #    return
        time.sleep(0.01)
        if self.game_running and not self.paused:
            self.move_objects()
            self.controller.update_bat(self.our_bat)
            self.check_ball()
            if not self.their_ball:
                self.controller.update_ball(self.ball)
            self.checkspeed()
        elif self.paused:
            self.check_pause()
