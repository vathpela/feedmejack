#!/usr/bin/python3

from xyz import *

class Box(object):
    def __init__(self, xy_min, xy_max, tool=0.0):
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
    def __init__(self, xyz_min, xyz_max, tool=0.0):
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

class Circle(object):
    _strname = "Circle"
    def __init__(self, center, radius, tool=0.0):
        self.center = center
        self.radius = abs(radius)
        self.tool = float(tool)

    def __str__(self):
        return "%s(%s,%s)" % (self._strname, self.center, self.radius)

    def __contains__(self, point):
        d = abs(point.distance(self.center))
        if self.tool:
            r = self.radius + ( self.tool / 2 )
            if d <= r:
                return True
        else:
            r = self.radius
            if d >= self.radius * 0.99:
                return True
            if d <= self.radius * 1.01:
                return True
        return False

class Plate(Circle):
    _strname = "Plate"

    def __contains__(self, point):
        t2 = self.tool / 2
        d = abs(point.distance(self.center))
        if d <= self.radius + t2:
            return True
        return False

class Ball(Plate):
    _strname = "Ball"
    # point.distance() makes this magical

__all__ = ['Cube', 'Box', 'Circle', 'Plate', 'Ball']

if __name__ == '__main__':
    p = Plate(XY(10,10), 2)
    print("%s with tool 0" % (p,))
    for point in [XY(x,y) for y in range(8,13) for x in range(8,13)]:
        print("%s in %s: %s" % (point, p, point in p))
    print("%s with tool 0.8" % (p,))
    p = Plate(XY(10,10), 2, tool=0.8)
    for point in [XY(x,y) for y in range(8,13) for x in range(8,13)]:
        print("%s in %s: %s" % (point, p, point in p))

    b = Ball(XYZ(10,10,10), 2)
    print("b.center: %s" % (b.center,))
    print("%s with tool 0" % (b,))
    raster = []
    for point in [XYZ(x,y,z) for z in range(8,13)
                             for y in range(8,13)
                             for x in range(8,13)]:
        print("%s in %s: %s" % (point, b, point in b))
        if point in b:
            raster.append(point)

    for z in range(12,7,-1):
        zr = []
        for p in [XYZ(x,y,z) for y in range(8,13) for x in range(8,13)]:
            for point in raster:
                if point == p:
                    zr.append(p)
        print("%s" % (zr,))

    b = Ball(XYZ(10,10,10), 2, tool=0.8)
    print("b.center: %s" % (b.center,))
    print("%s with tool 0.8" % (b,))
    raster = []
    for point in [XYZ(x,y,z) for z in range(8,13)
                             for y in range(8,13)
                             for x in range(8,13)]:
        print("%s in %s: %s" % (point, b, point in b))
        if point in b:
            raster.append(point)

    for z in range(12,7,-1):
        zr = []
        for p in [XYZ(x,y,z) for y in range(8,13) for x in range(8,13)]:
            for point in raster:
                if point == p:
                    zr.append(p)
        print("%s" % (zr,))
