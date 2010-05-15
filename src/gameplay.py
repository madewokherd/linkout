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

def draw(surface, state):
    width, height = surface.get_size()

    surface.fill(pygame.Color(0, 0, 0))

    # draw a grid background for now
    gridcolor = pygame.Color(30, 30, 30)
    for i in range(state.xtiles):
        pygame.draw.line(surface, gridcolor, (width * i / state.xtiles, 0), (width * i / state.xtiles, height), (width / state.width))
    for i in range(state.ytiles):
        pygame.draw.line(surface, gridcolor, (0, height * i / state.ytiles), (width, height * i / state.ytiles), (height / state.height))

def run(screen, state):
    clock = pygame.time.Clock()

    while 1:
        clock.tick(50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0

        state, requests = state.next_state()

        draw(screen, state)
        pygame.display.flip()

