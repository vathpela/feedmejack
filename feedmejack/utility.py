#!/usr/bin/python3

import os
import sys
import time
import pint

from decimal import Decimal as _Decimal

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

class StatusItem():
    def __init__(self, **d):
        self.__dict__ = {'heading':None,
                         'scroll':False,
                         'last':None,
                         'immediate':False,
                         'update':False,
                         'update_target':False,
                         }
        self.__dict__.update(d)

class Reporter(object):
    def __init__(self, settings):
        self.settings = settings
        self.status = {
            'status': StatusItem(heading='status', x=-71, y=20, limit=39),
            'goal': StatusItem(heading='goal', x=-71, y=21, limit=39),
            'target': StatusItem(heading='target', x=-71, y=22, limit=39),
            'wpos': StatusItem(heading='wpos', x=-71, y=23, limit=39),
            'mpos': StatusItem(heading='mpos', x=-71, y=24, limit=39),
            'parser_state_str': StatusItem(heading='params', x=-71, y=25, limit=71),
            'cmd': StatusItem(x=1, y=18, limit=79, scroll=True, immediate=True,
                update_target=True),
            'asctime': StatusItem(x=50, y=20, limit=30, immediate=True),
            'time': StatusItem(x=50, y=21, limit=30, immediate=True),
        }
        self.last_show_status = 0
        self.refresh_threshold = 0

        if self.settings.reporter_tty and self.settings.reporter_tty != '-':
            self.fd = os.open(self.settings.reporter_tty, os.O_RDWR)
        else:
            self.fd = os.open(sys.stdout.fileno(), O_RDWR)
        self.cur_x = 1
        self.cur_y = 1
        self.max_x = 80
        self.max_y = 25
        self.escape("~;")
        self.clear()
        self.gohome()
        self.cursor_save_with_attrs()
        self.set_attribute(hidden=True)
        self.cursor_restore_with_attrs()
        self.scroll_enable(tline=1, bline=19)
        for x in range(0, 25):
            self.next_line()

    @property
    def x(self):
        return self.cur_x
    @property
    def y(self):
        return self.cur_y

    def getattr(self):
        [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]=tty.tcgetattr(self.fd)
        return {'iflag':iflag,
                'oflag':oflag,
                'cflag':cflag,
                'ispeed':ispeed,
                'ospeed':ospeed,
                'cc':cc}

    def escape(self, s=""):
        os.write(self.fd, bytes("\x1b%s" % (s,), "UTF-8"))

    def clear(self):
        self.erase_screen()

    def gotoxy(self, x:int, y:int):
        x = int(x)
        y = int(y)
        if x > self.max_x:
            raise ValueError(x)
        if y > self.max_y:
            raise ValueError(y)

        self.escape("[%d;%dH" % (y, x))
        self.cur_x = x
        self.cur_y = y

    def write(self, s, limit=None):
        if limit is None:
            limit = self.max_x - self.x
        l = min(len(s), limit)
        ns = s[:l]
        ns += " " * (limit - min(len(s), limit))
        os.write(self.fd, bytes(ns, "UTF-8"))
        self.cur_x += l

    def gohome(self):
        self.escape("[H")
        self.cur_x = 1
        self.cur_y = 1

    def reset(self):
        self.escape("c")

    def up(self, n=1):
        n = int(n)
        self.escape("%dA" % (n,))

    def down(self, n=1):
        self.escape("%dB" % (n,))

    def forward(self, n=1):
        n = int(n)
        self.escape("%dCA" % (n,))

    def backward(self, n=1):
        n = int(n)
        self.escape("%dD" % (n,))

    def cursor_save(self):
        self.escape("[s")

    def cursor_restore(self):
        self.escape("[u")

    def cursor_save_with_attrs(self):
        self.escape("7")

    def cursor_restore_with_attrs(self):
        self.escape("8")

    def query_cursor_position(self):
        return self.x, self.y

    def getxy(self):
        return self.query_cursor_position()
        self.escape("[6n")
        esc = os.read(self.fd, 1)
        if esc[0] != "\x1b"[0]:
            raise ValueError(esc)
        c=None
        x=0
        s=""
        while x <= 11:
            x+=1
            c = os.read(self.fd, 1)
            s += c
            if c[0] == 'R':
                if s[0] != '[':
                    raise ValueError(s)
                x,y = s[1:].split(';')
                return fmj.xyz.XY(x=int(x), y=int(y))

        raise ValueError(s)

    def scroll_up(self):
        # "reverse index" in DEC manuals
        self.escape("M")

    def scroll_down(self, n=1):
        # "index" in DEC manuals
        if self.bline:
            self.cursor_save_with_attrs()
            (x,y) = self.getxy()
            n = int(n)
            while n > 0:
                n -= 1
                self.gotoxy(80, self.bline)
                self.escape("E")
                #self.write("\r\n")
            self.gotoxy(x,y)
            self.cursor_restore_with_attrs()

        #self.write("\r\n")
        #self.escape("D%d" % (n,))
        #self.gotoxy(19, 1)

    def next_line(self):
        self.escape("E")

    def scroll_enable(self, tline=None, bline=None):
        self.tline = tline
        self.bline = bline
        if tline != None and bline != None:
            tline = int(tline)
            bline = int(bline)
            self.escape("[%d;%dr" % (tline, bline))
        else:
            self.escape("[r")

    def wrap_enable(self):
        self.escape("[7h")

    def wrap_disable(self):
        self.escape("[7l")

    def erase_to_eol(self):
        self.escape("[K")

    def erase_from_sol(self):
        self.escape("[1K")

    def erase_line(self):
        self.escape("[2K")

    def erase_down(self):
        self.escape("[J")

    def erase_up(self):
        self.escape("[1J")

    def erase_screen(self):
        self.escape("[2J")

    def set_attribute(self, **kwds):
        attrs = {
            'reset': 0,
            'bright': 1,
            'dim': 2,
            'underscore': 3,
            'blink': 4,
            'reverse': 5,
            'hidden': 6,
            }

        l = []
        for kwd in attrs.keys():
            if kwd in kwds:
                l.append(str(attrs[kwd]))
        if l:
            s = ";".join(l)
            self.escape("[%sm" % (s,))

    def update_heading(self, name):
        if not self.status[name].heading:
            return

        x = self.status[name].x
        if x < 0:
            x = self.max_x + x
        y = self.status[name].y
        if y < 0:
            y = self.max_y + y
        h = self.status[name].heading
        hx = x - (len(h) + 1)
        self.gotoxy(hx, y)
        self.write("%s" % (h,))

    def update_value(self, name, value):
        self.status[name].last = value
        x = self.status[name].x
        if x < 0:
            x = self.max_x + x
        y = self.status[name].y
        if y < 0:
            y = self.max_y + y
        if self.status[name].limit:
            limit = self.status[name].limit
        else:
            limit = self.max_x - x
        if self.status[name].scroll:
            self.cursor_restore_with_attrs()
            self.write("%s" % (value,), limit=limit)
            self.next_line()
        else:
            self.gotoxy(x,y)
            self.write("%s" % (value,), limit=limit)

    def show_status(self, **kwds):
        now = time.time()
        updated = False
        (oldx, oldy) = self.getxy()
        self.cursor_save_with_attrs()
        if self.last_show_status == 0:
            for k in self.status.keys():
                self.update_heading(k)
            self.last_show_status = now - 0.7

        for k in kwds.keys():
            if not k in self.status:
                continue
            status = self.status[k]
            if k in ['wpos','mpos']:
                val = kwds[k]
                val = "X%3.3f Y%3.3f Z%3.3f" % (val.x, val.y, val.z)
            elif isinstance(kwds[k], set):
                val = ' '.join(tuple(kwds[k]))
            else:
                val = str(kwds[k])
                val = val.strip()

            soon_enough = now + self.refresh_threshold
            if status.immediate or self.last_show_status < soon_enough:
                if val == status.last:
                    continue
                status.last = val
                if self.last_show_status >= soon_enough or not status.immediate:
                    updated = True

                self.update_value(k, val)
                if status.update_target and hasattr(kwds[k], 'target'):
                    self.update_value('target', kwds[k].target)
                self.cursor_restore_with_attrs()
            elif val != status.last:
                status.last = val
                status.update = True


        if updated:
            for k,v in self.status.items():
                if v.update:
                    v.update = False
                    self.update_value(k, val)
                    self.cursor_restore_with_attrs()
            self.last_show_status = now
            self.show_status(time="%f" % (now,),
                    asctime="%s" % (time.asctime(time.localtime(now)),))

__all__ = ["clean", "frange", "Decimal", "Reporter"]
