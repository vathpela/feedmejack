#!/usr/bin/python3

import sys
import os

def frange(x, y, step):
    if x > y:
        if step >= 0:
            step = -step
        while x > y:
            yield x
            x += step
    else:
        while x < y:
            yield x
            x += step

class GCode(object):
    def __init__(self, cmd, order, **tmpls):
        self.cmd = cmd
        self.order = order
        self.tmpls = tmpls

    def print(self, **args):
        s = "%s" % (self.cmd,)
        for x in self.order:
            try:
                s += " %s" % (self.tmpls[x] % args[x])
            except KeyError:
                pass

        print("%s" % (s,))

if __name__ == '__main__':
    l = len(sys.argv)
    if l != 4 and l != 7:
        print("Usage: arc startx starty radius [startz endz stepz")
        sys.exit(1)

    g1 = GCode("G1", ['f','x','y','z'],
            x="X%0.03f", y="Y%0.03f", z="Z%0.03f", f='F%d')
    g2 = GCode("G2", ['f','x','y','i','j'],
            x="X%0.03f", y="Y%0.03f", i="I%0.03f", j="J%0.03f", f='F%d')
    g3 = GCode("G3", ['f','x','y','i','j'],
            x="X%0.03f", y="Y%0.03f", i="I%0.03f", j="J%0.03f", f='F%d')

    sx=float(sys.argv[1])
    sy=float(sys.argv[2])
    radius=float(sys.argv[3])

    sz=None
    endz=None
    stepz=None

    if l == 7:
        sz=float(sys.argv[4])
        endz=float(sys.argv[5])
        stepz=float(sys.argv[6])

    g1.print(x=sx, y=sy, z=sz, f=100)

    i = 0
    for z in frange(sz, endz, stepz):
        g1.print(z=z)
        cwx=sx+radius
        cwy=sy-radius

        ccwx=sx
        ccwy=sy

        if i % 2 == 0:
            g2.print(x=cwx, y=cwy, i=0, j=-radius, f=10)
        else:
            g3.print(x=ccwx, y=ccwy, i=-radius, j=0, f=10)
        i += 1
