# Copyright (c) 2010 Vincent Povirk
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import math
import random

UP = "UP"
LEFT = "LEFT"
RIGHT = "RIGHT"
DOWN = "DOWN"

direction_angles = {
    UP: math.pi * 0.5,
    LEFT: math.pi,
    RIGHT: 0.8,
    DOWN: math.pi * 1.5,
    }

ABORT = "ABORT"
BLOCK = "BLOCK"
DELETE = "DELETE"
ADD = "ADD"

class Inputs(object):
    dx = 0
    dy = 0
    buttons_pressed = ()

class GameObject(object):
    physical = False    # True if this object has a location in space
    dead = False        # True if this object should be removed before the next frame
    solid = False       # True if this object gets in the way of moving objects
    player_weapon = 0   # Non-zero weapon power if this is dangerous to enemies
    sprite = None       # Not used by this module, may be a pixmap to draw this

    def kill(self):
        self.dead = True

class ScreenEdge(GameObject):
    solid = True

    def __init__(self, name):
        self.name = name

TOP_EDGE = ScreenEdge("TOP")
BOTTOM_EDGE = ScreenEdge("BOTTOM")
LEFT_EDGE = ScreenEdge("LEFT")
RIGHT_EDGE = ScreenEdge("RIGHT")

class Tile(GameObject):
    physical = True

class Ground(Tile):
    pass

class Wall(Tile):
    solid = True

class Moveable(GameObject):
    physical = True
    xerror = 0.0
    yerror = 0.0

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

    def move_left(self, state, dx, dy):
        newx = self.x - 1

        if newx < 0:
            ret = self.collide(LEFT_EDGE, LEFT, state, dx, dy)
            if ret:
                return ret

        for obj in state.objects:
            if obj is not self and \
               isinstance(obj, Moveable) and \
               obj.x <= newx < obj.x + obj.width and \
               max(self.y, obj.y) < min(self.y + self.height, obj.y + obj.height):
                ret = self.collide(obj, LEFT, state, dx, dy)
                obj.collide(self, RIGHT, state, 0, 0)
                if ret:
                    return ret

        self.x = newx

    def move_right(self, state, dx, dy):
        newx = self.x + 1
        newedge = newx + self.width

        if newedge >= state.width:
            ret = self.collide(RIGHT_EDGE, RIGHT, state, dx, dy)
            if ret:
                return ret

        for obj in state.objects:
            if obj is not self and \
               isinstance(obj, Moveable) and \
               obj.x <= newedge < obj.x + obj.width and \
               max(self.y, obj.y) < min(self.y + self.height, obj.y + obj.height):
                ret = self.collide(obj, RIGHT, state, dx, dy)
                obj.collide(self, LEFT, state, 0, 0)
                if ret:
                    return ret

        self.x = newx

    def move_up(self, state, dx, dy):
        newy = self.y - 1

        if newy < 0:
            ret = self.collide(TOP_EDGE, UP, state, dx, dy)
            if ret:
                return ret

        for obj in state.objects:
            if obj is not self and \
               isinstance(obj, Moveable) and \
               obj.y <= newy < obj.y + obj.height and \
               max(self.x, obj.x) < min(self.x + self.width, obj.x + obj.width):
                ret = self.collide(obj, UP, state, dx, dy)
                obj.collide(self, DOWN, state, 0, 0)
                if ret:
                    return ret

        self.y = newy

    def move_down(self, state, dx, dy):
        newy = self.y + 1
        newedge = newy + self.height

        if newedge >= state.height:
            ret = self.collide(BOTTOM_EDGE, DOWN, state, dx, dy)
            if ret:
                return ret

        for obj in state.objects:
            if obj is not self and \
               isinstance(obj, Moveable) and \
               obj.y <= newedge < obj.y + obj.height and \
               max(self.x, obj.x) < min(self.x + self.width, obj.x + obj.width):
                ret = self.collide(obj, DOWN, state, dx, dy)
                obj.collide(self, UP, state, 0, 0)
                if ret:
                    return ret

        self.y = newy

    def move(self, state, dx, dy):
        if isinstance(dx, float):
            # FIXME: Is this logic subject to weird floating point errors?
            dx, self.xerror = divmod(dx+self.xerror, 1.0)
            dx = int(dx)

        if isinstance(dy, float):
            dy, self.yerror = divmod(dy+self.yerror, 1.0)
            dy = int(dy)

        steps = max(abs(dx), abs(dy))

        x = y = 0

        for i in range(1, steps+1):
            newx = dx * i / steps
            step_dx = newx - x
            if step_dx == -1:
                if self.move_left(state, dx-x, dy-y) == ABORT:
                    return
            elif step_dx == 1:
                if self.move_right(state, dx-x, dy-y) == ABORT:
                    return
            x = newx

            newy = dy * i / steps
            step_dy = newy - y
            if step_dy == -1:
                if self.move_up(state, dx-x, dy-y) == ABORT:
                    return
            elif step_dy == 1:
                if self.move_down(state, dx-x, dy-y) == ABORT:
                    return
            y = newy

    def moveto(self, state, x, y):
        return self.move(state, x-self.x, y-self.y)

    def distance_to_touch(self, oth):
        if self.x + self.width < oth.x:
            dx = oth.x - self.x - self.width
        elif self.x > oth.x + oth.width:
            dx = oth.x + oth.width - self.x
        else:
            dx = 0

        if self.y + self.height < oth.y:
            dy = oth.y - self.y - self.height
        elif self.y > oth.y + oth.height:
            dy = oth.y + oth.height - self.y
        else:
            dy = 0

        return dx, dy

    def collide(self, oth, direction, state, dx, dy):
        pass

class ForegroundWall(Moveable):
    physical = True
    solid = True

def angle_to_offset(dx, dy):
        try:
            if dx > 0:
                return math.atan(dy/dx)
            else:
                return math.atan(dy/dx) + math.pi
        except ZeroDivisionError:
            if dy < 0:
                return math.pi * 1.5
            else:
                return math.pi * 0.5

class Turnable(Moveable):

    def __init__(self, *args):
        Moveable.__init__(self, *args)
        self.angle = 0.0

    def turn_to_offset(self, dx, dy):
        self.angle = angle_to_offset(dx, dy)

    def turn_by_offset(self, dx, dy, radius):
        if 0 == dx and 0 == dy:
            return
        x = radius * math.cos(self.angle)
        y = radius * math.sin(self.angle)
        x = x + dx
        y = y + dy
        if 0 == dx and 0 == dy:
            return
        self.turn_to_offset(x, y)

    def turn_away_from(self, oth):
        dx = (self.x + self.width/2) - (oth.x + oth.width/2)
        dy = (self.y + self.height/2) - (oth.y + oth.height/2)
        self.turn_to_offset(dx, dy)

class Ball(Turnable):
    player_weapon = 1

    def __init__(self, x=0, y=0, width=8, height=8, angle=math.atan(2), speed=4):
        Turnable.__init__(self, x, y, width, height)
        self.speed = speed
        self.angle = angle

    def copy(self):
        return Ball(self.x, self.y, self.width, self.height, self.dx, self.dy, self.speed)

    def advance(self, state, inputs):
        self.move(state, self.speed * math.cos(self.angle), self.speed * math.sin(self.angle))

        return ()

    def collide(self, oth, direction, state, dx, dy):
        if oth.solid:
            if (direction == LEFT and math.cos(self.angle) < 0) or\
               (direction == RIGHT and math.cos(self.angle) > 0):
                self.angle = math.pi - self.angle
            elif (direction == UP and math.sin(self.angle) < 0) or\
                 (direction == DOWN and math.sin(self.angle) > 0):
                self.angle = math.pi*2 - self.angle
            return ABORT

class FairyBall(Ball):
    def advance(self, state, inputs):
        if 1 in inputs.buttons_pressed:
            for oth in state.objects:
                if isinstance(oth, Plunger):
                    self.x = (oth.x + oth.width/2) - self.width / 2
                    self.y = (oth.y + oth.height/2) - self.height / 2
                    return ()

        return Ball.advance(self, state, inputs)

    def collide(self, oth, direction, state, dx, dy):
        if isinstance(oth, Plunger):
            self.angle = oth.angle
        else:
            Ball.collide(self, oth, direction, state, dx, dy)

class Boomerang(Ball):
    caught = None
    uncaught = None

    def advance(self, state, inputs):
        if self.caught:
            if 1 in inputs.buttons_pressed:
                self.uncaught = self.caught
                self.caught = None
            else:
                self.x = (self.caught.x + self.caught.width/2) - self.width / 2
                self.y = (self.caught.y + self.caught.height/2) - self.height / 2
                return ()

        if self.uncaught:
            dx, dy = self.distance_to_touch(self.uncaught)
            if dx != 0 or dy != 0:
                self.uncaught = None

        return Ball.advance(self, state, inputs)

    def collide(self, oth, direction, state, dx, dy):
        if isinstance(oth, Plunger):
            self.angle = oth.angle
            if oth is not self.uncaught:
                self.caught = oth
        elif oth.solid:
            if (direction == LEFT and math.cos(self.angle) < 0) or\
               (direction == RIGHT and math.cos(self.angle) > 0) or \
               (direction == UP and math.sin(self.angle) < 0) or \
               (direction == DOWN and math.sin(self.angle) > 0):
                self.angle = self.angle + math.pi
            return ABORT

class Plunger(Turnable):
    "Plunger will follow the mouse"
    solid = True
    angle = 0.0
    turn_radius = 12.0

    def __init__(self, x, y, width, height, direction=UP):
        Moveable.__init__(self, x, y, width, height)
        self.angle = direction_angles[direction]

    def copy(self):
        return Plunger(self.x, self.y, self.width, self.height, direction)

    def advance(self, state, inputs):
        if 3 not in inputs.buttons_pressed:
            self.move(state, inputs.dx, inputs.dy)

        if 1 not in inputs.buttons_pressed:
            self.turn_by_offset(inputs.dx, inputs.dy, self.turn_radius)

        return ()

    def collide(self, oth, direction, state, dx, dy):
        if oth.solid:
            return BLOCK

class DaggerBit(Moveable):
    player_weapon = 1

    def __init__(self, owner, width, height, distance):
        Moveable.__init__(self, 0, 0, width, height)
        self.owner = owner
        self.distance = distance
        self.x, self.y = self.ideal_position()

    def ideal_position(self):
        x = (self.owner.x + self.owner.width / 2) + self.distance * math.cos(self.owner.angle) - self.width / 2
        y = (self.owner.y + self.owner.height / 2) + self.distance * math.sin(self.owner.angle) - self.height / 2
        return int(x), int(y)

    def advance(self, state, inputs):
        x, y = self.ideal_position()
        self.moveto(state, x, y)
        return ()

class Robot(Moveable):
    "Robot will move towards the plunger"
    solid = True

    def __init__(self, x, y, width, height, speed, deadly=True):
        Moveable.__init__(self, x, y, width, height)
        self.speed = speed
        self.deadly = deadly

    def copy(self):
        return Robot(self.x, self.y, self.width, self.height, speed)

    def advance(self, state, inputs):
        for obj in state.objects:
            if isinstance(obj, Plunger):
                dx = obj.x + obj.width / 2 - self.x - self.width / 2
                dy = obj.y + obj.height / 2 - self.y - self.height / 2
                if 0 == dy == dx:
                    return ()
                elif abs(dx) > abs(dy):
                    self.move(state, min(self.speed, abs(dx)) * cmp(dx, 0), 0)
                else:
                    self.move(state, 0, min(self.speed, abs(dy)) * cmp(dy, 0))

        return ()

    def collide(self, oth, direction, state, dx, dy):
        if oth.player_weapon >= 1:
            self.kill()
        if self.deadly and isinstance(oth, Plunger):
            oth.kill()
        if oth.solid:
            return ABORT

class Generator(GameObject):
    "Spawns objects when there are fewer than N on the screen"

    def __init__(self, obj_type, max_objects, width, height, min_distance_sq, *args):
        self.obj_type = obj_type
        self.max_objects = max_objects
        self.width = width
        self.height = height
        self.min_distance_sq = min_distance_sq
        self.args = args

    def advance(self, state, inputs):
        count = 0

        for obj in state.objects:
            if isinstance(obj, self.obj_type):
                count += 1

        if count < self.max_objects:
            x = state.random.randint(0, state.width - self.width)
            y = state.random.randint(0, state.height - self.height)

            for obj in state.objects:
                if isinstance(obj, Moveable) and \
                    (((x + self.width/2) - (obj.x + obj.width/2))**2 +
                     ((y + self.height/2) - (obj.y + obj.height/2))**2) < self.min_distance_sq:
                    return ()

            return ((ADD, self.obj_type(x, y, self.width, self.height, *self.args)),)

        return ()

class EscalatingGenerator(Generator):
    "Spawns objects when there are fewer than N on the screen. N increases as time goes on."

    def __init__(self, obj_type, max_objects, escalation_time, width, height, min_distance_sq, *args):
        Generator.__init__(self, obj_type, max_objects, width, height, min_distance_sq, *args)
        self.escalation_time = escalation_time
        self.time_since_escalation = 0

    def advance(self, state, inputs):
        self.time_since_escalation += 1

        if self.time_since_escalation >= self.escalation_time:
            self.time_since_escalation = 0
            self.max_objects += 1

        return Generator.advance(self, state, inputs)

class State(object):
    "This object represents the state of the game at a frame."

    def __init__(self):
        self.tilewidth = 16
        self.tileheight = 16
        self.xtiles = 16
        self.ytiles = 15
        self.width = self.tilewidth * self.xtiles
        self.height = self.tileheight * self.ytiles

        self.objects = []

        self.random = random.Random()
        self.random.seed()

    def advance(self, inputs):
        """Returns the state at the next frame and any control requests (sounds,
         quit, etc.)"""
        to_add = []

        for obj in self.objects:
            reqs = obj.advance(self, inputs)
            for i in reqs:
                if isinstance(i, tuple):
                    if i[0] == ADD:
                        to_add.append(i[1])

        for i in range(len(self.objects)-1, -1, -1):
            if self.objects[i].dead:
                self.objects.pop(i)

        for obj in to_add:
            self.objects.append(obj)

        return ()

