#!/usr/bin/python3

from xyz import *

class Box(object):
    def __init__(self, xy_min, xy_max, tool=0.8):
        self.xy_min = xy_min
        self.xy_max = xy_max
        self.tool = tool

    def __str__(self):
        return "Box(%s,%s)" % (self.xy_min, self.xy_max)

    def __contains__(self, point):
        tw = float(self.tool) / 2.0
        if float(point.x) + tw < self.xy_min.x:
            return False
        if float(point.x) - tw > self.xy_max.x:
            return False
        if float(point.y) + tw < self.xy_min.y:
            return False
        if float(point.y) - tw > self.xy_max.y:
            return False
        return True

class Cube(object):
    def __init__(self, xyz_min, xyz_max, tool=0.8):
        if not hasattr(xyz_min, 'z'):
            raise ValueError("xyz_min has no z dimension")
        if not hasattr(xyz_max, 'z'):
            raise ValueError("xyz_max has no z dimension")
        self.xyz_min = xyz_min
        self.xyz_max = xyz_max
        self.tool = tool

    def __str__(self):
        return "Cube(%s,%s)" % (self.xyz_min, self.xyz_max)

    def __contains__(self, point):
        tw = float(self.tool) / 2.0
        box = Box(self.xyz_min, self.xyz_max, self.tool)
        if not point in box:
            return False
        if not hasattr(point, 'z'):
            return True
        if float(point.z) < self.xyz_min.z:
            return False
        if float(point.z) > self.xyz_max.z:
            return False
        return True

__all__ = ['Cube', 'Box']
