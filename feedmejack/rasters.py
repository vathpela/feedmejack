#!/usr/bin/python3

from .xyz import *
from .masks import *

import math
import pdb

class ArcRasterizer(object):
    def __init__(self, arc, tool, mask=Mask(False)):
        self._arc = arc
        self._tool = tool
        self._mask = mask

    @property
    def arc(self):
        return self._arc

    @property
    def tool(self):
        return self._tool

    @property
    def mask(self):
        return self._mask

    def point(self, theta, p):
        c = self.arc.center
        x = c.x +((p.x-c.x) * math.cos(theta)) + ((c.y-p.y) * math.sin(theta))
        y = c.y +((p.y-c.y) * math.cos(theta)) + ((p.x-c.x) * math.sin(theta))
        return XY(x,y)

    @property
    def points(self):
        def frange(x, y, jump):
            while x < y:
                yield x
                x += jump

        radians = [x for x in frange(0.0, 2*math.pi, 0.001)]
        prev = XY(self.arc.center.x + self.arc.radius, self.arc.center.y)
        if prev in self.mask:
            yield prev
        for r in radians:
            p = self.point(r, prev)
            prev = p
            if p in self.mask:
                yield p

class PlateRasterizer(ArcRasterizer):
    def __init__(self, *args, **kwds):
        ArcRasterizer.__init__(self, *args, **kwds)

    @property
    def points(self):
        def frange(x, y, jump):
            while x < y:
                yield x
                x += jump

        # this is intentionally not a spiral, because GCode doens't support
        # those yet.
        w = self.tool.width
        radians = [x for x in frange(0.0, 2*math.pi, 0.001)]
        radii = [x for x in frange(0.0, self.arc.radius, w * 0.95)]
        for radius in radii:
            prev = XY(self.arc.center.x + radius, self.arc.center.y)
            if prev in self.mask:
                yield prev
            for r in radians:
                p = self.point(r, prev)
                prev = p
                if p in self.mask:
                    yield p
__all__ = ['ArcRasterizer', 'PlateRasterizer']
