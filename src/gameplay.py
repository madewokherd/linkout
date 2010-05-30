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

import pygame

import gamelogic

def draw_ball(surface, state, obj):
    width, height = surface.get_size()

    color = pygame.Color(255, 127, 0)

    left = width * obj.x / state.width
    right = width * (obj.x + obj.width) / state.width
    top = height * obj.y / state.height
    bottom = height * (obj.y + obj.height) / state.height

    thickness = width / state.width

    top_pt = ((left+right)/2-thickness, top)
    bottom_pt = ((left+right)/2-thickness, bottom)

    pygame.draw.line(surface, color, top_pt, bottom_pt, thickness)

    pygame.draw.ellipse(surface, color, pygame.Rect(left, top, (right-left)/2, (bottom-top)/2), thickness)

    pygame.draw.ellipse(surface, color, pygame.Rect((left+right)/2, top, (right-left)/2, (bottom-top)/2), thickness)

def draw_plunger(surface, state, obj):
    width, height = surface.get_size()

    color = pygame.Color(0, 196, 0)

    left = width * obj.x / state.width
    right = width * (obj.x + obj.width) / state.width
    top = height * obj.y / state.height
    bottom = height * (obj.y + obj.height) / state.height

    rect = pygame.Rect(left, top, right-left, bottom-top)

    x_center = (left+right)/2
    x_mult = (right-left)/2

    y_center = (top+bottom)/2
    y_mult = (bottom-top)/2

    sin_angle = math.sin(obj.angle)
    cos_angle = math.cos(obj.angle)

    tip = (int(x_center+x_mult*cos_angle), int(y_center+y_mult*sin_angle))
    back = (int(x_center-x_mult*cos_angle), int(y_center-y_mult*sin_angle))
    side1 = (int(x_center+x_mult*sin_angle*0.8), int(y_center-y_mult*cos_angle*0.8))
    side2 = (int(x_center-x_mult*sin_angle*0.8), int(y_center+y_mult*cos_angle*0.8))

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

def draw_paused(surface):
    if pygame.font:
        font = pygame.font.Font(None, 48)
        text = font.render("Paused", 1, (240, 240, 240))
        textpos = text.get_rect(centerx=surface.get_width()/2, centery=surface.get_height()/2)
        surface.blit(text, textpos)

def run(screen, state):
    width, height = screen.get_size()

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    try:
        dx_rem = dy_rem = 0
        buttons_pressed = set()
        keys_pressed = set()
        paused = False

        while 1:
            clock.tick(50)

            inputs = gamelogic.Inputs()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
                elif event.type == pygame.KEYDOWN:
                    keys_pressed.add(event.key)
                    if event.key == pygame.K_ESCAPE:
                        return 0
                    elif event.key in (pygame.K_PAUSE, pygame.K_p):
                        paused = not paused
                        pygame.mouse.set_visible(paused)
                        pygame.event.set_grab(not paused)
                elif event.type == pygame.KEYUP:
                    keys_pressed.remove(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    dx, dy = event.rel
                    inputs.dx += dx
                    inputs.dy += dy
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    buttons_pressed.add(event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    buttons_pressed.remove(event.button)

            if pygame.K_w in keys_pressed: inputs.dy -= 6
            if pygame.K_a in keys_pressed: inputs.dx -= 6
            if pygame.K_s in keys_pressed: inputs.dy += 6
            if pygame.K_d in keys_pressed: inputs.dx += 6

            if pygame.K_UP in keys_pressed: inputs.dy -= 6
            if pygame.K_LEFT in keys_pressed: inputs.dx -= 6
            if pygame.K_DOWN in keys_pressed: inputs.dy += 6
            if pygame.K_RIGHT in keys_pressed: inputs.dx += 6

            inputs.dx, dx_rem = divmod(inputs.dx * state.width + dx_rem, width)
            inputs.dy, dy_rem = divmod(inputs.dy * state.height + dy_rem, height)
            inputs.buttons_pressed = buttons_pressed

            if not paused:
                requests = state.advance(inputs)

            draw(screen, state)

            if paused:
                draw_paused(screen)

            pygame.display.flip()
    finally:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

