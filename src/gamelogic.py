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

import random

UP = "UP"
LEFT = "LEFT"
RIGHT = "RIGHT"
DOWN = "DOWN"

ABORT = "ABORT"
BLOCK = "BLOCK"
DELETE = "DELETE"
ADD = "ADD"

class Inputs(object):
    dx = 0
    dy = 0
    buttons_pressed = ()

class ScreenEdge(object):
    def __init__(self, name):
	self.name = name

TOP_EDGE = ScreenEdge("TOP")
BOTTOM_EDGE = ScreenEdge("BOTTOM")
LEFT_EDGE = ScreenEdge("LEFT")
RIGHT_EDGE = ScreenEdge("RIGHT")

class Moveable(object):
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

    def collide(self, oth, direction, state, dx, dy):
        pass

class Ball(Moveable):
    def __init__(self, x=0, y=0, width=8, height=8, dx=2, dy=4):
        Moveable.__init__(self, x, y, width, height)
        self.dx = dx
        self.dy = dy

    def copy(self):
        return Ball(self.x, self.y, self.width, self.height, self.dx, self.dy)

    def advance(self, state, inputs):
        if 1 in inputs.buttons_pressed:
            for oth in state.objects:
                if isinstance(oth, Plunger):
                    speed = max(abs(self.dx), abs(self.dy))
                    dx = (oth.x + oth.width/2) - (self.x + self.width/2)
                    dy = (oth.y + oth.height/2) - (self.y + self.height/2)
                    if 0 == dy == dx:
                        pass
                    elif abs(dx) > abs(dy):
                        self.dx = speed * cmp(dx, 0)
                        self.dy = (dy * speed // abs(dx))
                    else:
                        self.dy = speed * cmp(dy, 0)
                        self.dx = (dx * speed // abs(dy))

        self.move(state, self.dx, self.dy)

        return ()

    def collide(self, oth, direction, state, dx, dy):
        if isinstance(oth, ScreenEdge) or isinstance(oth, Robot):
            if direction == LEFT:
                self.dx = abs(self.dx)
            elif direction == RIGHT:
                self.dx = -abs(self.dx)
            elif direction == UP:
                self.dy = abs(self.dy)
            elif direction == DOWN:
                self.dy = -abs(self.dy)
            if isinstance(oth, ScreenEdge):
                return ABORT
        elif isinstance(oth, Plunger):
            speed = max(abs(self.dx), abs(self.dy))
            dx = (self.x + self.width/2) - (oth.x + oth.width/2)
            dy = (self.y + self.height/2) - (oth.y + oth.height/2)
            if 0 == dy == dx:
                return
            elif abs(dx) > abs(dy):
                self.dx = speed * cmp(dx, 0)
                self.dy = (dy * speed // abs(dx))
            else:
                self.dy = speed * cmp(dy, 0)
                self.dx = (dx * speed // abs(dy))
            return ABORT

class Plunger(Moveable):
    "Plunger will follow the mouse"

    def __init__(self, x, y, width, height, direction):
        Moveable.__init__(self, x, y, width, height)
        self.direction = direction
        self.dead = False

    def copy(self):
        return Plunger(self.x, self.y, self.width, self.height, direction)

    def advance(self, state, inputs):
        self.move(state, inputs.dx, inputs.dy)

        if self.dead:
            return (DELETE,)
        else:
            return ()

    def collide(self, oth, direction, state, dx, dy):
        if isinstance(oth, ScreenEdge):
            return BLOCK
        if isinstance(oth, Robot):
            self.dead = True

class Robot(Moveable):
    "Robot will move towards the plunger"

    def __init__(self, x, y, width, height, speed):
        Moveable.__init__(self, x, y, width, height)
        self.speed = speed
        self.dead = False

    def copy(self):
        return Robot(self.x, self.y, self.width, self.height, speed)

    def advance(self, state, inputs):
        for obj in state.objects:
            if isinstance(obj, Plunger):
                dx = (obj.x + obj.width/2) - (self.x + self.width/2)
                dy = (obj.y + obj.height/2) - (self.y + self.height/2)
                if 0 == dy == dx:
                    return
                elif abs(dx) > abs(dy):
                    self.move(state, self.speed * cmp(dx, 0), 0)
                else:
                    self.move(state, 0, self.speed * cmp(dy, 0))

        if self.dead:
            return (DELETE,)
        else:
            return ()

    def collide(self, oth, direction, state, dx, dy):
        if isinstance(oth, Ball):
            self.dead = True
        return BLOCK

class Generator(object):
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
        to_delete = []
        to_add = []

        for obj in self.objects:
            reqs = obj.advance(self, inputs)
            for i in reqs:
                if i == DELETE:
                    to_delete.append(obj)
                elif isinstance(i, tuple):
                    if i[0] == ADD:
                        to_add.append(i[1])

        for obj in to_delete:
            self.objects.remove(obj)

        for obj in to_add:
            self.objects.append(obj)

        return ()

