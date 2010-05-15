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

TOP_EDGE = "TOP_EDGE"
BOTTOM_EDGE = "BOTTOM_EDGE"
LEFT_EDGE = "LEFT_EDGE"
RIGHT_EDGE = "RIGHT_EDGE"

UP = "UP"
LEFT = "LEFT"
RIGHT = "RIGHT"
DOWN = "DOWN"

ABORT = "ABORT"
BLOCK = "BLOCK"

class Inputs(object):
    dx = 0
    dy = 0

class Moveable(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

    def move_left(self, state, dx, dy):
        if self.x <= 0:
            ret = self.collide(LEFT_EDGE, LEFT, state, dx, dy)
            if ret:
                return ret

        self.x = self.x - 1

    def move_right(self, state, dx, dy):
        if self.x + self.width >= state.width:
            ret = self.collide(RIGHT_EDGE, RIGHT, state, dx, dy)
            if ret:
                return ret

        self.x = self.x + 1

    def move_up(self, state, dx, dy):
        if self.y <= 0:
            ret = self.collide(TOP_EDGE, UP, state, dx, dy)
            if ret:
                return ret

        self.y = self.y - 1

    def move_down(self, state, dx, dy):
        if self.y + self.height >= state.height:
            ret = self.collide(BOTTOM_EDGE, DOWN, state, dx, dy)
            if ret:
                return ret

        self.y = self.y + 1

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
        new_ball = self.copy()

        new_ball.move(state, self.dx, self.dy)

        return (new_ball,), ()

    def collide(self, oth, direction, state, dx, dy):
        if oth in (LEFT_EDGE, RIGHT_EDGE, TOP_EDGE, BOTTOM_EDGE):
            if direction == LEFT:
                self.dx = abs(self.dx)
            elif direction == RIGHT:
                self.dx = -abs(self.dx)
            elif direction == UP:
                self.dy = abs(self.dy)
            elif direction == DOWN:
                self.dy = -abs(self.dy)
            return ABORT

class Plunger(Moveable):
    "Plunger will follow the mouse"

    def copy(self):
        return Plunger(self.x, self.y, self.width, self.height)

    def advance(self, state, inputs):
        new_plunger = self.copy()

        new_plunger.move(state, inputs.dx, inputs.dy)

        return (new_plunger,), ()

    def collide(self, oth, direction, state, dx, dy):
        if oth in (LEFT_EDGE, RIGHT_EDGE, TOP_EDGE, BOTTOM_EDGE):
            return BLOCK

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

    def next_state(self, inputs):
        """Returns the state at the next frame and any control requests (sounds,
         quit, etc.)"""
        state = State()
        requests = []

        for obj in self.objects:
            new_objs, new_reqs = obj.advance(self, inputs)
            state.objects.extend(new_objs)
            requests.extend(new_reqs)

        return state, requests

