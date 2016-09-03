#!/usr/bin/python3

import array
import collections
from ctypes import *
import fcntl
import os
import termios
import time
import pdb

from .utility import *
from . import xyz

class Termios2(Structure):
    #
    # typedef unsigned char   cc_t;
    # typedef unsigned int    speed_t;
    # typedef unsigned int    tcflag_t;
    #
    # #define NCCS 19
    #
    # struct termios2 {
    #         tcflag_t c_iflag;               /* input mode flags */
    #         tcflag_t c_oflag;               /* output mode flags */
    #         tcflag_t c_cflag;               /* control mode flags */
    #         tcflag_t c_lflag;               /* local mode flags */
    #         cc_t c_line;                    /* line discipline */
    #         cc_t c_cc[NCCS];                /* control characters */
    #         speed_t c_ispeed;               /* input speed */
    #         speed_t c_ospeed;               /* output speed */
    # };

    _fields_ = [('c_iflag', c_uint),
                ('c_oflag', c_uint),
                ('c_cflag', c_uint),
                ('c_lflag', c_uint),
                ('c_line', c_ubyte),
                ('c_cc', c_ubyte * 19),
                ('c_ispeed', c_uint),
                ('c_ospeed', c_uint),
                ]

    def asbuf(self):
        buf = array.array('I', [0] * int(self.__sizeof__() / 4))
        buf[0] = self.c_iflag
        buf[1] = self.c_oflag
        buf[2] = self.c_cflag
        buf[3] = self.c_lflag

        buf[4] = self.c_line         \
                |(self.c_cc[0] << 8) \
                |(self.c_cc[1] << 16)\
                |(self.c_cc[2] << 24)

        buf[5] = (self.c_cc[3])      \
                |(self.c_cc[4] << 8) \
                |(self.c_cc[5] << 16)\
                |(self.c_cc[6] << 24)

        buf[6] = (self.c_cc[7])      \
                |(self.c_cc[8] << 8) \
                |(self.c_cc[9] << 16)\
                |(self.c_cc[10] << 24)

        buf[7] = (self.c_cc[11])      \
                |(self.c_cc[12] << 8) \
                |(self.c_cc[13] << 16)\
                |(self.c_cc[14] << 24)

        buf[8] = (self.c_cc[15])      \
                |(self.c_cc[16] << 8) \
                |(self.c_cc[17] << 16)\
                |(self.c_cc[18] << 24)

        buf[9] = self.c_ispeed
        buf[10] = self.c_ospeed
        return buf

    def frombuf(self, buf):
        self.c_iflag = buf[0]
        self.c_oflag = buf[1]
        self.c_cflag = buf[2]
        self.c_lflag = buf[3]

        self.c_line = buf[4] & 0xff

        self.c_cc[0] = (buf[4] & 0xff00) >> 8
        self.c_cc[1] = (buf[4] & 0xff0000) >> 16
        self.c_cc[2] = (buf[4] & 0xff000000) >> 24
        self.c_cc[3] = (buf[5] & 0xff)

        self.c_cc[4] = (buf[5] & 0xff00) >> 8
        self.c_cc[5] = (buf[5] & 0xff0000) >> 16
        self.c_cc[6] = (buf[5] & 0xff000000) >> 24
        self.c_cc[7] = (buf[6] & 0xff)

        self.c_cc[8] = (buf[6] & 0xff00) >> 8
        self.c_cc[9] = (buf[6] & 0xff0000) >> 16
        self.c_cc[10] = (buf[6] & 0xff000000) >> 24
        self.c_cc[11] = (buf[7] & 0xff)

        self.c_cc[12] = (buf[7] & 0xff00) >> 8
        self.c_cc[13] = (buf[7] & 0xff0000) >> 16
        self.c_cc[14] = (buf[7] & 0xff000000) >> 24
        self.c_cc[15] = (buf[8] & 0xff)

        self.c_cc[16] = (buf[8] & 0xff00) >> 8
        self.c_cc[17] = (buf[8] & 0xff0000) >> 16
        self.c_cc[18] = (buf[8] & 0xff000000) >> 24

        self.c_ispeed = buf[9]
        self.c_ospeed = buf[10]

        pass

    def get(self, fd):
        TCGETS2 = 0x802C542A
        buf = self.asbuf()
        fcntl.ioctl(fd, TCGETS2, buf)
        self.frombuf(buf)

    def set(self, fd):
        TCSETS2 = 0x402C542B
        buf = self.asbuf()
        fcntl.ioctl(fd, TCSETS2, buf)

class SerialPort():
    baud_table = {
        0:termios.B0,
        50:termios.B50,
        75:termios.B75,
        110:termios.B110,
        134:termios.B134,
        150:termios.B150,
        200:termios.B200,
        300:termios.B300,
        600:termios.B600,
        1200:termios.B1200,
        1800:termios.B1800,
        2400:termios.B2400,
        4800:termios.B4800,
        9600:termios.B9600,
        19200:termios.B19200,
        38400:termios.B38400,
        57600:termios.B57600,
        115200:termios.B115200,
        230400:termios.B230400,
        460800:termios.B460800,
        500000:termios.B500000,
        576000:termios.B576000,
        921600:termios.B921600,
        1000000:termios.B1000000,
        1152000:termios.B1152000,
        1500000:termios.B1500000,
        2000000:termios.B2000000,
        2500000:termios.B2500000,
        3000000:termios.B3000000,
        3500000:termios.B3500000,
        4000000:termios.B4000000,
        }

    def __init__(self, settings, name):
        self.settings = settings
        self.name = name

        #print("tty_path: %s tty_speed: %s" % (self.tty_path, self.tty_speed))
        if self.tty_path and self.tty_path != '-':
            self.fd = os.open(self.tty_path, os.O_RDWR)
        else:
            self.fd = os.open(sys.stdout.fileno(), O_RDWR)
        self.device = os.fdopen(self.fd, "w+b", buffering=0)

        self.termios = Termios2()

        self.set_speed(self.tty_speed)

    @property
    def tty_path(self):
        n = '%s_tty' % (self.name,)
        return getattr(self.settings, n)

    @property
    def tty_speed(self):
        n = '%s_tty_speed' % (self.name,)
        return getattr(self.settings, n)

    def set_speed(self, speed):
        BOTHER = 0o010000
        IBSHIFT = 16

        ifound = False
        ofound = False
        iclose = speed/50
        oclose = speed/50
        ibinput = False

        #print("setting speed to %s" % (speed,))
        self.termios.get(self.fd)

        self.termios.c_ispeed = self.termios.c_ospeed = speed

        if (self.termios.c_cflag & termios.CBAUD) == BOTHER:
            oclose = 0
        if ((self.termios.c_cflag >> IBSHIFT) & termios.CBAUD) == BOTHER:
            iclose = 0
        if (self.termios.c_cflag >> IBSHIFT) & termios.CBAUD:
            ibinput = True

        self.termios.c_cflag &= ~termios.CBAUD
        #print('self.termios.c_cflag: 0x%x' % (self.termios.c_cflag,))

        bauds = list(SerialPort.baud_table.keys())
        bauds.sort()
        for i in range(0, len(SerialPort.baud_table)):
            baud = bauds[i]
            bits = SerialPort.baud_table[baud]

            if speed - oclose <= baud and speed + oclose >= baud:
                self.termios.c_cflag |= bits
                ofound = i
            if speed - iclose <= baud and speed + iclose >= baud:
                if ofound == i and not ibinput:
                    ifound = i
                else:
                    ifound = i
                    self.termios.c_cflag |= bits << IBSHIFT
        #print('self.termios.c_cflag: 0x%x' % (self.termios.c_cflag,))
        if ofound is False:
            self.termios.c_cflag = BOTHER;
        #print('self.termios.c_cflag: 0x%x' % (self.termios.c_cflag,))

        if ifound is False and ibinput:
            self.termios.c_cflag |= BOTHER << IBSHIFT;
        #print('self.termios.c_cflag: 0x%x' % (self.termios.c_cflag,))

        self.termios.set(self.fd)

    def getattr(self):
        [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]=tty.tcgetattr(self.fd)
        return {'iflag':iflag,
                'oflag':oflag,
                'cflag':cflag,
                'ispeed':ispeed,
                'ospeed':ospeed,
                'cc':cc}

class Terminal(SerialPort):
    def __init__(self, settings, name):
        SerialPort.__init__(self, settings, name)

        self.count = 0

        self.cur_x = 1
        self.cur_y = 1
        self.saved_x = 1
        self.saved_y = 1
        self.max_x = 80
        self.max_y = 25
        time.sleep(0.2)
        self.escape("~;")
        time.sleep(0.2)
        self.clear()
        self.gohome()
        self.set_attribute(hidden=True)
        self.scroll_enable(tline=1, bline=18)
        self.gotoxy(0,self.bline)
        self.cursor_save_with_attrs()
        self.cursor_restore_with_attrs()

    @property
    def x(self):
        return self.cur_x
    @property
    def y(self):
        return self.cur_y

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
        if x == self.x and y == self.y:
            #print("not doing gotoxy(%d,%d)" % (x,y))
            self.count += 1
            if self.count > 5:
                raise RuntimeError
            #return
        self.count = 0
        #print("doing gotoxy(%d,%d)" % (x,y))

        self.escape("[%d;%dH" % (y, x))
        time.sleep(0.01)
        self.cur_x = x
        self.cur_y = y

    def write(self, s, limit=None):
        #print("doing write")
        if limit is None:
            limit = self.max_x - self.x
        l = min(len(s), limit)
        ns = s[:l]
        ns += " " * (limit - min(len(s), limit))
        os.write(self.fd, bytes(ns, "UTF-8"))
        self.cur_x += l
        if '\n' in ns:
            self.cur_y += 1

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
        #print("doing cursor_save")
        self.saved_x = self.cur_x
        self.saved_y = self.cur_y
        self.escape("[s")
        time.sleep(0.01)

    def cursor_restore(self):
        #print("doing cursor_restore")
        self.cur_x = self.saved_x
        self.cur_y = self.saved_y
        self.escape("[u")
        time.sleep(0.01)

    def cursor_save_with_attrs(self):
        if self.cursor_saved:
            #print("doing cursor_save_with_attrs")
            return
        #print("doing cursor_save_with_attrs")
        self.saved_x = self.cur_x
        self.saved_y = self.cur_y
        self.cursor_saved = True
        self.escape("7")
        time.sleep(0.01)

    def cursor_restore_with_attrs(self):
        if self.cursor_saved:
            #print("doing cursor_restore_with_attrs")
            pass
        else:
            #print("doing cursor_restore_with_attrs but not saved before")
            pass
        self.cur_x = self.saved_x
        self.cur_y = self.saved_y
        self.escape("8")
        time.sleep(0.01)

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
                return xyz.XY(x=int(x), y=int(y))

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
        self.cur_y += 1
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

class StatusItem():
    def __init__(self, **d):
        if not "name" in d:
            d['name'] = d['heading']
        self.__dict__ = {'heading':None,
                         'scroll':False,
                         'last':None,
                         'immediate':True,
                         'update':False,
                         'update_target':False,
                         'include_time':False,
                         'name':None,
                         }
        self.__dict__.update(d)

    def __str__(self):
        if self.name in ['wpos', 'mpos', 'offset']:
            if isinstance(self.last, str):
                return self.last
            if self.last.x < 0:
                xsign = '-'
            else:
                xsign = ' '

            if self.last.y < 0:
                ysign = '-'
            else:
                ysign = ' '

            if hasattr(self.last, 'z'):
                if self.last.z < 0:
                    zsign = '-'
                else:
                    zsign = ' '

                val = "X%c%03.3f Y%c%03.3f Z%c%03.3f" % (
                        xsign, abs(self.last.x),
                        ysign, abs(self.last.y),
                        zsign, abs(self.last.z))
            else:
                val = "X%c%03.3f Y%c%03.3f          " % (
                        xsign, abs(self.last.x),
                        ysign, abs(self.last.y))
        elif self.name == 'tlo':
            if isinstance(self.last, str):
                return self.last
            val = 'Z%03.3f' % (self.last.z)
        else:
            val = str(self.last)
        return val

class Reporter(Terminal):
    def __init__(self, settings):
        self.cursor_saved = False
        Terminal.__init__(self, settings, "reporter")
        self.status = {
            'status': StatusItem(heading='status', x=-71, y=20, limit=30),
            'goal': StatusItem(heading='goal', x=-71, y=21, limit=30),
            'target': StatusItem(heading='target', x=-71, y=22, limit=30),
            'wpos': StatusItem(heading='wpos', x=-71, y=23, limit=30),
            'mpos': StatusItem(heading='mpos', x=-71, y=24, limit=30),
            'parser_state_str': StatusItem(heading='params', x=-71, y=25, limit=50),
            'cmd': StatusItem(x=1, y=17, limit=79, scroll=True, immediate=True,
                update_target=True, include_time=True, name="cmd"),
            'start': StatusItem(x=50, y=20, limit=30, name='start'),
            'asctime': StatusItem(x=50, y=21, limit=30, immediate=False,
                name="asctime"),
            'time': StatusItem(x=50, y=22, limit=30, immediate=False,
                name="time"),
            'tlo': StatusItem(heading='tlo', x=65, y=25, limit=15),
            'offset': StatusItem(x=50, y=23, limit=30, name="offset"),
        }
        self.last_show_status = 0
        self.refresh_threshold = 0

        for x in range(0, 25):
            self.next_line()

        for name in self.status.keys():
            self.update_heading(name)
        self.cursor_restore_with_attrs()

        self.start_time = time.time()

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
        #print("updating heading for %s at (%d,%d) (value at (%d,%d))" % (h, hx,
        #    y, x, y))
        #time.sleep(0.05)
        self.gotoxy(hx, y)
        time.sleep(0.1)
        self.write("%s" % (h,))

    def update_value(self, name, value):
        if name == 'status' and (isinstance(value, (xyz.XY, xyz.XYZ)) or
                'X' in str(value)):
            print("status is \"%s\" (%s)" % (value, value.__class__))
            raise RuntimeError
        if name == 'wpos' and not (isinstance(value, (xyz.XY, xyz.XYZ,StatusItem)) or
            value[0] == 'X'):
            print("wpos is \"%s\" (%s)" % (value, value.__class__))
            raise RuntimeError
        if name == 'mpos' and not (isinstance(value, (xyz.XY, xyz.XYZ,
            StatusItem)) or
                value[0] == 'X'):
            print("mpos is \"%s\" (%s)" % (value, value.__class__))
            raise RuntimeError

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
        #print("updating value for %s at (%d,%d)" % (name, x, y))
        if self.status[name].scroll:
            self.cursor_restore_with_attrs()
            self.write("%s" % (value,), limit=limit)
            self.next_line()
        else:
            self.gotoxy(x,y)
            self.write("%s" % (value,), limit=limit)
        self.status[name].update = False

    def update_item_cache(self, name, value, target=None):
        status = self.status[name]
        ret = False
        if status.last != value:
            ret = True
        if status.update_target and target != None:
            ret = self.update_item_cache('target', target)

        if ret:
            status.last = value
            status.update = True
        self.status[name] = status
        return ret

    def show_status(self, **kwds):
        now = time.time()
        updated = False
        restore = False
        if self.last_show_status == 0:
            self.last_show_status = now - 0.7

        for k in kwds.keys():
            if not k in self.status:
                continue
            status = self.status[k]
            if k in ['wpos','mpos','offset','tlo']:
                val = StatusItem(name=k, last=kwds[k])
                val = str(val)
            elif isinstance(kwds[k], set):
                val = ' '.join(tuple(kwds[k]))
            else:
                val = str(kwds[k])
                val = val.strip()

            if status.include_time:
                t = Decimal(time.time(), "1000000000.0")
                val = "%s   %s" % (t, val)

            if status.update_target and hasattr(kwds[k], 'target'):
                kwargs = {'target': kwds[k].target}
            else:
                kwargs = {}
            new_updated = self.update_item_cache(k, val, **kwargs)

            if new_updated:
                if status.immediate:
                    self.update_value(k, val)
                    restore = True
                else:
                    updated = True

        if not updated:
            for u in [v.update for k,v in self.status.items()]:
                updated = True

        soon_enough = self.last_show_status + self.refresh_threshold
        if updated and now > soon_enough:
            for k,v in self.status.items():
                if v.update:
                    v.update = False
                    self.update_value(k, v)
                    restore = True
            self.last_show_status = now

        if restore:
            if now > soon_enough:
                self.update_value('time', '%f' % (now,))
                self.update_value('asctime',
                        "%s" % (time.asctime(time.localtime(now)),))
                self.update_value('start',
                        "%s" % (time.asctime(time.localtime(self.start_time)),))
            #self.gotoxy(0, self.bline)
            self.cursor_restore_with_attrs()

__all__ = [
        "Reporter",
        "SerialPort",
        "Terminal",
        ]

