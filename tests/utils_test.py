# pylint: skip-file

import unittest
import math

from feedmejack.utility import *

class UtilityTest(unittest.TestCase):
    def test_isnumeric(self):
        self.assertTrue(isnumeric("010120312034959340534089023"))
        self.assertFalse(isnumeric("010a20312034959340534089023"))

    def test_alnum_split(self):
        self.assertEqual(["G", "0"], list(alnum_split("G0")))

    def test_trim_zeroes(self):
        self.assertEqual("G0 Z50",
                         trim_zeroes("G0 Z50"))
        self.assertEqual("G1 X87.35 Y110.175 Z19.3",
                         trim_zeroes("G1 X87.350 Y110.175 Z19.30"))
        self.assertEqual("G1 X81 Y107 Z19.3",
                         trim_zeroes("G1 X81.000 Y107.000 Z19.30"))
        self.assertEqual("G1 X0 Y1 Z2",
                         trim_zeroes("G1 X0 Y1 Z2"))
        self.assertEqual("G1 X0.1 Y1 Z2",
                         trim_zeroes("G1 X0.10 Y1 Z2"))
        self.assertEqual("1", trim_zeroes("1"))
        self.assertEqual("-0.1", trim_zeroes("-00.1"))
        self.assertEqual("0.1", trim_zeroes("0.1"))
        self.assertEqual("G43.0 X0.1 Y1 Z2",
                         trim_zeroes("G43.0 X0.10 Y1 Z2"))
        self.assertEqual("G04.0 X0.1 Y1 Z2",
                         trim_zeroes("G04.0 X0.10 Y1 Z2"))

    def test_anchor_pos(self):
        self.assertEqual("X   0.1   Y   1     Z   2    ",
                         anchor_pos("X0.10 Y1 Z2"))
