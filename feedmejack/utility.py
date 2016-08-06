#!/usr/bin/python3

import os
import sys
import time
import pint

from decimal import Decimal as _Decimal

from .serial import *

global unitreg
unitreg = pint.UnitRegistry()

def quantity(val, units="mm"):
    q = unitreg.Quantity(val)
    if q.dimensionless:
        q2 = unitreg.Quantity("1 %s" % (units,))
        q._units = q2._units
    return q

def clean(val, quant=None):
    val = _Decimal(val)
    val = val.normalize()
    if quant:
        val = val.quantize(_Decimal(quant))
    return val

Decimal = lambda val,quant=None: clean(val,quant)

def frange(x, y, jump, quant=None):
    x = clean(x, quant=quant)
    y = clean(y, quant=quant)
    jump = clean(jump, quant=quant)
    if jump > 0:
        compare = lambda x,y: x <= y
    else:
        compare = lambda x,y: x >= y
    x = x - jump
    while compare(x + jump, y):
        x = x + jump
        yield clean(x, quant=quant)
    tmpx = x + jump
    if not compare(tmpx, y):
        yield clean(y, quant=quant)

def sweep(x, y, r, quant=None):
    p = None
    for n in frange(x, y, r, quant=quant):
        if p is None:
            p = n
            continue
        yield [p, n]
        p = n
    if not p is None and p != y:
        yield [y, y]

__all__ = ["clean", "frange", "sweep", "Decimal", "quantity"]
