#!/usr/bin/python3

from decimal import Decimal as _Decimal
import math

if __name__ != '__main__':
    from .xyz import XY, XYZ, Line

def _clean(val):
        val = _Decimal(val)
        val = val.normalize()
        val = val.quantize(_Decimal("1.00000"))
        return val

def _inside(val, l, r):
    val = _clean(val)
    if l < r:
        minimum = l
        maximum = r
    else:
        minimum = r
        maximum = l
    if val < minimum - _Decimal(0.01) or val > maximum + _Decimal(0.01):
        return False
    return True

class Triangle(object):
    _strname = "Triangle"
    def __new__(cls, A, B, C):
        self = object.__new__(cls)
        self.__init__(A, B, C)

        if _Decimal(90.0) in self.angles:
            self = object.__new__(RightTriangle)
            self.__init__(A, B, C)
        return self

    def __init__(self, A, B, C):
        # print("lines: %s" % (lines,))
        # print("lengths: %s" % [x.length for x in lines])

        # always organize it so B is opposite the longest line,
        # and A is opposite the second longest...
        self.A = A
        self.B = B
        self.C = C

        origin = XY(0,0)

        def swap(one, two):
            # print("swapping %s and %s" % (one, two))
            tmp = getattr(self, one)
            setattr(self, one, getattr(self, two))
            setattr(self, two, tmp)

        def avg(*l):
            return sum(l) / len(l)

        # try to get a stable sort order, even though the only real
        # restriction is b.length is longest and a.length is next.
        if origin.distance(self.A) > origin.distance(self.B):
            swap('A', 'B')
        if origin.distance(self.B) > origin.distance(self.C):
            swap('B', 'C')
        if origin.distance(self.A) > origin.distance(self.C):
            swap('A', 'C')

        if avg(self.A.x, self.A.y) > avg(self.B.x, self.B.y):
            swap('A', 'B')
        if avg(self.B.x, self.B.y) > avg(self.C.x, self.C.y):
            swap('B', 'C')
        if avg(self.A.x, self.A.y) > avg(self.C.x, self.C.y):
            swap('A', 'C')

        # this is the only sorting that /really/ matters, but we do the
        # previous two to try to get a stable sort order to make testing
        # easier...
        if self.a.length > self.b.length:
            swap('A', 'B')
        if self.c.length > self.b.length:
            swap('B', 'C')
        if self.c.length > self.a.length:
            swap('A', 'C')

    def subtriangle(self, is_a1=False):
        if is_a1:
            points = [self.Bmid, self.A, self.B]
        else:
            points = [self.Bmid, self.C, self.B]

        return RightTriangle(*points)

    @property
    def parimeter(self):
        return self.a.length + self.b.length + self.c.length

    @property
    def a0(self):
        return self.subtriangle(is_a1=False)

    @property
    def a1(self):
        return self.subtriangle(is_a1=True)

    @property
    def area(self):
        return self.a0.area + self.a1.area

    @property
    def thetaA(self):
        bdeg = math.degrees(math.atan2(self.b.xyrise, self.b.xyrun))
        cdeg = math.degrees(math.atan2(self.c.xyrise, self.c.xyrun))

        theta = bdeg - cdeg

        return _clean(theta)

    @property
    def thetaC(self):
        bdeg = math.degrees(math.atan2(self.b.xyrise, self.b.xyrun))
        adeg = math.degrees(math.atan2(self.a.xyrise, self.a.xyrun))

        theta = bdeg - adeg

        return _clean(theta)

    @property
    def Bmid(self):
        # print("a: %s b: %s c: %s" % (self.a, self.b, self.c))

        # print("self.thetaA: %s" % (self.thetaA,))
        # print("self.thetaC: %s" % (self.thetaC,))

        angleB0 = 90 - self.thetaA
        # print("angleB0: %s" % (angleB0,))
        angleD = angleB0 * 2
        # print("angleD: %s" % (angleD,))

        lengthD = self.c.length

        x = self.B.x - self.A.x
        y = self.B.y - self.A.y

        x = self.B.x - lengthD * _clean(math.cos(math.radians(angleD)))
        y = self.B.y + lengthD * _clean(math.sin(math.radians(angleD)))
        # print("(x,y): (%s,%s)" % (x,y))
        BmidX = (x + self.A.x) / 2
        BmidY = (y + self.A.y) / 2
        return XY(BmidX, BmidY)

    @property
    def CBA(self):
        return self.ABC

    @property
    def BCA(self):
        return self.ACB

    @property
    def CAB(self):
        return self.BAC

    @property
    def ABC(self):
        return _clean(180 - (abs(self.thetaA) + abs(self.thetaC)))

    @property
    def BAC(self):
        return abs(self.thetaA)

    @property
    def ACB(self):
        return abs(self.thetaC)

    @property
    def angles(self):
        yield self.BAC
        yield self.ABC
        yield self.ACB

    def __str__(self):
        return "%s(%s,%s,%s)" % (self._strname, self.A, self.B, self.C)

    def __contains__(self, point):
        raise NotImplementedError

    @property
    def is_right(self):
        return _Decimal(45.0) in self.angles

    @property
    def is_acute(self):
        for angle in self.angles:
            if angle >= _Decimal(45.0):
                return False
        return True

    @property
    def is_obtuse(self):
        for angle in self.angles:
            if angle > _Decimal(45.0):
                return True
        return False

    @property
    def lengths(self):
        yield self.A.distance(self.B)
        yield self.B.distance(self.C)
        yield self.C.distance(self.A)

    @property
    def longest(self):
        return max(self.lengths)

    @property
    def shortest(self):
        return min(self.lengths)

    @property
    def points(self):
        yield self.A
        yield self.B
        yield self.C

    @property
    def a(self):
        return Line(self.B, self.C)

    @property
    def b(self):
        return Line(self.A, self.C)

    @property
    def c(self):
        return Line(self.A, self.B)

    @property
    def middlest_point_index(self):
        if _inside(self.A.x, self.B.x, self.C.x) and \
           _inside(self.A.y, self.B.y, self.C.y):
            return 0

        if _inside(self.B.x, self.A.x, self.C.x) and \
           _inside(self.B.y, self.A.y, self.C.y):
            return 1

        if _inside(self.C.x, self.B.x, self.A.x) and \
           _inside(self.C.y, self.B.y, self.A.y):
            return 2

    @property
    def baseline(self):
        mpi = self.middlest_point_index
        if mpi == 0:
            return self.a
        elif mpi == 1:
            return self.b
        elif mpi == 2:
            return self.c
        else:
            raise RuntimeError("self.points index cannot be %s" % (mpi))

    @property
    def lines(self):
        yield self.a
        yield self.b
        yield self.c

class RightTriangle(Triangle):
    _strname = "RightTriangle"

    def __init__(self, A, B, C):
        Triangle.__init__(self, A, B, C)
        squares = [A.distance(B), B.distance(C), C.distance(A)]
        one_percent = max(squares) / 100
        squares[0] *= squares[0]
        squares[1] *= squares[1]
        squares[2] *= squares[2]

        if squares[1] - (squares[0] + squares[2]) < one_percent:
            pass
        elif squares[2] - (squares[0] + squares[1]) < one_percent:
            pass
        elif squares[0] - (squares[1] + squares[2]) < one_percent:
            pass
        else:
            raise ValueError("(%s,%s,%s) do not comprise a right triangle." % \
                             (A, B, C))

    @property
    def area(self):
        return _clean(self.a.length * self.c.length / _Decimal(2.0))

    @property
    def ABC(self):
        return _Decimal(90.0)

    @property
    def BAC(self):
        return _Decimal(180.0) - _Decimal(90.0) - _clean(self.thetaC)

    @property
    def ACB(self):
        return _Decimal(180.0) - _Decimal(90.0) - _clean(self.thetaA)

    @property
    def Bmid(self):
        """ the point on self.b from which you could draw a segment to self.B
        which would be perpendicular to self.b.
        """

        x = (self.A.x + self.C.x) / _Decimal(2.0)
        y = (self.A.y + self.C.y) / _Decimal(2.0)
        try:
            z = (self.B.z + self.C.z) / _Decimal(2.0)
            Bmid = XYZ(x, y, z)
        except:
            Bmid = XY(x, y)
        return Bmid

    @property
    def middlest_point_index(self):
        return 1

    @property
    def thetaA(self):
        a = self.A.distance(self.B)
        o = self.C.distance(self.B)
        return math.degrees(math.atan2(a,o))

    @property
    def thetaC(self):
        a = self.C.distance(self.B)
        o = self.A.distance(self.B)
        return math.degrees(math.atan2(a,o))

    @property
    def baseline(self):
        lines = list(self.lines)
        return lines[self.middlest_point_index]

    def __str__(self):
        return Triangle.__str__(self)

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

__all__ = ['Arc', 'Ball', 'Box', 'Circle', 'Cube',
           'Plate', 'RightTriangle', 'Square', 'Triangle', 'Wedge']

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
