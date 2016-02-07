#!/usr/bin/python3

if __name__ != '__main__':
    from .shapes import *

class Boundary(object):
    def __init__(self, test, positive=True):
        self.test = test
        self.positive = not not positive

    def __contains__(self, thingy):
        if self.test is True:
            ret = True
        elif self.test is False:
            ret = False
        elif hasattr(self.test, '__call__'):
            ret = self.test(thingy)
        elif hasattr(self.test, '__contains__'):
            ret = thingy in self.test
        else:
            ret = bool(thingy)
        if not self.positive:
            return not ret
        return ret

    def __str__(self):
        if self.test is True:
            return "True"
        elif self.test is False:
            return "False"

        if self.positive:
            prefix = ""
        else:
            prefix = "not "

        if hasattr(self.test, '__call__'):
            return "(%s%s)" % (prefix, str(self.test))
        elif hasattr(self.test, '__contains__'):
            return "XY %sin %s" % (prefix, str(self.test),)
        else:
            return "%s%s" % (str(self.test),)

    def __repr__(self):
        return repr(self.test)

    def __mul__(self, other):
        if other < 0:
            positive = not self.positive
            test = self.test
        elif other == 0:
            test = False
        else:
            positive = self.positive
            test = self.test
        return Boundary(test=test, positive=positive)

class Mask(object):
    _strname = "Mask"

    def __init__(self, *bounds):
        self.bounds = []
        for bound in bounds:
            self.add_bound(bound)

    def __contains__(self, point):
        def checkbounds(point, bound):
            if hasattr(bound, '__call__'):
                ret = bound(point)
            elif hasattr(bound, '__contains__'):
                ret = point in bound
            else:
                ret = bool(bound)
            #if hasattr(bound, 'positive') and not bound.positive:
            #    return not ret
            return ret

        blist = []
        blist.extend(self.bounds)
        argpairs = zip([point]*len(blist), blist)
        truths = [checkbounds(x[0], x[1]) for x in argpairs]
        return not False in truths

    def add_bound(self, b, positive=True):
        if isinstance(b, Boundary):
            bound = b
        else:
            bound = Boundary(b, positive=positive)
        self.bounds.append(b)

    def __str__(self):
        st = "%s(" % (self.__class__._strname,)
        s = " and ".join([str(b) for b in self.bounds])
        st += "%s)" % (s,)
        if s:
            return st
        else:
            return "True"

class ShapeMask(Mask):
    _strname = "ShapeMask"

    def __init__(self, shape, positive=True):
        self.box = shape
        Mask.__init__(self)
        self.add_bound(Boundary(shape, positive=positive))

__all__ = ['Mask', 'Boundary']

if __name__ == '__main__':
    from xyz import *
    from shapes import *

    class Tester(object):
        def __call__(self, point):
            return point.x > 3

        def __str__(self):
            return "lambda XY: XY.x > 3"

        def __repr__(self):
            return self.__str__()

    tester = Tester()

    p = XY(1,2)
    #b = Boundary(tester)

    #print("Boundary(%s) yields %s" % (tester,b))

    #t = p in b
    #print("XY(1,2) in b: %s" % (t,))

    #m = Mask()
    #print("Mask(): %s" % (m,))
    #print("p in m === %s in %s === %s" % (p, m, p in m))

    #m.add_bound(b)
    #print("Mask(b): %s" % (m,))
    #print("p in m === %s in %s === %s" % (p, m, p in m))

    #m = Mask()
    #nb = b * -1
    #print("b * -1: %s" % (nb))
    #m.add_bound(b * -1)
    #print("Mask(b): %s" % (m,))
    #print("p in m === %s in %s === %s" % (p, m, p in m))
    #m.add_bound(b)
    #print("Mask(b): %s" % (m,))
    #print("p in m === %s in %s === %s" % (p, m, p in m))

    #print("%s in %s: %s" % (p, b, p in b))
    #print("%s in %s: %s" % (p, nb, p in nb))

    box = Box(XY(0,0), XY(100,100))
    m = ShapeMask(shape=box)
    print("Mask(): %s" % (m,))
    print("p in m === %s in %s === %s" % (p, m, p in m))

    m = ShapeMask(shape=box, positive=False)
    print("Mask(): %s" % (m,))
    print("p in m === %s in %s === %s" % (p, m, p in m))

    m = Mask()
    m.add_bound(Boundary(box))
    box2 = Box(XY(25,25), XY(75,75))
    m.add_bound(Boundary(box2, positive=False))
    print("bound0: %s\nbound1: %s" % (box, box2))
    print("Mask(): %s" % (m,))
    for x in [-1,0,1,24,25,26,74,75,76,99,100,101]:
        p = XY(x,x)
        print("p in m === %s in %s === %s" % (p, m, p in m))

    m = ShapeMask(shape=box)
    print("Mask(): %s" % (m,))
    for x in [-1,0,1,24,25,26,74,75,76,99,100,101]:
        p = XY(x,x)
        print("p in m === %s in %s === %s" % (p, m, p in m))
    m.add_bound(Boundary(box2, positive=False))
    print("Mask(): %s" % (m,))
    for x in [-1,0,1,24,25,26,74,75,76,99,100,101]:
        p = XY(x,x)
        print("p in m === %s in %s === %s" % (p, m, p in m))

    plate = Plate(XY(10,10), 2)
    print("plate: %s" % (plate,))
    m = ShapeMask(shape=plate)
    print("Mask(): %s" % (m,))
    b = Box(XY(10.5,10.5), XY(12,12))
    m.add_bound(Boundary(b, positive=False))
    print("Mask(): %s" % (m,))

    plate = Plate(XY(10,10), 2)
    print("plate: %s" % (plate,))
    m = ShapeMask(shape=plate)
    print("Mask(): %s" % (m,))
    b = Box(XY(10.1,10.1), XY(12,12))
    m.add_bound(Boundary(b, positive=False))
    print("Mask(): %s" % (m,))
