#!/usr/bin/python3

import math

from .exceptions import *
from .utility import *

mill = None

class GCodeStandin():
    def __init__(self, **kwds):
        self.__dict__ = kwds
        self.mill = self.settings.mill

    @property
    def value(self):
        if self._name in self.__dict__:
            val = self.__dict__[self._name]
        else:
            val = None
        return val

    @property
    def tmpl(self):
        if hasattr(self, '_tmpl'):
            return self._tmpl

        if self.__class__.__name__ in self._cmd._tmpls:
            return self._cmd._tmpls[self.__class__.__name__]

        try:
            if int(self.value) == self.value:
                return "%s%%d" % (self.name.upper(),)
        except:
                pass

        return "%s%%f" % (self._name.upper(),)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        value = self.value
        if value is None:
            return ""

        s = self.tmpl % clean(value, quant="1.0")
        s = s.strip()
        try:
            if value % 1 > 0:
                s = s.rstrip(0)
        except:
            pass
        return s

class FStandin(GCodeStandin):
    def __init__(self, *args, **kwds):
        GCodeStandin.__init__(self, *args, **kwds)
        self._name = 'F'

    @property
    def value(self):
        if self.mill.f:
            candidates = [self.mill.f]
        else:
            candidates = [self.settings.feed]

        if self._name in self.__dict__:
            v = self.__dict__[self._name]
            if not v is None:
                candidates.append(clean(v))
        f = min(filter(lambda x: x not in [0, None, math.inf], candidates))
        if not f:
            raise InvalidFeedRate

        # if this is 'F' and mill.f is set:
        #     1) this is an attribute of some other command
        # and 2) a feed rate has been established
        # so remove the property if it's the same rate, to save buffer.
        if f != self.mill.f:
            return f.quantize(1)
        return None

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

        if self._data is None:
            raise ValueError
        s = self.string(**self._data)
        new_tokens = []
        for token in s.split(' '):
            if not token or len(token) == 0:
                continue
            if '.' in token:
                a,c = token.split('.')
                alist = list(alnum_split(a))
                a = alist[0]
                if len(alist) > 1:
                    b = ''.join(alist[1:])
                else:
                    b = ''
                b = b.lstrip('0')
                if len(b) == 0:
                    b = '0'
                c = c.rstrip('0')
                if len(c) == 0:
                    joiner = ""
                else:
                    joiner = "."
            else:
                alist = list(alnum_split(token))
                a = alist[0]
                if len(alist) > 1:
                    b = ''.join(alist[1:])
                else:
                    b = ''
                b = b.lstrip('0')
                if len(b) == 0:
                    b = '0'
                c = ''
                joiner = ""

            token = "%s%s%s%s" % (a,b,joiner,c)
            new_tokens.append(token)
        return ' '.join(new_tokens)

    def __repr__(self):
        return self.__str__()

    def _format(self, order, args, tmpls=None):
        strs = []
        if tmpls is None:
            tmpls = self._tmpls
        if isinstance(order, dict):
            for name, new_order in order.items():
                strs += self._format(new_order, args[name],
                                     tmpls=self._tmpls[name])
        elif isinstance(order, list) or isinstance(order, tuple):
            for new_order in order:
                try:
                    arg = args[new_order]
                except KeyError:
                    continue
                strs += self._format(new_order, arg, tmpls=tmpls[new_order])
        elif isinstance(order, str):
            if isinstance(args, dict):
                try:
                    args = args[order]
                except KeyError:
                    args = None
            if isinstance(tmpls, dict):
                tmpls = tmpls[order]
            if isinstance(tmpls, type):
                kwargs = {
                    order: args,
                    '_name': order,
                    '_cmd': self,
                    }
                obj = tmpls(settings=self.settings, **kwargs)
                x = str(obj)
                if x:
                    strs.append(x)
            elif args is None:
                pass
            else:
                try:
                    strs.append(tmpls % args)
                except:
                    print("could not format \"%s\" %% \"%s\"" % (tmpls,args))
                    raise

        return strs

    def string(self, **args):
        if hasattr(self, '_noname') and self._noname:
            strs = []
        else:
            strs = [self._cmd]
        for x in self._order:
            strs += self._format(x, args)

        s = ' '.join(strs)
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
    _tmpls = {'f':"F%s"}
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
               'end': { 'x':"X%s", 'y': "Y%s", 'z': "Z%s" }
             }
    _target_order = [{'end': ['x', 'y', 'z']}]

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G1(GCodeMaker):
    _cmd = "G1"
    _order = ['f', {'end': ['x', 'y', 'z']}]
    _tmpls = {'f':FStandin, 'FStandin': 'F%d',
               'end': { 'x':"X%s", 'y': "Y%s", 'z': "Z%s" }
             }
    _target_order = [{'end': ['x', 'y', 'z']}]

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G2(GCodeMaker):
    """clockwise arc"""
    _cmd = "G2"
    _order = ['f', 'x', 'y', 'z', 'i', 'j']
    _tmpls = {'x':"X%s", 'y':"Y%s", 'z':"Z%s",
            'f':FStandin, 'FStandin': 'F%d', 'i':'I%s','j':'J%s'}
    _target_order = ['x', 'y', 'z', 'i', 'j', 'f']

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G3(GCodeMaker):
    """anticlockwise arc"""
    _cmd = "G3"
    _order = ['f', 'x', 'y', 'z', 'i', 'j']
    _tmpls = {'x':"X%s", 'y':"Y%s", 'z':"Z%s",
            'f':FStandin, 'FStandin':'F%d', 'i':"I%s",'j':'J%s'}
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
    _tmpls = {'z':"Z%s"}

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
    _tmpls = {'x':"X%s", 'y':"Y%s", 'z':"Z%s"}

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)
