# pylint: skip-file

import unittest

from feedmejack import shapes, xyz
from decimal import Decimal

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

            self.assertEqual(t.a.length, 3)
            self.assertEqual(t.b.length, Decimal('4.24264'))
            self.assertEqual(t.c.length, 3)

            self.assertEqual(t.BAC, 45)
            self.assertEqual(t.ABC, 90)
            self.assertEqual(t.ACB, 45)

        a = xyz.XY(0,0)
        b = xyz.XY(3,0)
        c = xyz.XY(3,4)

        AB = xyz.Line(a,b)
        AC = xyz.Line(a,c)
        BC = xyz.Line(b,c)

        for abc in ((a,b,c), (a,c,b), (b,a,c), (b,c,a), (c,a,b), (c,b,a)):
            t = shapes.RightTriangle(abc[0], abc[1], abc[2])

            self.assertTrue(t.a in [AB, AB.reverse])
            self.assertEqual(t.b, AC)
            self.assertTrue(t.c in [BC, BC.reverse])

            self.assertEqual(t.a.length, 3)
            self.assertEqual(t.b.length, 5)
            self.assertEqual(t.c.length, 4)

            self.assertEqual(t.BAC, Decimal('53.13010'))
            self.assertEqual(t.ABC, 90)
            self.assertEqual(t.ACB, Decimal('36.86990'))
