#!/usr/bin/python3

class XY(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return XY(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return XY(self.x - other.x, self.y - other.y)

    def __str__(self):
        return "(%0.03f,%0.03f)" % (self.x, self.y)

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

class XYZ(object):
    def __init__(self, x, y, z):
        self.xy = XY(x,y)
        self.z = z

    @property
    def x(self):
        self.xy.x

    @property
    def y(self):
        self.xy.y

    def __add__(self, other):
        return XYZ(self.x + other.x, self.y + other.y, other.z)

    def __sub__(self, other):
        return XYZ(self.x - other.x, self.y - other.y, self.z)

    def __str__(self):
        return "(%0.03f,%0.03f,%0.03f)" % (self.x, self.y, self.z)

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
