#!/usr/bin/python3

import os
import sys
import time
import pint

from decimal import Decimal as _Decimal

import pdb

def isnumeric(s):
    return all([char.isdigit() for char in s])

def alnum_split(s):
    if len(s) == 0:
        return s
    if s[0].isalpha():
        was_alpha = True
    else:
        was_alpha = False
    current = ""
    for c in s:
        is_alpha = c.isalpha()
        if is_alpha == was_alpha:
            current += c
        else:
            yield current
            current = c
            was_alpha = not was_alpha;
    yield current

def trim_zeroes(s):
    new_tokens = []
    for token in s.split(' '):
        newtoken = []
        if not token or len(token) == 0:
            continue
        if not token[0].isdigit() and token[0] != '-':
            prefix = token[0]
            newtoken.append(prefix)
            token = token[1:]
        else:
            prefix = None

        if not token or len(token) == 0:
            if prefix:
                new_tokens.append(prefix)
            continue

        if prefix and not prefix in ['X','Y','Z','I','J','K']:
            newtoken.append(token)
            new_tokens.append(''.join(newtoken))
            continue

        if token[0] == '-':
            sign = '-'
            token = token[1:]
        else:
            sign = ''
        newtoken.append(sign)

        if '.' in token:
            w,d = token.split('.')
            joiner = '.'
        else:
            w = token
            joiner = ''
            d = ''

        w = w.lstrip('0')
        d = d.rstrip('0')

        if joiner == '.' and len(d) == 0:
            joiner = ''
        if len(w) == 0:
            w = '0'

        newtoken += [w, joiner, d]
        new_tokens.append(''.join(newtoken))

    return ' '.join(new_tokens)

def anchor_pos(s):
    def anchor_one(p, t):
        if p in ['X','Y','Z','I','J','K']:
            t = trim_zeroes(t)
        if t[0] == '-':
            sign = '-'
            t = t[1:]
        else:
            sign = ' '

        if "." in t:
            a,b = t.split('.')
        else:
            a = t
            b = '    '

        a = '%s%s%s' % (' ' * (3-len(a)), sign, a)

        if len(b) != 0 and not b[0] in (' ','.'):
            b = '.%s' % (b,)
        b = '%s%s' % (b, ' ' * (4 - len(b)))

        return '%s%s%s' % (p, a, b)

    s = s.split(' ')
    a = ''.join(s)
    tokens = []
    try:
        a,z = a.split('Z')
        z = anchor_one('Z', z)
    except:
        z = '         '
    tokens.insert(0, z)

    try:
        a,y = a.split('Y')
        y = anchor_one('Y', y)
    except:
        y = '         '
    tokens.insert(0, y)

    try:
        a,x = a.split('X')
        x = anchor_one('X', x)
    except:
        x = '         '
    tokens.insert(0, x)

    return ' '.join(tokens)

global unitreg
unitreg = pint.UnitRegistry()

def clean(val, quant=None):
    try:
        val = _Decimal(val)
    except:
        raise
    val = val.normalize()
    if quant:
        val = val.quantize(_Decimal(quant))
    return val

Decimal = lambda val,quant=None: clean(val,quant)

class Quantity():
    def __init__(self, val, units="mm"):
        q = unitreg.Quantity(val)
        if q.dimensionless:
            q2 = unitreg.Quantity("1 %s" % (units,))
            q._units = q2._units
        self.q = q

    def __lt__(self, other):
        if isinstance(other, Quantity):
            return self.mm < other.mm
        else:
            o = Decimal(other)
            s = Decimal(self.mm)
            return s < o

    def __eq__(self, other):
        if isinstance(other, Quantity):
            return self.mm == other.mm
        else:
            o = Decimal(other)
            s = Decimal(self.mm)
            return s == o

    def __hash__(self):
        return hash(self.q)

    def __str__(self):
        return str(self.q)

    def __abs__(self):
        mm = abs(self.mm)
        x = self.__class__.__new__(Quantity)
        x.__init__(val=mm, units="mm")
        return x

    @property
    def mm(self):
        m = self.q.to("mm").magnitude
        return Decimal(m, "10000000000.0000")

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

__all__ = [
        "isnumeric",
        "alnum_split",
        "anchor_pos",
        "clean",
        "Decimal",
        "frange",
        "Quantity",
        "sweep",
        "trim_zeroes"
        ]
