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

import os
import sys
import xml.sax
import xml.sax.handler

import pygame

import gamelogic

DEBUG = False

class TileSet(object):
    def __init__(self, tilewidth, tileheight, image):
        self.width = tilewidth
        self.height = tileheight
        self.image = image
        self.tiles = {}

    @staticmethod
    def from_source(source, tilewidth, tileheight):
        image = pygame.image.load(source)
        result = TileSet(tilewidth, tileheight, image)

class MapContentHandler(xml.sax.handler.ContentHandler):
    def startDocument(self):
        self.tilesets = {}
        self.layers = {}
        self.mapattrs = {}
        self.intileset = False
        self.inlayer = False

    def startElement(self, name, attrs):
        if name == 'map':
            self.mapattrs = attrs
            if DEBUG:
                print "start of map"
        elif name == 'tileset':
            self.intileset = True
            self.tilesetattrs = attrs
        elif name == 'image' and self.intileset:
            self.tilesetimage = attrs['source']

    def endElement(self, name):
        if name == 'tileset' and self.intileset:
            source = os.path.normpath(os.path.join(os.path.dirname(self.filename), self.tilesetimage))
            if DEBUG:
                print "found tileset: source=%s" % source
            self.tilesets[self.tilesetattrs['firstgid']] = TileSet.from_source(
                source, self.tilesetattrs['tilewidth'], self.tilesetattrs['tileheight'])

def load(filename):
    filename = os.path.abspath(filename)

    xmlhandler = MapContentHandler()
    xmlhandler.filename = filename

    xml.sax.parse(filename, xmlhandler)

def main(argv):
    global DEBUG
    DEBUG = True

    load(argv[0])

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

