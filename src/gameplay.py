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

import pygame

import gamelogic

def draw_ball(surface, state, obj):
    width, height = surface.get_size()

    color = pygame.Color(255, 127, 0)

    left = width * obj.x / state.width
    right = width * (obj.x + obj.width) / state.width
    top = height * obj.y / state.height
    bottom = height * (obj.y + obj.height) / state.height

    rect = pygame.Rect(left, top, right-left, bottom-top)

    thickness = width / state.width

    pygame.draw.ellipse(surface, color, rect, thickness)

def draw_plunger(surface, state, obj):
    width, height = surface.get_size()

    color = pygame.Color(0, 196, 0)

    left = width * obj.x / state.width
    right = width * (obj.x + obj.width) / state.width
    top = height * obj.y / state.height
    bottom = height * (obj.y + obj.height) / state.height

    rect = pygame.Rect(left, top, right-left, bottom-top)

    left_pt = (left, (top+bottom)/2)
    right_pt = (right, (top+bottom)/2)
    top_pt = ((left+right)/2, top)
    bottom_pt = ((left+right)/2, bottom)

    if obj.direction == gamelogic.UP:
        tip = top_pt
        back = bottom_pt
        side1 = left_pt
        side2 = right_pt
    elif obj.direction == gamelogic.DOWN:
        tip = bottom_pt
        back = up_pt
        side1 = left_pt
        side2 = right_pt
    elif obj.direction == gamelogic.LEFT:
        tip = left_pt
        back = right_pt
        side1 = top_pt
        side2 = bottom_pt
    elif obj.direction == gamelogic.DOWN:
        tip = right_pt
        back = left_pt
        side1 = top_pt
        side2 = bottom_pt

    thickness = width / state.width

    pygame.draw.line(surface, color, tip, back, thickness)
    pygame.draw.line(surface, color, tip, side1, thickness)
    pygame.draw.line(surface, color, tip, side2, thickness)
    pygame.draw.line(surface, color, side1, side2, thickness)

    pygame.draw.rect(surface, pygame.Color(0, 64, 0), rect, thickness)

object_draw_functions = {
    gamelogic.Ball: draw_ball,
    gamelogic.Plunger: draw_plunger,
    }

def draw_unknown(surface, state, obj):
    if isinstance(obj, gamelogic.Moveable):
        width, height = surface.get_size()

        color = pygame.Color(255, 0, 0)

        left = width * obj.x / state.width
        right = width * (obj.x + obj.width) / state.width
        top = height * obj.y / state.height
        bottom = height * (obj.y + obj.height) / state.height

        thickness = width / state.width

        pygame.draw.line(surface, color, (left, top), (right, top), thickness)
        pygame.draw.line(surface, color, (left, bottom), (right, bottom), thickness)

        pygame.draw.line(surface, color, (left, top), (left, bottom), thickness)
        pygame.draw.line(surface, color, (right, top), (right, bottom), thickness)

        pygame.draw.line(surface, color, (left, top), (right, bottom), thickness)
        pygame.draw.line(surface, color, (left, bottom), (right, top), thickness)

def draw_object(surface, state, obj):
    try:
        f = object_draw_functions[type(obj)]
    except KeyError:
        f = draw_unknown
    f(surface, state, obj)

def draw(surface, state):
    width, height = surface.get_size()

    surface.fill(pygame.Color(0, 0, 0))

    # draw a grid background for now
    gridcolor = pygame.Color(30, 30, 30)
    for i in range(state.xtiles):
        pygame.draw.line(surface, gridcolor, (width * i / state.xtiles, 0), (width * i / state.xtiles, height), (width / state.width))
    for i in range(state.ytiles):
        pygame.draw.line(surface, gridcolor, (0, height * i / state.ytiles), (width, height * i / state.ytiles), (height / state.height))

    for obj in state.objects:
        draw_object(surface, state, obj)

def run(screen, state):
    width, height = screen.get_size()

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(0)
    pygame.event.set_grab(True)

    try:
        dx_rem = dy_rem = 0

        while 1:
            clock.tick(50)

            inputs = gamelogic.Inputs()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return 0
                elif event.type == pygame.MOUSEMOTION:
                    dx, dy = event.rel
                    inputs.dx += dx
                    inputs.dy += dy

            inputs.dx, dx_rem = divmod(inputs.dx * state.width + dx_rem, width)
            inputs.dy, dy_rem = divmod(inputs.dy * state.height + dy_rem, height)

            requests = state.advance(inputs)

            draw(screen, state)
            pygame.display.flip()
    finally:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(1)

