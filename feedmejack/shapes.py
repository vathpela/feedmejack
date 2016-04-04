#!/usr/bin/python3

if __name__ != '__main__':
    from .xyz import XY, XYZ, Line

class Square(object):
    _strname = "Square"
    def __init__(self, xy_min, xy_max):
        self.xy_min = xy_min
        self.xy_max = xy_max

    def __str__(self):
        return "%s(%s,%s)" % (self._strname, self.xy_min, self.xy_max)

    def __contains__(self, point):
        if point.r == 0:
            over = lambda x: x * 1.05
            under = lambda x: x * 0.95
        else:
            over = lambda x: x + point.r
            under = lambda x: x - point.r

        x_min_under = under(self.xy_min.x)
        x_min_over = over(self.xy_min.x)
        x_max_under = under(self.xy_max.x)
        x_max_over = over(self.xy_max.x)
        y_min_under = under(self.xy_min.y)
        y_min_over = over(self.xy_min.y)
        y_max_under = under(self.xy_max.y)
        y_max_over = over(self.xy_max.y)

        if point.x < x_min_under:
            return False
        if point.x > x_max_over:
            return False
        if point.y < y_min_under:
            return False
        if point.y > y_max_over:
            return False

        if point.x > x_min_over and point.x < x_max_under and \
                point.y > y_min_over and point.y < y_max_under:
            return False
        return True

class Box(Square):
    _strname = "Box"
    def __contains__(self, point):
        if point.x + point.r < self.xy_min.x:
            return False
        if point.x - point.r > self.xy_max.x:
            return False
        if point.y + point.r < self.xy_min.y:
            return False
        if point.y - point.r > self.xy_max.y:
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
        if point.z < self.xyz_min.z:
            return False
        if point.z > self.xyz_max.z:
            return False
        return True

class Circle(object):
    """ A Circle is an Arc that never ends... """

    _strname = "Circle"
    def __init__(self, center, radius):
        self.center = center
        self.radius = abs(radius)

    def __str__(self):
        return "%s(%s,%s)" % (self._strname, self.center, self.radius)

    def __contains__(self, point):
        distance = abs(point.distance(self.center))
        cr0 = self.radius
        cr1 = self.radius
        if point.r == 0:
            cr0 *= 0.95
            cr1 *= 1.05

        # la la la why not...
        if distance - point.r >= cr0:
            return True
        if distance + point.r <= cr1:
            return True
        return False

class Arc(Circle):
    """ An Arc is a Circle with a start and end position in radians """

    _strname = "Arc"
    def __init__(self, center, radius, start, end):
        self.center = center
        self.radius = abs(radius)
        self.start = start
        self.end = end

    def __str__(self):
        return "%s(%s,%s,%d,%d)" % (self._strname, self.center, self.radius,
                                    self.start, self.end)

    def theta(self, point):
        return math.acos(point.x / self.radius)

    def within_arc_segment(self, point):
        # now we need to figure out if it's in our arc segment

        # first, how many rads from the tool center does the tool extend
        # lAB = 2piR * d/360
        # === lAB / 2piR = d/360
        # === 360lAB / 2piR = d
        r = point.r
        if point.r == 0:
            # make up something wildly...
            r = self.radius * 1.05 - self.radius * 0.95

        point_r_rads = math.radians((r * 360) / (2*math.pi*self.radius))
        if self.start < self.end:
            min_theta = self.start - point_r_rads
            max_theta = self.end + point_r_rads
        elif self.start >= self.end:
            min_theta = self.end - point_r_rads
            max_theta = self.start + point_r_rads

        # now, what's the position of our point
        theta = self.theta(point)
        if theta >= min_theta and theta <= max_theta:
            return True
        return False

    def is_at_arc_distance(self, point):
        # first figure out if the point is at the right distance...
        distance = abs(point.distance(self.center))
        cr0 = self.radius
        cr1 = self.radius
        if point.r == 0:
            # la la la why not...
            cr0 *= 0.95
            cr1 *= 1.05

        if distance - point.r < cr0:
            return False
        if distance + point.r > cr1:
            return False
        return True

    def __contains__(self, point):
        if self.is_at_arc_distance(point) and self.within_arc_segment(point):
            return True
        return False

class Plate(Circle):
    _strname = "Plate"

    def __contains__(self, point):
        d = abs(point.distance(self.center))
        r = point.r
        if point.r == 0:
            r = self.radius * 1.05 - self.radius * 0.95
        if d - r <= self.radius:
            return True
        return False

class Wedge(Arc):
    _strname = "Wedge"

    def __contains__(self, point):
        d = abs(point.distance(self.center))
        r = point.r
        if point.r == 0:
            r = self.radius * 1.05 - self.radius * 0.95
        if d - r <= self.radius:
            return self.with_arc_segment(point)
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
