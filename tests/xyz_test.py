# pylint: skip-file

import unittest

from feedmejack import xyz
from decimal import Decimal

class XYTestCase(unittest.TestCase):
    def test_XY_add(self):
        a = xyz.XY(0,1)
        b = xyz.XY(1,1)
        c = xyz.XY(1,2)
        self.assertEqual(a+b, c)

        b = xyz.XY(-3,-4)
        c = xyz.XY(-3,-3)
        self.assertEqual(a+b, c)

    def test_XY_str(self):
        a = xyz.XY(0,1)
        self.assertEqual(str(a), "XY(0,1)")
        a = xyz.XY(0,0)
        self.assertEqual(str(a), "XY(0,0)")
        a = xyz.XY(-0,0)
        self.assertEqual(str(a), "XY(0,0)")
        a = xyz.XY(0,-0)
        self.assertEqual(str(a), "XY(0,0)")
        a = xyz.XY(0,-1)
        self.assertEqual(str(a), "XY(0,-1)")
        a = xyz.XY(-0,-1)
        self.assertEqual(str(a), "XY(0,-1)")
        a = xyz.XY(-1,-1)
        self.assertEqual(str(a), "XY(-1,-1)")

    def test_XY_directions(self):
        a = xyz.XY(0,0)

        left = xyz.XY(-1,0)
        right = xyz.XY(1,0)
        nearer = xyz.XY(0,-1)
        farther = xyz.XY(0,1)

        self.assertTrue(a.rightof(left))
        self.assertFalse(a.leftof(left))
        self.assertFalse(a.nearer(left))
        self.assertFalse(a.farther(left))

        self.assertTrue(a.leftof(right))
        self.assertFalse(a.rightof(right))
        self.assertFalse(a.nearer(right))
        self.assertFalse(a.farther(right))

        self.assertFalse(a.leftof(nearer))
        self.assertTrue(a.farther(nearer))
        self.assertFalse(a.rightof(nearer))
        self.assertFalse(a.nearer(nearer))

        self.assertFalse(a.leftof(farther))
        self.assertFalse(a.farther(farther))
        self.assertFalse(a.rightof(farther))
        self.assertTrue(a.nearer(farther))

        self.assertTrue(a.xlinear(nearer))
        self.assertTrue(a.xlinear(farther))
        self.assertFalse(a.xlinear(left))
        self.assertFalse(a.xlinear(right))

        self.assertFalse(a.ylinear(nearer))
        self.assertFalse(a.ylinear(farther))
        self.assertTrue(a.ylinear(left))
        self.assertTrue(a.ylinear(right))

        b = xyz.XY(3,4)

        self.assertEqual(a.distance(b), Decimal('5.00000'))
        self.assertEqual(a.slope(b), Decimal(4.0)/Decimal(3.0))
        self.assertEqual(b.slope(a), Decimal(4.0)/Decimal(3.0))

        for p in (a, left, right, nearer, farther):
            with self.assertRaises(ValueError):
                x = p.quadrant

        self.assertEqual(xyz.XY(1,1).quadrant, 1)
        self.assertEqual(xyz.XY(-1,1).quadrant, 2)
        self.assertEqual(xyz.XY(-1,-1).quadrant, 3)
        self.assertEqual(xyz.XY(1,-1).quadrant, 4)

        with self.assertRaises(RuntimeError):
            a.yzquadrant
        with self.assertRaises(RuntimeError):
            a.xzquadrant

class XYZTestCase(unittest.TestCase):
    def test_XYZ_identity(self):
        a = xyz.XY(0,0)
        b = xyz.XYZ(0,0,0)
        self.assertEqual(a,b)

        c = xyz.XYZ(1,1,1)
        self.assertEqual(c.yzquadrant, 1)
        self.assertEqual(c.xzquadrant, 1)

        d = xyz.XYZ(-1,-1,-1)
        self.assertEqual(c.distance(d), Decimal('3.46410'))

class LineTestCase(unittest.TestCase):
    def test_Line_str(self):
        a = xyz.Line(xyz.XY(0,0), xyz.XY(1,1))
        self.assertEqual(str(a), "Line(XY(0,0),XY(1,1))")

    def test_Line_length(self):
        a = xyz.Line(xyz.XY(0,0), xyz.XY(1,1))
        self.assertEqual(a.length, Decimal('1.41421'))

        a = xyz.Line(xyz.XY(1,-3), xyz.XY(-5,-7))
        self.assertEqual(a.length, Decimal('7.21110'))

        self.assertEqual(list(a.points), [xyz.XY(1,-3), xyz.XY(-5,-7)])

    def test_Line_bisections(self):
        a = xyz.Line(xyz.XY(0,0), xyz.XY(4,5))

        self.assertEqual(a.middle, xyz.XY(2, 2.5))

        self.assertEqual(a.top, xyz.Line(xyz.XY(2,2.5), xyz.XY(4,5)))
        self.assertEqual(a.bottom, xyz.Line(xyz.XY(0,0), xyz.XY(2,2.5)))

        self.assertEqual(a.xybisector,
                         xyz.Line(xyz.XY(-0.5,4.5), xyz.XY(4.5,0.5)))

    def test_Line_atD(self):
        a = xyz.Line(xyz.XY(0,0), xyz.XY(4,5))
        d = a.length * 2
        self.assertNotEqual(a.atD(d), xyz.XY(7,10))
        self.assertEqual(a.atD(d), xyz.XY(8,10))
        self.assertNotEqual(a.atD(d), xyz.XY(9,10))
        d = 0 - d
        self.assertNotEqual(a.atD(d), xyz.XY(-7,-10))
        self.assertEqual(a.atD(d), xyz.XY(-8,-10))
        self.assertNotEqual(a.atD(d), xyz.XY(-9,-10))

    def test_Line_xyBLAH(self):
        a = xyz.Line(xyz.XY(0,0), xyz.XY(4,5))
        self.assertEqual(a.xyb, 0)
        self.assertEqual(a.xym, 1.25)
        self.assertEqual(a.xybisector.xyb, Decimal("4.1"))
        self.assertEqual(a.xybisector.xym, Decimal("-0.8"))

        self.assertEqual(a.xyYAtX(-4),-5)
        self.assertEqual(a.xyYAtX(0),0)
        self.assertEqual(a.xyYAtX(2),2.5)
        self.assertEqual(a.xyYAtX(4),5)
        self.assertEqual(a.xyYAtX(8),10)

        self.assertEqual(a.xyXAtY(-5),-4)
        self.assertEqual(a.xyXAtY(0),0)
        self.assertEqual(a.xyXAtY(2.5),2)
        self.assertEqual(a.xyXAtY(5),4)
        self.assertEqual(a.xyXAtY(10),8)

        self.assertEqual(a.atX(4), xyz.XY(4,5))

    def test_Line_reverse(self):
        a = xyz.Line(xyz.XY(0,0), xyz.XY(4,5))
        b = xyz.Line(xyz.XY(4,5), xyz.XY(0,0))

        self.assertEqual(a.reverse, b)

    def test_Line_distance(self):
        a = xyz.Line(xyz.XY(0,0), xyz.XY(4,5))
        A = xyz.XY(0,4)
        self.assertEqual(a.distance(A), Decimal('4.06156'))

    def test_Line_sort(self):
        a = xyz.XY(0,0)
        b = xyz.XY(3,0)
        c = xyz.XY(3,4)

        AB = xyz.Line(a,b)
        BC = xyz.Line(b,c)
        AC = xyz.Line(a,c)

        good = [AB, BC, AC]

        for abc in ([AB,BC,AC], [AB,AC,BC],
                    [BC,AB,AC], [BC,AC,AB],
                    [AC,AB,BC], [AC,BC,AB]):
            abc.sort()
            self.assertEqual(good, abc)
