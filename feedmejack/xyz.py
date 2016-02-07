#!/usr/bin/python3

class XY(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

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

class XYZ(object):
    def __init__(self, x, y, z):
        self.xy = XY(x,y)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return XYZ(self.x + other.x, self.y + other.y, other.z)

    def __sub__(self, other):
        return XYZ(self.x - other.x, self.y - other.y, self.z)

    def __str__(self):
        fmt = "XYZ("
        if int(self.x) == float(self.x):
            fmt += "%d,"
        else:
            fmt += "%0.2f,"
        if int(self.y) == float(self.y):
            fmt += "%d,"
        else:
            fmt += "%0.2f,"
        if int(self.z) == float(self.z):
            fmt += "%d)"
        else:
            fmt += "%0.2f)"

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

def Point(x, y, z=None):
    if z is None:
        return XY(x,y)
    else:
        return XYZ(x,y,z)

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
