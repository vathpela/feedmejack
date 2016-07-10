# pylint: skip-file

import unittest
import math

from feedmejack import shapes, xyz
from decimal import Decimal

class LineTestCase(unittest.TestCase):
    def test_Line(self):
        a = xyz.XY(0,0)
        b = xyz.XY(0.5, 0.86603)
        l = xyz.Line(a, b)
        self.assertEqual(l.xym, Decimal('1.73206'))
        self.assertEqual(l.xyb, Decimal('0'))

        l = xyz.Line(b, a)
        self.assertEqual(l.xym, Decimal('1.73206'))
        self.assertEqual(l.xyb, Decimal('0'))

        a = xyz.XY(0,0)
        b = xyz.XY(0.5, -0.86603)
        l = xyz.Line(a, b)
        self.assertEqual(l.xym, Decimal('-1.73206'))
        self.assertEqual(l.xyb, Decimal('0'))

        l = xyz.Line(b, a)
        self.assertEqual(l.xym, Decimal('-1.73206'))
        self.assertEqual(l.xyb, Decimal('0'))

        a = xyz.XY(1,0)
        b = xyz.XY(1.5, 0.86603)
        l = xyz.Line(a, b)
        self.assertEqual(l.xym, Decimal('1.73206'))
        self.assertEqual(l.xyb, Decimal('-1.73206'))

        a = xyz.XY(3,0)
        b = xyz.XY(4,5)
        l = xyz.Line(a, b)
        self.assertEqual(l.xym, Decimal('5'))
        self.assertEqual(l.xyb, Decimal('-15'))

class RightTriangleTestCase(unittest.TestCase):
    def test_RightTriangle_angles(self):
        a = xyz.XY(0,0)
        b = xyz.XY(3,0)
        c = xyz.XY(3,3)

        for abc in ((a,b,c), (a,c,b), (b,a,c), (b,c,a), (c,a,b), (c,b,a)):
            t = shapes.RightTriangle(abc[0], abc[1], abc[2])

            self.assertTrue(t.a in [xyz.Line(xyz.XY(0,0), xyz.XY(3,0)),
                                    xyz.Line(xyz.XY(3,0), xyz.XY(3,3))])
            self.assertEqual(t.b, xyz.Line(xyz.XY(0,0), xyz.XY(3,3)))
            self.assertTrue(t.c in [xyz.Line(xyz.XY(0,0), xyz.XY(3,0)),
                                    xyz.Line(xyz.XY(3,0), xyz.XY(3,3))])
            self.assertTrue(t.b.length >= t.a.length)
            self.assertTrue(t.b.length >= t.c.length)
            self.assertTrue(t.a.length >= t.c.length)

            self.assertEqual(t.a.length, 3)
            self.assertEqual(t.b.length, Decimal('4.24264'))
            self.assertEqual(t.c.length, 3)

            self.assertEqual(t.BAC, 45)
            self.assertEqual(t.ABC, 90)
            self.assertEqual(t.ACB, 45)

            self.assertEqual(t.Bmid, xyz.XY(1.5, 1.5))

        a = xyz.XY(0,0)
        b = xyz.XY(3,0)
        c = xyz.XY(3,4)

        AB = xyz.Line(a,b)
        AC = xyz.Line(a,c)
        BC = xyz.Line(b,c)

        for abc in ((a,b,c), (a,c,b), (b,a,c), (b,c,a), (c,a,b), (c,b,a)):
            t = shapes.RightTriangle(abc[0], abc[1], abc[2])

            self.assertTrue(t.a in [BC, BC.reverse])
            self.assertEqual(t.b, AC)
            self.assertTrue(t.c in [AB, AB.reverse])
            self.assertTrue(t.b.length >= t.a.length)
            self.assertTrue(t.b.length >= t.c.length)
            self.assertTrue(t.a.length >= t.c.length)

            self.assertEqual(t.a.length, 4)
            self.assertEqual(t.b.length, 5)
            self.assertEqual(t.c.length, 3)

            self.assertEqual(t.BAC, Decimal('36.86990'))
            self.assertEqual(t.ABC, 90)
            self.assertEqual(t.ACB, Decimal('53.13010'))

            self.assertEqual(t.Bmid, xyz.XY(1.5, 2))

class TriangleTestCase(unittest.TestCase):
    def test_Triangle_subsets(self):
        a = xyz.XY(0,0)
        b = xyz.XY(1,0)
        c = xyz.XY(0.5, math.sqrt(Decimal("0.75")))

        for abc in ((a,b,c), (a,c,b), (b,a,c), (b,c,a), (c,a,b), (c,b,a)):
            t = shapes.Triangle(abc[0], abc[1], abc[2])
            self.assertEqual(t.A, a)
            self.assertEqual(t.B, b)
            self.assertEqual(t.C, c)

            self.assertFalse(isinstance(t, shapes.RightTriangle))

            self.assertTrue(t.b.length >= t.a.length)
            self.assertTrue(t.b.length >= t.c.length)
            self.assertTrue(t.a.length >= t.c.length)

            l = t.a.length + t.c.length
            l = t.a.length / l
            l = t.b.length * l

            self.assertEqual(t.a, xyz.Line(a, c))
            self.assertEqual(t.b, xyz.Line(b, c))
            self.assertEqual(t.c, xyz.Line(a, b))

            self.assertEqual(t.a.length, 1)
            self.assertEqual(t.b.length, 1)
            self.assertEqual(t.c.length, 1)

            mids = [xyz.XY(Decimal("0.25000"), Decimal("0.43301")),
                    xyz.XY(0.5, 0),
                    xyz.XY(Decimal("0.75000"), Decimal("0.43301"))]
            self.assertTrue(t.Bmid in mids)

            self.assertTrue(t.ABC > Decimal('59.001') and \
                            t.ABC < Decimal('60.001'))
            self.assertTrue(t.BAC > Decimal('59.001') and \
                            t.ABC < Decimal('60.001'))
            self.assertTrue(t.ACB > Decimal('59.001') and \
                            t.ABC < Decimal('60.001'))

        a = xyz.XY(0,0)
        b = xyz.XY(3,0)
        c = xyz.XY(4,5)

        for abc in ((a,b,c), (a,c,b), (b,a,c), (b,c,a), (c,a,b), (c,b,a)):
            t = shapes.Triangle(abc[0], abc[1], abc[2])

            self.assertFalse(isinstance(t, shapes.RightTriangle))

            self.assertTrue(t.b.length >= t.a.length)
            self.assertTrue(t.b.length >= t.c.length)
            self.assertTrue(t.a.length >= t.c.length)

            self.assertEqual(t.Bmid, xyz.XY(1.17074, 1.46342))

            l = t.a.length + t.c.length
            l = t.a.length / l
            l = t.b.length * l

            self.assertEqual(t.a, xyz.Line(xyz.XY(3,0), xyz.XY(4,5)))
            self.assertEqual(t.b, xyz.Line(xyz.XY(0,0), xyz.XY(4,5)))
            self.assertEqual(t.c, xyz.Line(xyz.XY(0,0), xyz.XY(3,0)))

            self.assertEqual(t.a.length, Decimal('5.09902'))
            self.assertEqual(t.b.length, Decimal('6.40312'))
            self.assertEqual(t.c.length, 3)

            self.assertEqual(t.thetaA, Decimal('51.34019'))
            self.assertEqual(t.thetaC, Decimal('-27.34988'))

            self.assertEqual(t.ABC, Decimal('101.30993'))
            self.assertEqual(t.BAC, Decimal('51.34019'))
            self.assertEqual(t.ACB, Decimal('27.34988'))
