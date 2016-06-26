# pylint: skip-file

import unittest

from feedmejack import xyz
from decimal import Decimal

class XYTestCase(unittest.TestCase):
    def test_add(self):
        a = xyz.XY(0,1)
        b = xyz.XY(1,1)
        c = xyz.XY(1,2)
        self.assertEqual(a+b, c)

        b = xyz.XY(-3,-4)
        c = xyz.XY(-3,-3)
        self.assertEqual(a+b, c)

    def test_str(self):
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

    def test_directions(self):
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
    def test_XY_identity(self):
        a = xyz.XY(0,0)
        b = xyz.XYZ(0,0,0)
        self.assertEqual(a,b)

        c = xyz.XYZ(1,1,1)
        self.assertEqual(c.yzquadrant, 1)
        self.assertEqual(c.xzquadrant, 1)

        d = xyz.XYZ(-1,-1,-1)
        self.assertEqual(c.distance(d), Decimal('3.46410'))
