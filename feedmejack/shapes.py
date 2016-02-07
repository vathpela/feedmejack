#!/usr/bin/python3

from xyz import *

class Box(object):
    def __init__(self, xy_min, xy_max):
        self.xy_min = xy_min
        self.xy_max = xy_max

    def __str__(self):
        return "Box(%s,%s)" % (self.xy_min, self.xy_max)

    def __contains__(self, point):
        if float(point.x) < self.xy_min.x:
            return False
        if float(point.x) > self.xy_max.x:
            return False
        if float(point.y) < self.xy_min.y:
            return False
        if float(point.y) > self.xy_max.y:
            return False
        return True

class Cube(object):
    def __init__(self, xyz_min, xyz_max):
        if not hasattr(xyz_min, 'z'):
            raise ValueError("xyz_min has no z dimension")
        if not hasattr(xyz_max, 'z'):
            raise ValueError("xyz_max has no z dimension")
        self.xyz_min = xyz_min
        self.xyz_max = xyz_max

    def __str__(self):
        return "Cube(%s,%s)" % (self.xyz_min, self.xyz_max)

    def __contains__(self, point):
        box = Box(self.xyz_min, self.xyz_max)
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
    def __init__(self, center, radius):
        self.center = center
        self.radius = abs(radius)

    def __str__(self):
        return "%s(%s,%s)" % (self._strname, self.center, self.radius)

    def __contains__(self, point):
        d = abs(point.distance(self.center))
        r = self.radius
        # la la la why not...
        if d >= self.radius * 0.95:
            return True
        if d <= self.radius * 1.05:
            return True
        return False

class Plate(Circle):
    _strname = "Plate"

    def __contains__(self, point):
        d = abs(point.distance(self.center))
        if d <= self.radius:
            return True
        return False

class Ball(Plate):
    _strname = "Ball"
    # point.distance() makes this magical

__all__ = ['Cube', 'Box', 'Circle', 'Plate', 'Ball']

if __name__ == '__main__':
    p = Plate(XY(10,10), 2)
    print("%s" % (p,))
    for point in [XY(x,y) for y in range(8,13) for x in range(8,13)]:
        print("%s in %s: %s" % (point, p, point in p))

    b = Ball(XYZ(10,10,10), 2)
    print("%s" % (b,))
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

    b = Ball(XYZ(10,10,10), 2)
    print("%s" % (b,))
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
