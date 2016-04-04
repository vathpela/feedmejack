#!/usr/bin/python3

import pdb

class XY(object):
    def __init__(self, x, y, r=0):
        self.x = float(x)
        self.y = float(y)
        self.r = float(r)

    def __add__(self, other):
        return XY(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return XY(self.x - other.x, self.y - other.y)

    def __str__(self):
        fmt = "XY("
        if int(self.x) == float(self.x):
            fmt += "%d,"
        else:
            fmt += "%0.2f,"
        if int(self.y) == float(self.y):
            fmt += "%d)"
        else:
            fmt += "%0.2f)"

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
        import math
        x = other.x - self.x
        x *= x
        y = other.y - self.y
        y *= y
        return math.sqrt(x+y)

    def slope(self, other):
        return (other.y - self.y) / (other.x - self.x)

    def __hash__(self):
        return hash((self.x, self.y, self.r))

class XYZ(object):
    def __init__(self, x, y, z, r=0):
        self.xy = XY(x,y)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.r = float(r)

    def __add__(self, other):
        return XYZ(self.x + other.x, self.y + other.y, other.z)

    def __sub__(self, other):
        return XYZ(self.x - other.x, self.y - other.y, self.z)

    def __str__(self):
        fmt = "XYZ("
        if int(self.x) == float(self.x):
            fmt += "%d,"
        else:
            fmt += "%0.3f,"
        if int(self.y) == float(self.y):
            fmt += "%d,"
        else:
            fmt += "%0.3f,"
        if int(self.z) == float(self.z):
            fmt += "%d)"
        else:
            fmt += "%0.3f)"

        return fmt % (self.x, self.y, self.z)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

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
        import math
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
        return math.sqrt(x+y+z)

    def __hash__(self):
        return hash((self.x, self.y, self.z, self.r))

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

    def __str__(self):
        return "%s(%s,%s)" % (self._strname, self.xy_min, self.xy_max)

    def __repr__(self):
        return str(self)

    @property
    def xyslope(self):
        return (self.xy_max.y - self.xy_min.y) / \
               (self.xy_max.x - self.xy_min.x)

    @property
    def xzslope(self):
        return (self.xy_max.z - self.xy_min.z) / \
               (self.xy_max.x - self.xy_min.x)

    @property
    def yzslope(self):
        return (self.xy_max.z - self.xy_min.z) / \
               (self.xy_max.y - self.xy_min.y)

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
        lrads = math.atan(self.xyslope)
        rrads = math.atan(self.xyslope ** -1)

    def crossesZ(self, z):
        #if self.xy_min.z == z or self.xy_max.z == z:
        #    return True
        if self.xy_min.z > self.xy_max.z:
            if z >= self.xy_max.z and z <= self.xy_min.z:
                return True
        else:
            if z >= self.xy_min.z and z <= self.xy_max.z:
                return True
        return False

    def atZ(self, z):
        if not self.crossesZ(z):
            return None
        if self.xy_min.z == z:
            return self.xy_min
        if self.xy_max.z == z:
            return self.xy_max

        xzs = self.xzslope
        dz = z - self.xy_min.z
        dx = dz * xzs
        yzs = self.yzslope
        dy = dz * yzs

        if self.xy_min.x + dx > 300 or self.xy_min.y + dy > 300:
            #import pdb
            #pdb.set_trace()
            pass
            # XXX x or y is wrong here
            pass
        return XYZ(self.xy_min.x + dx, self.xy_min.y + dy, z)

    def hasEndpoint(self, xyz):
        if xyz in (self.xy_min, self.xy_max):
            return True
        return False

    @property
    def reverse(self):
        return Line(self.xy_max, self.xy_min)

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

    def zintersection(self, z:float):
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

    def withinX(self, left: float, right: float):
        return left >= self.minX and right <= self.maxX

    @property
    def maxY(self):
        return max([v.y for v in self.vertices])

    @property
    def minY(self):
        return min([v.y for v in self.vertices])

    def withinY(self, front: float, back: float):
        return front >= self.minY and back <= self.maxY

    @property
    def maxZ(self):
        return max([v.z for v in self.vertices])

    @property
    def minZ(self):
        return min([v.z for v in self.vertices])

    def withinZ(self, top: float, bottom: float):
        for v in self.vertices:
            if top >= v.z and bottom <= v.z:
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
        for line in self.lines:
            if line.crossesZ(z):
                crossers.append(line)
                print("%s crosses %f" % (line, z))

        l = len(crossers)
        if l == 3:
            for line in crossers:
                if line.xy_min.z == z:
                    crossers.remove(line)
                    l-=1
                    break
        if l > 2:
            for line in crossers:
                if line.xy_min.z == z and line.xy_max.z == z:
                    return Line(line.xy_min, line.xy_max)
            import pdb
            pdb.set_trace()
            raise RuntimeError("too many crossers: %s" % (crossers,))
        elif l == 0:
            return None

        try:
            print("crossers[0]: %s crossers[1]: %s" % (crossers[0], crossers[1]))
            pointa = crossers[0].atZ(z)
            pointb = crossers[1].atZ(z)
            print("pointa: %s pointb: %s" % (pointa, pointb))
        except IndexError:
            pdb.set_trace()
            pass
        return Line(pointa, pointb)

class Object(object):
    def __init__(self):
        self._vlib = VertexLibrary()
        self.faces = set()

    def addVertex(self, vertex: XYZ):
        self._vlib.get(vertex)

    def addFace(self, *vertices: int):
        face = Face(library=self._vlib, vertices=vertices)
        self.faces.add(face)

    def xSlice(self, left: float, right:float):
        for face in self.faces:
            if face.withinX(left=left, right=right):
                yield face

    def ySlice(self, front: float, back:float):
        for face in self.faces:
            if face.withinY(front=front, back=back):
                yield face

    def zSlice(self, top: float, bottom:float):
        lib = VertexLibrary()
        for face in self.faces:
            if face.withinZ(bottom=bottom, top=top):
                vertices = []
                for v in face.vertices:
                    i = lib.append(v)
                    vertices.append(i)
                    vertices.reverse()
                yield Face(lib, vertices=vertices)

    @property
    def zRange(self):
        zs = [v.z for v in self._vlib]
        return (min(zs), max(zs))

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
