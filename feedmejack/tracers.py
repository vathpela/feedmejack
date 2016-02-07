#!/usr/bin/python3

from .gcode import *
from .xyz import *

class ArcBox(object):
    def __init__(self, start, top_left, bottom_right, center, tool=0.8):
        self._start = start
        self._top_left = top_left
        self._bottom_right = bottom_right
        self._center = center
        self._tool = float(tool)

    @property
    def tool(self):
        return self._tool

    @property
    def start(self):
        return self._start

    @property
    def top_left(self):
        return self._top_left

    @property
    def bottom_right(self):
        return self._bottom_right

    @property
    def center(self):
        return self._center

    @property
    def top_right(self):
        return Coord(bottom_right.x, top_left.y)

    @property
    def path(self):
        for x in self.fill():
            yield str(x)

    def __str__(self):
        s = ""
        for p in self.path:
            s = "%s\n%s" % (s, p)
        s = "%s\n" % (s,)
        return s

    def __repr__(self):
        return self.__str__()

    @property
    def path_width(self):
        return self._tool / 1.25

    @property
    def feed_rate(self):
        return 1000.0 / (80.0 / self._tool)

    def fill(self):
        return [g for g in
                [G1(end=self.start, f=self.feed_rate),]]
        #         G3(end=self.

__all__ = ['ArcBox']
