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

import sys

import gamelogic
import gameplay

def main(argv):
    pygame.init()
    screen = pygame.display.set_mode((580,480))

    state = gamelogic.State()

    player = gamelogic.Plunger(128, 0, 16, 16, gamelogic.UP)
    state.objects.append(player)

    #state.objects.append(gamelogic.Ball(128, 0, 8, 8))
    #state.objects.append(gamelogic.Generator(gamelogic.Robot, 3, 16, 16, 12544, 2, False))
    state.objects.append(gamelogic.EscalatingGenerator(gamelogic.Robot, 0, 750, 16, 16, 12544, 2, True))

    for i in range(8, 26, 4):
        state.objects.append(gamelogic.DaggerBit(player, 3, 3, i))

    gameplay.run(screen, state)

if __name__ == '__main__':
    sys.exit(main(sys.argv))

