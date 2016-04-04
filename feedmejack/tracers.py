#!/usr/bin/python3

from .gcode import *
from .xyz import *
from .shapes import *
from .rasters import *
from .masks import *

class ArcBox(object):
    def __init__(self, start, box, arc, tool, fill=True):
        self._start = start
        self._top_left = top_left
        self._bottom_right = bottom_right
        self._center = center
        self._tool = tool
        self._fill = fill

        self._box = box
        self._arc = arc

    @property
    def tool(self):
        return self._tool

    @property
    def box(self):
        return self._box

    @property
    def arc(self):
        return self._arc

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
        return xyz.XY(bottom_right.x, top_left.y)

    @property
    def fill(self):
        return bool(self._fill)

    @property
    def path(self):
        for x in self.trace():
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
        return self.tool.width

    @property
    def feed_rate(self):
        return 1000.0 / (80.0 / self.tool.width)

    def trace_perimeter(self, start):
        m = masks.ShapeMask(*self.box)
        ar = rasters.ArcRasterizer(arc=self.arc, tool=self.tool, mask=m)
        p = ar.points

        def is_colinear(segment0, segment1):
            import pdb
            pdb.set_trace()



    def trace(self):
        if hasattr(self.start, 'z'):
            # XXX find an appropriate way to set Z backoff for our device...
            yield G0(end={'z':self.start.z + 30})
            p = xyz.XYZ(self.start.x, self.start.y, self.start.z+30)
            yield G0(end=p)
            p.z = self.start.z * 1.05
            yield G0(end=p)
            yield G1(end=self.start.z, f=self.feed_rate)

        return [g for g in
                [G1(end=self.start, f=self.feed_rate),]]
        #         G3(end=self.

__all__ = ['ArcBox']
