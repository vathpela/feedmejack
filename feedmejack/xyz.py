#!/usr/bin/python3

import pdb
import math
from decimal import Decimal as _Decimal
from .utility import *
import decimal

def _inside(val, l, r):
    val = Decimal(val)
    if l < r:
        minimum = l
        maximum = r
    else:
        minimum = r
        maximum = l
    if val < minimum - _Decimal(0.01) or val > maximum + _Decimal(0.01):
        return False
    return True

class XY(object):
    def __init__(self, x, y, r=0):
        self.x = Decimal(x)
        self.y = Decimal(y)
        self.r = Decimal(r)

    def __add__(self, other):
        return XY(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return XY(self.x - other.x, self.y - other.y)

    def __str__(self):
        fmt = "XY("
        if int(self.x) == _Decimal(self.x):
            fmt += "%d,"
        else:
            fmt += "%s,"
        if int(self.y) == _Decimal(self.y):
            fmt += "%d)"
        else:
            fmt += "%s)"

        return fmt % (self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, XY):
            return False
        return self.x == other.x and self.y == other.y

    def leftof(self, other):
        return self.x < other.x

    def rightof(self, other):
        return self.x > other.x

    def farther(self, other):
        return self.y > other.y

    def nearer(self, other):
        return self.y < other.y

    def xlinear(self, other):
        return self.x == other.x

    def ylinear(self, other):
        return self.y == other.y

    def keys(self):
        return [x in ['x','y']]

    def __getitem__(self, key):
        return {'x':self.x, 'y':self.y}[key]

    def distance(self, other):
        x = other.x - self.x
        x *= x
        y = other.y - self.y
        y *= y
        return Decimal(math.sqrt(x+y))

    def slope(self, other):
        ret = (other.y - self.y) / (other.x - self.x)
        return ret

    def __hash__(self):
        return hash((self.x, self.y, self.r))

    def __lt__(self, other):
        origin = XY(0,0)
        sd = self.distance(origin)
        od = other.distance(origin)
        if sd < od:
            return True
        return False

    @property
    def quadrant(self):
        if self.x > 0:
            if self.y > 0:
                return 1
            elif self.y == 0:
                raise ValueError
            return 4
        elif self.x < 0:
            if self.y > 0:
                return 2
            elif self.y == 0:
                raise ValueError
            return 3
        raise ValueError

    @property
    def xyquadrant(self):
        return self.quadrant

    @property
    def yzquadrant(self):
        raise RuntimeError("XY point has no YZ quadrant.")

    @property
    def xzquadrant(self):
        raise RuntimeError("XY point has no XZ quadrant.")

class XYZ(XY):
    def __init__(self, x, y, z, r=0):
        self.x = Decimal(x)
        self.y = Decimal(y)
        self.z = Decimal(z)
        self.r = Decimal(r)
        self.xy = XY(self.x, self.y)

    def __add__(self, other):
        return XYZ(self.x + other.x, self.y + other.y, other.z)

    def __sub__(self, other):
        return XYZ(self.x - other.x, self.y - other.y, self.z)

    def __str__(self):
        fmt = "XYZ("
        if int(self.x) == _Decimal(self.x):
            fmt += "%d,"
        else:
            fmt += "%s,"
        if int(self.y) == _Decimal(self.y):
            fmt += "%d,"
        else:
            fmt += "%s,"
        if int(self.z) == _Decimal(self.z):
            fmt += "%d)"
        else:
            fmt += "%s)"

        return fmt % (self.x, self.y, self.z)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if hasattr(other, 'z'):
            return self.x == other.x and self.y == other.y and self.z == other.z
        else:
            return self.x == other.x and self.y == other.y

    def leftof(self, other):
        return self.x < other.x

    def rightof(self, other):
        return self.x > other.x

    def farther(self, other):
        return self.y > other.y

    def nearer(self, other):
        return self.y < other.y

    def above(self, other):
        return self.z > other.z

    def below(self,other):
        return self.z < other.z

    def xyplanar(self, other):
        return self.z == other.z

    def xzplanar(self, other):
        return self.y == other.y

    def yzplanar(self, other):
        return self.x == other.x

    def xlinear(self, other):
        return self.y == other.y and self.z == other.z

    def ylinear(self, other):
        return self.x == other.x and self.z == other.z

    def zlinear(self, other):
        return self.x == other.x and self.y == other.y

    def keys(self):
        return [x in ['x','y','z']]

    def __getitem__(self, key):
        return {'x':self.x, 'y':self.y, 'z':self.z}[key]

    def distance(self, other):
        x = other.x - self.x
        x *= x
        y = other.y - self.y
        y *= y
        if hasattr(other, 'z'):
            z2 = other.z
        else:
            z2 = self.z
        z = z2 - self.z
        z *= z
        return Decimal(math.sqrt(x+y+z))

    def __hash__(self):
        return hash((self.x, self.y, self.z, self.r))

    @property
    def xyquadrant(self):
        return XY(self.x,self.y).quadrant

    @property
    def yzquadrant(self):
        return XY(self.y,self.z).quadrant

    @property
    def xzquadrant(self):
        return XY(self.x,self.z).quadrant

    @property
    def quadrant(Self):
        return self.xyquadrant

def Point(x, y, z=None):
    if z is None:
        return XY(x,y)
    else:
        return XYZ(x,y,z)

class Line(object):
    _strname = "Line"

    def __init__(self, xy_min, xy_max):
        self.xy_min = xy_min
        self.xy_max = xy_max
        self.color = None

    def __str__(self):
        return "%s(%s,%s)" % (self._strname, self.xy_min, self.xy_max)

    def __repr__(self):
        return str(self)

    @property
    def length(self):
        return self.xy_min.distance(self.xy_max)

    def __len__(self):
        return self.length

    def __eq__(self, other):
        if self.length == other.length:
            return True
        return False

    def __lt__(self, other):
        if self.length < other.length:
            return True
        return False

    def __hash__(self):
        return hash((self.xy_min, self.xy_max))

    @property
    def points(self):
        yield self.xy_min
        yield self.xy_max

    @property
    def middle(self):
        x = self.xmin + (self.xmax - self.xmin) / _Decimal(2.0)
        y = self.ymin + (self.ymax - self.ymin) / _Decimal(2.0)
        try:
            z = self.zmin + (self.zmax - self.zmin) / _Decimal(2.0)
            return XY(x,y,z)
        except:
            return XY(x,y)

    @property
    def bottom(self):
        return Line(self.xy_min, self.middle)

    @property
    def top(self):
        return Line(self.middle, self.xy_max)

    @property
    def xmin(self):
        return self.xy_min.x
    @property
    def xmax(self):
        return self.xy_max.x

    @property
    def ymin(self):
        return self.xy_min.y
    @property
    def ymax(self):
        return self.xy_max.y

    @property
    def zmin(self):
        return self.xy_min.z
    @property
    def zmax(self):
        return self.xy_max.z

    @property
    def xrange(self):
        return self.xmax - self.xmin
    @property
    def yrange(self):
        return self.ymax - self.ymin
    @property
    def zrange(self):
        return self.zmax - self.zmin

    # rise is in distance units
    @property
    def xyrise(self):
        return self.ymax - self.ymin
    # run is in distance units
    @property
    def xyrun(self):
        return self.xmax - self.xmin
    # m is a unitless ratio
    @property
    def xym(self):
        try:
            return self.xyrise / self.xyrun
        except decimal.DivisionByZero:
            return math.inf
    # theta is in degrees
    @property
    def xytheta(self):
        atan = math.atan2(self.xyrise, self.xyrun)
        return math.degrees(atan)
    # sin/cos/tan are all ratios of distance units
    @property
    def xysin(self):
        return math.sin(math.radians(self.xytheta))
    @property
    def xycos(self):
        return math.cos(math.radians(self.xytheta))
    @property
    def xytan(self):
        return math.tan(math.radians(self.xytheta))

    @property
    def xzrise(self):
        return self.xy_max.z - self.xy_min.z
    @property
    def xzrun(self):
        return self.xy_max.x - self.xy_min.x
    @property
    def xzm(self):
        return self.xzrise / self.xzrun
    @property
    def xztheta(self):
        atan = math.atan2(self.xzrise, self.xzrun)
        return math.degrees(atan)
    @property
    def xzsin(self):
        return math.sin(math.radians(self.xztheta))
    @property
    def xzcos(self):
        return math.cos(math.radians(self.xztheta))
    @property
    def xztan(self):
        return math.tan(math.radians(self.xztheta))

    @property
    def yzrise(self):
        return self.xy_max.z - self.xy_min.z
    @property
    def yzrun(self):
        return self.xy_max.y - self.xy_min.y
    @property
    def yzm(self):
        return self.xzrise / self.xzrun
    @property
    def yztheta(self):
        atan = math.atan2(self.yzrise, self.yzrun)
        return math.degrees(atan)
    @property
    def yzsin(self):
        return math.sin(math.radians(self.yztheta))
    @property
    def yzcos(self):
        return math.cos(math.radians(self.yztheta))
    @property
    def yztan(self):
        return math.tan(math.radians(self.yztheta))

    def __contains__(self, point):
        r = point.r
        if point.r == 0:
            # dude, whatever
            r = 0.5

        d = point.distance(self.xy_max)
        if d < r:
            return True
        d = point.distance(self.xy_min)
        if d < r:
            return True

        # now we draw a box from the tangent points at the same slope as the
        # line, r away.  If the point center is inside that box, it touches the
        # line.
        lrads = math.atan2(self.xyrise, self.xyrun)
        rrads = math.atan2(self.xyrun, self.xyrise)

    def crossesX(self, x):
        if self.xmin > self.xmax:
            if x >= self.xmax and x <= self.xmin:
                return True
        else:
            if x >= self.xmin and x <= self.xmax:
                return True
        return False

    def crossesY(self, y):
        if self.ymin > self.ymax:
            if y >= self.ymax and y <= self.ymin:
                return True
        else:
            if y >= self.ymin and y <= self.ymax:
                return True
        return False

    def crossesZ(self, z):
        if self.zmin > self.zmax:
            if z >= self.zmax and z <= self.zmin:
                return True
        else:
            if z >= self.zmin and z <= self.zmax:
                return True
        return False

    def atD(self, d):
        t = self.length / d
        x0 = self.xy_min.x
        x1 = self.xy_max.x
        dx = x1 - x0

        y0 = self.xy_min.y
        y1 = self.xy_max.y
        dy = y1 - y0

        x = x0 + dx / t
        y = y0 + dy / t

        if hasattr(self.xy_min, 'z') and hasattr(self.xy_max, 'z'):
            z0 = self.xy_min.z
            z1 = self.xy_max.z
            dz = z1 - z0
            if d < 0:
                dz = 0 - abs(dz)
            z = z0 + dz / t
            return XYZ(x,y,z)
        return XY(x,y)

    def dzAtZ(self, z):
        # indent = "        dzAtZ:"
        # things we know:
        # points a(x0,y0,z0) and b(x0,y0,z0), straddling z in one way or the other
        # point c's z1

        dz = z - self.zmin
        # print("%s dz = %f - %f = %f" % (indent, z, self.zmin, z - self.zmin))
        return dz

    def dxAtZ(self, z):
        # indent = "        dxAtZ:"
        # things we know:
        # points a(x0,y0,z0) and b(x0,y0,z0), straddling z in one way or the other
        # point c's z1

        dz = self.dzAtZ(z)
        dx = float(dz) / self.xztan
        # print("%s dx = dz / tan(theta[xz]) = %f / tan(%f) = %f / %f = %f" %
        #        (indent, dz, self.xztheta, dz, self.xztan, dx))
        return dx

    def dyAtZ(self, z):
        # indent = "        dyAtZ:"
        # things we know:
        # points a(x0,y0,z0) and b(x0,y0,z0), straddling z in one way or the other
        # point c's z1

        dz = self.dzAtZ(z)
        dy = float(dz) / self.yztan
        # print("%s dy = dz / tan(theta[yz]) = %f / tan(%f) = %f / %f = %f" %
        #        (indent, dz, self.yztheta, dz, self.yztan, dy))
        return dy

    @property
    def xyb(self):
        # y = mx + b
        # y - mx = b
        # b = y - mx
        b = self.xy_max.y - (self.xym * self.xy_max.x)
        return Decimal(b)

    def xyYAtX(self, x):
        return (self.xym * Decimal(x)) + self.xyb

    def xyXAtY(self, y):
        # y = mx + b
        # y -b = mx
        # (y-b)/m = x
        return (Decimal(y) - self.xyb) / self.xym

    def atX(self, x):
        indent = "      AtX:"

        if not self.crossesX(x):
            # raise ValueError
            return None
        if self.xy_min.x == x:
            return self.xy_min
        if self.xy_max.x == x:
            return self.xy_max

        msg = ""
        msg += "%s finding point at x=%f\n" % (indent, x)

        dx = self.dxAtX(x)
        if self.xmin + dx != x:
            raise ValueError("%s != %s" % (self.xmin + dx, x))
        msg += "%s FINAL X: %f\n" % (indent, self.xmin + dx)

        pdx = (dx) / self.xrange
        msg += "%s %s x=%f (%f %%)\n" % (indent, self, x, pdx*100)

        yest = self.ymin + (self.yrange * pdz)
        zest = self.zmin + (self.zrange * pdx)

        dz = self.dzAtX(x)
        z = self.zmin + _Decimal(dz)

        msg += "%s dz = %f\n" % (indent, dz)
        msg += "%s FINAL Z: %s\n" % (indent, z)

        dy = self.dyAtX(x)
        y = self.ymin + _Decimal(dy)

        msg += "%s dy = %s\n" % (indent, dy)
        msg += "%s FINAL Y: %s\n" % (indent, y)

        def errbar(y, z):
            return 100 - (100 / x * y)

        if abs(errbar(zest, z)) > 0.0001 or abs(errbar(yest, y)) > 0.0001:
            msg += "%s estimates: z=%s y=%s" % (indent, zest, yest)
            print("%s" % (msg,))
        if abs(errbar(zest, z)) > 0.0001:
            print("%s z error is %s pct" % (indent, errbar(zest, z)))

        if abs(errbar(yest, y)) > 0.0001:
            print("%s y error is %s pct" % (indent, errbar(yest, y)))

        if not _inside(x, self.xmin, self.xmax):
            raise ValueError("%s is not in range %s..%s" % (x, self.xmin, self.xmax))
        if not _inside(y, self.ymin, self.ymax):
            raise ValueError("%s is not in range %s..%s" % (x, self.ymin, self.ymax))
        if not _inside(z, self.zmin, self.zmax):
            raise ValueError("%s is not in range %s..%s" % (x, self.zmin, self.zmax))
        return Point(x, y, z)

    def atZ(self, z):
        indent = "      AtZ:"

        if not self.crossesZ(z):
            # raise ValueError
            return None
        if self.xy_min.z == z:
            return self.xy_min
        if self.xy_max.z == z:
            return self.xy_max

        msg = ""
        msg += "%s finding point at z=%f\n" % (indent, z)

        dz = self.dzAtZ(z)
        if self.zmin + dz != z:
            raise ValueError("%s != %s" % (self.zmin + dz, z))
        msg += "%s FINAL Z: %f\n" % (indent, self.zmin + dz)

        pdz = (dz) / self.zrange
        msg += "%s %s z=%f (%f %%)\n" % (indent, self, z, pdz*100)

        # just sanity checking - though as a note, the only time I've seen this
        # differ from our math.$TRIGFNS() version below, it's been enough to
        # flip ths sign of a float, but still the value is basically 0.
        # "Error"s look something like:
        #   lineAtZ: Line(XYZ(163.576,13.477,332.267),XYZ(159.657,11.456,334.322))
        #   crosses 333.998378
        #   lineAtZ: Line(XYZ(159.657,11.456,334.322),XYZ(157.736,9.815,332.248)) crosses 333.998378
        #   lineAtZ: crosser:
        #       Line(XYZ(163.576,13.477,332.267),XYZ(159.657,11.456,334.322))
        #     dzAtZ: dz = 333.998378 - 332.266512 = 1.731866
        #       AtZ: FINAL Z: 333.998378
        #       AtZ: Line(XYZ(163.576,13.477,332.267),XYZ(159.657,11.456,334.322)) z=333.998378 (84.239319 %)
        #       AtZ: estimates: x=160.27509756016764 y=11.77480930658196
        #       AtZ: dx = -3.301207
        #       AtZ: FINAL X: 160.27509756016764
        #       AtZ: x error is 0.0 pct
        #       AtZ: dy = -1.7017770446177103
        #       AtZ: FINAL Y: 11.77480930658196
        #       AtZ: y error is -1.4210854715202004e-14 pct
        #   lineAtZ: point: XYZ(160.275,11.775,333.998)
        #   lineAtZ: crosser: Line(XYZ(159.657,11.456,334.322),XYZ(157.736,9.815,332.248))
        #     dzAtZ: dz = 333.998378 - 334.322400 = -0.324022
        #       AtZ: FINAL Z: 333.998378
        #       AtZ: Line(XYZ(159.657,11.456,334.322),XYZ(157.736,9.815,332.248)) z=333.998378 (15.619049 %)
        #       AtZ: estimates: x=159.3572979708394 y=11.19999308061723
        #       AtZ: dx = -0.300163
        #       AtZ: FINAL X: 159.3572979708394
        #       AtZ: x error is 0.0 pct
        #       AtZ: dy = -0.2564237619295354
        #       AtZ: FINAL Y: 11.19999308061723
        #       AtZ: y error is 0.0 pct
        #   lineAtZ: point: XYZ(159.357,11.200,333.998)
        #   lineAtZ: new line Line(XYZ(160.275,11.775,333.998),XYZ(159.357,11.200,333.998)) (slope 0.6262981947785048)
        # got line Line(XYZ(160.275,11.775,333.998),XYZ(159.357,11.200,333.998)) nf:0 d:0
        #
        # in fact, the only values I've seen other than 0 are:
        # -1.4210854715202004e-14 pct
        #  1.4210854715202004e-14 pct
        #  2.842170943040401e-14 pct
        #
        # To be honest, if every calculation I ever did came within
        # -2e-14..3e-14 *percent* of the final answer (which is obviously just
        # round-off error in a float), I'd be really, really happy about it.

        xest = self.xmin + (self.xrange * pdz)
        yest = self.ymin + (self.yrange * pdz)

        dx = self.dxAtZ(z)
        x = self.xmin + _Decimal(dx)

        msg += "%s dx = %f\n" % (indent, dx)
        msg += "%s FINAL X: %s\n" % (indent, x)

        dy = self.dyAtZ(z)
        y = self.ymin + _Decimal(dy)

        msg += "%s dy = %s\n" % (indent, dy)
        msg += "%s FINAL Y: %s\n" % (indent, y)

        def errbar(x, y):
            return 100 - (100 / x * y)

        if abs(errbar(xest, x)) > 0.0001 or abs(errbar(yest, y)) > 0.0001:
            msg += "%s estimates: x=%s y=%s" % (indent, xest, yest)
            print("%s" % (msg,))
        if abs(errbar(xest, x)) > 0.0001:
            print("%s x error is %s pct" % (indent, errbar(xest, x)))

        if abs(errbar(yest, y)) > 0.0001:
            print("%s y error is %s pct" % (indent, errbar(yest, y)))

        if not _inside(x, self.xmin, self.xmax):
            raise ValueError("%s is not in range %s..%s" % (x, self.xmin, self.xmax))
        if not _inside(y, self.ymin, self.ymax):
            raise ValueError("%s is not in range %s..%s" % (x, self.ymin, self.ymax))
        if not _inside(z, self.zmin, self.zmax):
            raise ValueError("%s is not in range %s..%s" % (x, self.zmin, self.zmax))
        return Point(x, y, z)

    @property
    def reverse(self):
        line = Line(self.xy_max, self.xy_min)
        line.color = self.color
        return line

    def distance(self, point):
        d = self.xy_min.distance(point) + self.xy_max.distance(point)
        d = _Decimal(d) / 2
        return Decimal(d)

    @property
    def xybisector(self):
        m = self.middle

        rise = self.xyrise
        run = self.xyrun

        point1 = XY(m.x - rise/2, m.y + run/2)
        l = Line(m, point1)
        point0 = l.atD(0 - (self.length/2))
        l = Line(point0, m)
        point1 = l.atD(self.length)
        l = Line(point0, point1)

        if hasattr(self.middle, 'z'):
            point0 = XYZ(point0.x, point0.y, self.middle.z)
            point1 = XYZ(point1.x, point1.y, self.middle.z)
        return Line(point0, point1)

class VertexLibrary(object):
    # This would be better as a python 3.5 deque.
    def __init__(self):
        self._vertices = {}
        self._indices = []
        self._n = 1

    def append(self, vertex: XYZ):
        entry = self._vertices.setdefault(vertex,{'value':None,
                                                  'aliases':[],
                                                  'faces':[]})
        if entry['value']:
            entry['aliases'].append(self._n)
            return entry['value']

        value = self._n
        self._n += 1
        entry['value'] = value
        self._indices.append(vertex)
        return value

    def get(self, k: XYZ):
        if k in self._vertices:
            return self.index(k)
        return self.append(k)

    def index(self, vertex: XYZ):
        return self._vertices[vertex]['value']

    def __getitem__(self, index: int):
        return self._indices[index-1]

class Face(object):
    def __init__(self, library, vertices: [int]):
        if len(vertices) < 3:
            raise ValueError
        self._library = library
        verts = []
        for v in vertices:
            verts.append(library[v])
        self._vertices = verts
        for v in self._vertices:
            library._vertices[v]['faces'].append(self)

    def __str__(self):
        verts=",".join([str(v) for v in self.vertices])
        s = "Face(%s)" % (verts,)
        return s

    def __repr__(self):
        return str(self)

    def zintersection(self, z:_Decimal):
        min_z = min([v.z for v in self.vertices])
        max_z = max([v.z for v in self.vertices])
        if min_z > z or max_z < z:
               return None
        min_x = min([v.x for v in self.vertices])
        max_x = max([v.x for v in self.vertices])
        min_y = min([v.y for v in self.vertices])
        max_y = max([v.y for v in self.vertices])
        pts = [XYZ(min_x, min_y, z),
               XYZ(max_x, max_y, z),
               XYZ(min_x, max_y, z)]

        l = len(self.vertices)
        return XY(sum([x.x for x in self.vertices]) / l, \
                  sum([x.y for x in self.vertices]) / l)

    @property
    def zline(self):
        min_x = min([v.x for v in self.vertices])
        max_x = max([v.x for v in self.vertices])
        min_y = min([v.y for v in self.vertices])
        max_y = max([v.y for v in self.vertices])
        return (XY(min_x,min_y),XY(max_x,max_y))

    @property
    def vertices(self):
        return [x for x in self._vertices]

    @property
    def maxX(self):
        return max([v.x for v in self.vertices])

    @property
    def minX(self):
        return min([v.x for v in self.vertices])

    def withinX(self, left:_Decimal, right:_Decimal):
        return left >= self.minX and right <= self.maxX

    @property
    def maxY(self):
        return max([v.y for v in self.vertices])

    @property
    def minY(self):
        return min([v.y for v in self.vertices])

    def withinY(self, front:_Decimal, back:_Decimal):
        return front >= self.minY and back <= self.maxY

    @property
    def maxZ(self):
        return max([v.z for v in self.vertices])

    @property
    def minZ(self):
        return min([v.z for v in self.vertices])

    @property
    def avgZ(self):
        return sum([v.z for v in self.vertices]) / len(self.vertices)

    def __lt__(self, other):
        if self.avgZ == other.avgZ:
            if self.minZ > other.minZ:
                return False
            return True
        if self.avgZ > other.avgZ:
            return False
        return True

    def __gt__(self, other):
        if self.avgZ == other.avgZ:
            if self.minZ < other.minZ:
                return False
            return True
        if self.avgZ < other.avgZ:
            return False
        return True

    def __eq__(self, other):
        if self.avgZ != other.avgZ:
            return False
        if self.minZ != other.minZ:
            return False
        if self.maxZ != other.maxZ:
            return False
        return True

    def __hash__(self):
        return hash(tuple(self.vertices))

    def crossesX(self, x):
        for line in self.lines:
            if line.crossesX(x):
                return True
        return False

    def crossesY(self, y):
        for line in self.lines:
            if line.crossesY(y):
                return True
        return False

    def crossesZ(self, z):
        for line in self.lines:
            if line.crossesZ(z):
                return True
        return False

    @property
    def lines(self):
        l = len(self.vertices) - 1
        lines = []
        for i,j in [(x,x+1) for x in range(0,l)] + [(l,0)]:
            v0 = self.vertices[i]
            v1 = self.vertices[j]
            pointa = XYZ(v0.x, v0.y, v0.z)
            pointb = XYZ(v1.x, v1.y, v1.z)
            yield Line(pointa, pointb)

    def lineAtZ(self, z):
        crossers = []
        points = []

        indent="  lineAtZ:"

        for line in self.lines:
            if line.crossesZ(z):
                crossers.append(line)
                # print("%s %s crosses %f" % (indent, line, z))

        for line in crossers:
            if line.xy_min.z == z or line.xy_max.z == z:
                if line.xy_min.z == z:
                    point = line.xy_min
                    print("%s point: %s" % (indent, point))
                    points.append(point)

                if line.xy_max.z == z:
                    if not line.xy_max in points:
                        point = line.xy_max
                        print("%s point: %s" % (indent, point))
                        points.append(point)
                crossers.remove(line)

        if 2 - len(points) != len(crossers):
            pdb.set_trace()
            raise RuntimeError("mismatched points (%d) vs crossers (%d)" %
                    (2 - len(points), len(crossers)))

        # slopes=[c.xym for c in crossers]
        for crosser in crossers:
            # print("%s crosser: %s" % (indent, crosser))
            point = crosser.atZ(z)
            # print("%s point: %s" % (indent, point))
            points.append(point)

        if len(points) < 2:
            pdb.set_trace()
            pass
            raise ValueError

        line = Line(points[0], points[1])
        # print("%s new line %s (slope %s)" % (indent, line, line.xym))
        return line

class Object(object):
    def __init__(self):
        self._vlib = VertexLibrary()
        self._faces = set()

    def addVertex(self, vertex: XYZ):
        return self._vlib.get(vertex)

    def addFace(self, *vertices: int):
        face = Face(library=self._vlib, vertices=vertices)
        self._faces.add(face)
        return face

    def xSlice(self, x:_Decimal):
        new = Object()
        for face in self.faces:
            if face.crossesX(x):
                vertices = []
                for v in face.vertices:
                    i = new.addVertex(v)
                    vertices.append(self._vlib[i])
                new.addFace(*vertices)
        return new

    def ySlice(self, y:_Decimal):
        new = Object()
        for face in self.faces:
            if face.crossesY(y):
                vertices = []
                for v in face.vertices:
                    i = new.addVertex(v)
                    vertices.append(i)
                new.addFace(*vertices)
        return new

    def zSlice(self, z:_Decimal):
        new = Object()
        for face in self.faces:
            if face.crossesZ(z):
                vertices = []
                for v in face.vertices:
                    i = new.addVertex(v)
                    vertices.append(i)
                new.addFace(*vertices)
        return new

    @property
    def zRange(self):
        zs = [v.z for v in self._vlib]
        return (min(zs), max(zs))

    @property
    def faces(self):
        for face in self._faces:
            yield face

__all__ = ['XY', 'XYZ', 'Point', 'VertexLibrary', 'Face', 'Object']

if __name__ == '__main__':
    a = XY(2,2)
    b = XY(1,1)

    if a - b != b:
        raise ValueError("%s - %s != %s == %s" % (a, b, b, a-b))

    if a + b != XY(3,3):
        raise ValueError

    if XY(1,2) != XY(1,2):
        raise ValueError

    if XY(0,0) == XY(1,1):
        raise ValueError
    if XY(0,0) == XY(-1,-1):
        raise ValueError
    if XY(1,0) == XY(1,-1):
        raise ValueError
    if XY(1,0) == XY(1,1):
        raise ValueError
    if XY(1,0) == XY(0,0):
        raise ValueError
    if XY(1,0) == XY(2,0):
        raise ValueError
