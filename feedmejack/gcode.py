#!/usr/bin/python3

import math

from .exceptions import *

mill = None

class GCodeStandin():
    def __init__(self, name):
        self.name = name

    def make(self, **kwds):
        mill = kwds['mill']
        attr = getattr(mill.gcode, self.name)
        r = attr(**kwds)
        if 'f' in r._data and r._data['f'] in [None, math.inf]:
            r._data['f'] = mill.f
        if r._data['f'] in [None, math.inf]:
            raise InvalidFeedRate

        # if this is 'F' and mill.f is set:
        #     1) this is an attribute of some other command
        # and 2) a feed rate has been established
        # so remove the property if it's the same rate, to save buffer.
        if self.name == 'F' and r._data['f'] == mill.f:
            return None

        return r

class GCodeMaker(object):
    _cmd = ""
    _order = []
    _tmpls = []
    _target_order = []

    def __init__(self, **data):
        self.cmd = self._cmd
        self.order = self._order
        self.tmpls = self._tmpls
        for attr in ['mill', 'settings']:
            if attr in data:
                setattr(self, attr, data[attr])
                del data[attr]
        self._data = data

    def set(self, data):
        self._data = data

    def __str__(self):
        if self._data is None:
            raise ValueError
        return self.string(**self._data)

    def __repr__(self):
        return self.__str__()

    def string(self, **args):
        if hasattr(self, '_noname') and self._noname:
            s = ""
        else:
            s = "%s" % (self._cmd,)
        for x in self._order:
            tmpl = None
            key = None
            val = None
            if isinstance(x, dict):
                for k,vals in x.items():
                    for v in vals:
                        try:
                            tmpl = self._tmpls[k][v]
                            val = args[k][v]
                            key = v
                            break
                        except KeyError:
                            pass
                    break
            elif isinstance(x, list) or isinstance(x, tuple):
                for i in range(1, len(x)):
                    try:
                        tmpl = self._tmpls[x[i]]
                        val = args[x[i]]
                        key = x[i]
                        break
                    except KeyError:
                        pass
            else:
                try:
                    tmpl = self._tmpls[x]
                    val = args[x]
                    key = x
                except KeyError:
                    pass
            if tmpl is None:
                raise InvalidGCodeTemplate(self)
            if val is None:
                raise InvalidGCodeValue("%s" % (self.__class__,))

            if isinstance(tmpl, GCodeStandin):
                kwds = {
                    key:val,
                    'settings': self.settings,
                    'mill': self.mill,
                    }
                x = tmpl.make(**kwds)
                if not x is None:
                    s += " %s" % (x,)
            else:
                s += " %s" % (tmpl % val)

        s = "%s" % (s,)
        return s.strip()

    def strip(self, *args, **kwds):
        r = str(self)
        return r.strip(*args, **kwds)

    def print(self, **args):
        s = self.string(**args)
        print("%s" % (s,))

    def go(self, **args):
        driver.exec(self.string(**args))

    @property
    def target(self):
        s = []
        for item in str(self).split(' '):
            if item[0] in ['X', 'Y', 'Z', 'I', 'J', 'K']:
                s.append(item)
        s = ' '.join(s)
        return s

    def estimate_final_pos(self, **args):
        pass

    def estimate_pct_complete(self, final, status):
        pass

class F(GCodeMaker):
    _cmd = "F"
    _order = ['f',]
    _tmpls = {'f':"F%0.03f"}
    _noname = True

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

    @property
    def f(self):
        if not 'f' in self._data or self._data['f'] in [None, math.inf]:
            self._data['f'] = self.mill.f
        return self._data['f']

class G0(GCodeMaker):
    _cmd = "G0"
    _order = [{'end': ['x', 'y', 'z']}]
    _tmpls = {
               'end': { 'x':"X%0.03f", 'y': "Y%0.03f", 'z': "Z%0.03f" }
             }
    _target_order = [{'end': ['x', 'y', 'z']}]

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G1(GCodeMaker):
    _cmd = "G1"
    _order = ['f', {'end': ['x', 'y', 'z']}]
    _tmpls = {'f':GCodeStandin(name="F"),
               'end': { 'x':"X%0.03f", 'y': "Y%0.03f", 'z': "Z%0.03f" }
             }
    _target_order = [{'end': ['x', 'y', 'z']}]

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G2(GCodeMaker):
    """clockwise arc"""
    _cmd = "G2"
    _order = ['f', 'x', 'y', 'z', 'i', 'j']
    _tmpls = {'x':"X%0.03f", 'y':"Y%0.03f", 'z':"Z%0.03f",
            'f':"F%0.03f", 'i':"I%0.03f",'j':'J%0.03f'}
    _target_order = ['x', 'y', 'z', 'i', 'j', 'f']

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G3(GCodeMaker):
    """anticlockwise arc"""
    _cmd = "G3"
    _order = ['f', 'x', 'y', 'z', 'i', 'j']
    _tmpls = {'x':"X%0.03f", 'y':"Y%0.03f", 'z':"Z%0.03f",
            'f':"F%0.03f", 'i':"I%0.03f",'j':'J%0.03f'}
    _target_order = ['x', 'y', 'z', 'i', 'j', 'f']

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G21(GCodeMaker):
    _cmd = "G21"
    _order = []
    _tmpls = {}

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G43dot1(GCodeMaker):
    """ Dynamic Tool Length Offset"""
    _cmd = "G43.1"
    _order = ['z']
    _tmpls = {'z':"Z%0.03f"}

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G54(GCodeMaker):
    _cmd = "G54"
    _order = []
    _tmpls = {}

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G55(GCodeMaker):
    _cmd = "G55"
    _order = []
    _tmpls = {}

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G90(GCodeMaker):
    _cmd = "G90"
    _order = []
    _tmpls = {}

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G92(GCodeMaker):
    _cmd = "G92"
    _order = ['x', 'y', 'z']
    _tmpls = {'x':"X%0.03f", 'y':"Y%0.03f", 'z':"Z%0.03f"}

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)
