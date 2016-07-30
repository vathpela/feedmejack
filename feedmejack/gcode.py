class GCodeMaker(object):
    _cmd = ""
    _order = []
    _tmpls = []
    _target_order = []

    def __init__(self, **data):
        self.cmd = self._cmd
        self.order = self._order
        self.tmpls = self._tmpls
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
            if isinstance(x, dict):
                for k,vals in x.items():
                    for v in vals:
                        try:
                            s += " %s" % (self._tmpls[k][v] % args[k][v])
                        except KeyError:
                            pass
                    break
            elif isinstance(x, list) or isinstance(x, tuple):
                for i in range(1, len(x)):
                    try:
                        s += " %s" % (self._tmpls[x[i]] % args[x[i]])
                    except KeyError:
                        pass
            else:
                try:
                    s += " %s" % (self._tmpls[x] % args[x])
                except KeyError:
                    pass

        return "%s" % (s,)

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
        args = self._data

        s = ""
        for x in self._target_order:
            if isinstance(x, dict):
                for k,vals in x.items():
                    for v in vals:
                        try:
                            s += " %s" % (self._tmpls[k][v] % args[k][v])
                        except KeyError:
                            pass
                    break
            elif isinstance(x, list) or isinstance(x, tuple):
                for i in range(1, len(x)):
                    try:
                        s += " %s" % (self._tmpls[x[i]] % args[x[i]])
                    except KeyError:
                        pass
            else:
                try:
                    s += " %s" % (self._tmpls[x] % args[x])
                except KeyError:
                    pass

        s = "%s" % (s,)
        return s.strip()

    def estimate_final_pos(self, **args):
        pass

    def estimate_pct_complete(self, final, status):
        pass

class F(GCodeMaker):
    _cmd = "F"
    _order = ['f',]
    _tmpls = {'f':"F%0.03f"}
    _noname = True

class G0(GCodeMaker):
    _cmd = "G0"
    _order = ['f', {'end': ['x', 'y', 'z']}]
    _tmpls = {'f':"F%0.03f",
               'end': { 'x':"X%0.03f", 'y': "Y%0.03f", 'z': "Z%0.03f" }
             }
    _target_order = [{'end': ['x', 'y', 'z']}]

    def __init__(self, **data):
        GCodeMaker.__init__(self, **data)

class G1(GCodeMaker):
    _cmd = "G1"
    _order = ['f', {'end': ['x', 'y', 'z']}]
    _tmpls = {'f':"F%0.03f",
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


