#!/usr/bin/python3

from . import exceptions
from .exceptions import *
from . import gcode
from . import masks
from . import policy
from . import shapes
from . import rasters
from . import tracers
from . import tools
from . import utility
from . import xyz

import array as _array
import fcntl as _fcntl
import os as _os
import pdb as _pdb
import selectors as _selectors
import termios as _termios
import time as _time
import signal as _signal
import sys as _sys
from decimal import Decimal as _Decimal


def _default_status_cb(**kwds):
    pass

class Comms(object):
    def __init__(self, device, speed):
        self.fd = _os.open(device, _os.O_RDWR)
        self.device = _os.fdopen(self.fd, "w+b", buffering=0)

        self.setspeed(speed)

        self.selector = _selectors.PollSelector()

        self.buf = u""

        self.selector.register(self.device, _selectors.EVENT_READ)
        self.callback = _default_status_cb

    def set_callback(self, callback):
        self.callback = callback

    def setspeed(self, speed):
        TCGETS2 = 0x802C542A
        TCSETS2 = 0x402C542B
        BOTHER = 0o010000
        buf = _array.array('i', [0] * 64)
        _fcntl.ioctl(self.fd, TCGETS2, buf)
        buf[2] &= ~_termios.CBAUD
        buf[2] |= _termios.B115200
        buf[9] = buf[10] = _termios.B115200
        _fcntl.ioctl(self.fd, TCSETS2, buf)

    def clear(self):
        self.buf = u""

    def write(self, msg):
        x = msg
        x.strip()
        if len(x):
            self.callback(writing=x)
        if '\r\n' in msg:
            parts = msg.split('\r\n')
            msg = '\n'.join(parts)

        try:
            self.device.write(msg.encode("utf8"))
        except AttributeError:
            self.device.write(msg)

    def readline(self, limit=100, interval=0.01):
        self._timeout = 0

        while self._timeout < limit and not '\n' in self.buf:
            for event, mask in self.selector.select(interval):
                if mask & _selectors.EVENT_READ:
                    self._timeout = 0
                    x = event.fileobj.read(1).decode('utf8')
                    if x != '\r':
                        self.buf = "%s%c" % (self.buf, x)
                    if '\n' in self.buf:
                        continue
                else:
                    if self.callback:
                        self.callback()
                    self._timeout += 1
            else:
                if self.callback:
                    self.callback()
                self._timeout += 1
            if self.callback:
                self.callback()
        if self.callback:
            self.callback()
        if '\n' in self.buf:
            lines = self.buf.split('\n')
            self.buf = '\n'.join(lines[1:])
            ret = str(lines[0]).strip()
            self.callback(read=ret)
            return ret
        else:
            if self.callback:
                self.callback(timeout=True)
            raise Timeout

class Mill(object):
    def __init__(self, settings=None, tool=None):
        self.settings = settings
        if settings.status_cb:
            self.status_cb = settings.status_cb
        else:
            self.status_cb = _default_status_cb
            settings.status_cb = _default_status_cb

        self.comms = Comms(settings.mill_tty, 115200)
        self.comms.set_callback(self.status_cb)

        self._f = 100

        self.maxsent = 2
        self.numsent = 0
        self.queue = []

        self.grbl_version = ""
        self.grbl_params = []
        self.parser_state = set()

        self.status = "Idle"
        self.mpos = xyz.XYZ(x=150, y=150, z=30)
        self.wpos = xyz.XYZ(x=150, y=150, z=30)

        if tool:
            self.tool = tool
        else:
            self.tool = list(tools.find_tool(max_width=0.76, min_length=9.4))[0]
        self.tool.set_dynamic_offset(self.settings.tool_offset)

        self.timeouts = 0
        self.homingfails = 0

    def __del__(self):
        self.settings.reporter.last_show_status=1
        self.get_status()
        self.show_status(status="Exiting", wpos=self.wpos, mpos=self.mpos,
                         target="")

    @property
    def _timeout(self):
        raise AttributeError

    @property
    def f(self):
        return int(self._f)

    def send(self, cmd):
        self.show_status(cmd=cmd)
        cmd = str(cmd)
        cmd = "%s\n" % (cmd.strip(),)
        self.comms.write(cmd)

    def _handle_error(self, response):
        self.show_status(cmd="!")
        self.show_status(cmd="reset")
        self.comms.write("!\x18\n\n\n\n")
        print("error: \"%s\"" % (response,))
        if response == "error: Alarm lock":
            if self.homingfails and self.homingfails < 3:
                self.comms._timeout = 0
            print("Resetting.")
            self.reset()
            return
        elif response in ["error: Bad number format",
                          "error: Expected command letter",]:
            print("Trying to write a newline 'cause that's meaningful...")
            self.comms.write("\n")
            return
        _pdb.set_trace()
        raise RuntimeError

    def _handle_alarm(self, response):
        self.show_status(cmd="!")
        self.show_status(cmd="reset")
        self.comms.write("!\x18\n\n\n\n")
        print("alarm: \"%s\"" % (response,))
        if response == "ALARM: Homing fail":
            self.homingfails += 1
            if self.homingfails < 3:
                self.comms._timeout = 0
                self.show_status(cmd="reset")
                self.show_status(cmd="$X")
                self.comms.write("\x18$X\n")
                self.send(gcode.G55())
                response = self.comms.readline()
                self.send(gcode.G43dot1(z=self.tool.z))
                response = self.comms.readline()
                self.get_status()
                self.send(gcode.G1(z=self.wpos.z - 10, f=10))
                return self._handle_response(response="")
            _sys.exit(2)
            #self.dumpqueue()
            #self.comms.write("\x18\n\n$X\n\n".encode("utf8"))

            #self.reset()
            #self.home()
        _pdb.set_trace()
        raise RuntimeError

    def _handle_post_reset(self, line=None):
        try:
            if line is None:
                line=False
                while not line:
                    line = self.comms.readline()
                    if line.startswith("Grbl"):
                        pass
                    else:
                        line = False
            try:
                self.grbl_version = line.split(' ')[1]
            except IndexError:
                print("line didn't split right: \"%s\"" % (line,))
            self.comms.write("\n")
            line = False
            while not line:
                try:
                    line = self.comms.readline()
                    if line == "":
                        line = False
                except Timeout:
                    break
            if line and line.startswith("['$H'"):
                self.send("$X")
                status = self.get_status()
            for x in range(0, len(self.queue)):
                self.queue[x].sent = False
            self.comms.write("\n")
        except:
            raise

    def _handle_unlock(self):
        self.show_status(cmd="!")
        self.show_status(cmd="reset")
        self.comms.write("!\x18")
        self.show_status(cmd="$X")
        self.comms.write("$X\n")
        line = self.comms.readline()
        self._handle_response(line, process_queue=False)

    def _handle_response(self, response, process_queue=True):
        if response.startswith("Error: ") or response.startswith("error: "):
            self._handle_error(response)
        elif response.startswith("ALARM"):
            self._handle_alarm(response)
        elif response.startswith("Grbl"):
            self._handle_post_reset(line=response)
        elif response.startswith("['$H'"):
            # should not ever get here...
            self._handle_unlock()
        elif response.startswith("[Caution: Unlocked]"):
            # should not ever get here...
            self._handle_unlock()
        elif response == "ok":
            if self.numsent > 0 and self.numsent < self.maxsent:
                self.logresp(response)
                self.dequeue(process_queue=process_queue)
            else:
                return self.get_status()
        elif response == "" or response == " ":
            pass
        elif response.startswith("<") and response.endswith(">"):
            return self.parse_status(response)
        else:
            raise ValueError(response)
        return None

    def get_parser_state(self):
        self.comms.write("$G\n")
        found = False
        while True:
            response = self.comms.readline()
            if response.startswith("["):
                self.parser_state_str = response[1:-1]
                self.parser_state = set(response[1:-1].split(' '))
                response = self.comms.readline()
                found = True
            elif response == "ok":
                return

            self._handle_response(response, process_queue=False)
            if found:
                self.show_status("parser_state_str")
                break

    def parse_status(self, line):
        if line.startswith("<") and line.endswith(">"):
            (status, line) = line[1:-1].split(',', maxsplit=1)

            (tosser, line) = line.split(':', maxsplit=1)
            mpos=[0,0,0]
            (mpos[0],mpos[1],mpos[2],line) = line.split(',', maxsplit=3)
            self.mpos = xyz.XYZ(x=mpos[0], y=mpos[1], z=mpos[2])

            wpos=[0,0,0]
            (tosser, line) = line.split(':', maxsplit=1)
            (wpos[0],wpos[1],wpos[2]) = line.split(',', maxsplit=2)
            self.wpos = xyz.XYZ(x=wpos[0], y=wpos[1], z=wpos[2])

            self.status_cb(status=status, wpos=self.wpos, mpos=self.mpos)
            return status
        return None

    def get_status(self):
        self.comms.write("?")
        count = 0
        timeout = False
        while True:
            try:
                response = self.comms.readline()
            except Timeout:
                self.comms.write("\n")
                try:
                    response = self.comms.readline()
                except Timeout:
                    timeout = True
                    break
            if response is True:
                self.comms.write("?")
                continue

            try:
                return self._handle_response(response, process_queue=False)
            except ValueError:
                if count == 10:
                    raise
                count += 1
                continue
            break

        if timeout:
            raise Timeout
        return None

    def show_status(self, *items, **values):
        kwds = {}
        for item in items:
            kwds[item] = getattr(self, item)
        kwds.update(values)

        self.settings.reporter.show_status(**kwds)

    def wait_for_idle(self, goal="Idle", timeout=10):
        self.comms.callback(goal=goal)
        start = _time.monotonic()
        while True:
            try:
                status = self.get_status()
                self.comms.callback(goal=goal, status=self.status,
                        mpos=self.mpos, wpos=self.wpos)
                break
            except Timeout:
                t = _time.monotonic()
                if t < start + timeout:
                    continue
                raise
        while status != goal:
            if status == None:
                pass
            elif status == "Alarm":
                self.reset()
            elif status == "Run":
                pass
            elif status == "Idle":
                if goal == "Home":
                    self.send("$H")
            elif status == "Hold":
                # try to test *why* this happened? Leave it to the user and
                # give them a continue button?
                self.comms.write("~")
                #self.screen.finalize()
                #_pdb.set_trace()
                #self.reset()
            elif status == "Home":
                pass
            elif status.startswith("Waiting for "):
                pass
            else:
                raise ValueError("status is \"%s\"" % (self.status,))
            try:
                status = self.get_status()
            except Timeout:
                t = _time.monotonic()
                if t < start + timeout:
                    continue
                raise
        if status == goal:
            self.status = status
            self.status_cb(status=self.status, wpos=self.wpos, mpos=self.mpos,
                           goal=goal)

            while True:
                try:
                    self.comms.readline(limit=2, interval=0.25)
                except Timeout:
                    self.comms.clear()
                    break

    def get_grbl_params(self):
        self.comms.write("$#\n")
        found_bracket = False
        grbl_params = []
        while True:
            response = self.comms.readline()
            if response.startswith("["):
                found_bracket = True
                response = response[1:-1]
                if response.startswith("TLO:"):
                    grbl_params.append({'TLO':_Decimal(response[4:])})
                    continue
                elif response.startswith("PRB:"):
                    tmp,value = response[4:].split(':')
                    pos = tmp.split(',')
                    pos = xyz.XYZ(x=pos[0], y=pos[1], z=pos[2])
                    grbl_params.append({response[:3]: [pos,value]})
                    continue
                else:
                    pos = response[4:].split(',')
                    pos = xyz.XYZ(x=pos[0], y=pos[1], z=pos[2])
                    grbl_params.append({response[:3]:pos})
                    continue
            else:
                self._handle_response(response)
            if found_bracket:
                self.grbl_params = grbl_params
                break
        self.wait_for_idle()

    def setup(self):
        self.status = "Waiting for idle"
        self.status_cb(status=self.status, wpos=self.wpos, mpos=self.mpos,
                       goal="Idle")

        while True:
            try:
                self.comms.readline(limit=1)
            except Timeout:
                self.comms.clear()
                break

        self.comms.write('\n')
        #while True:
        #    try:
        #        self.comms.readline(limit=10, interval=1.0)
        #    except Timeout:
        #        self.comms.write('\n')
        #        self.comms.readline()
        #        break

        self.wait_for_idle()
        self.status_cb(status="Idle", wpos=self.wpos, mpos=self.mpos, goal="")
        self.get_parser_state()
        self.wait_for_idle()
        self.get_grbl_params()

        if self.settings.home:
            self.home()
        else:
            self.send(gcode.G55())
            response = self.comms.readline()
            self._handle_response(response)
            self.send(gcode.G43dot1(z=self.tool.z))
            response = self.comms.readline()
            self._handle_response(response)

        self.get_parser_state()
        self.wait_for_idle()

        self.get_grbl_params()
        print("grbl params ($#):")
        for k,v in [list(zip(p.keys(),p.values()))[0] for p in self.grbl_params]:
            print("  %s: %s" % (k, v))
        print("parser state ($G): [%s]" % (' '.join(self.parser_state),))

    def home(self):
        self.status = "Waiting for idle"
        self.status_cb(status=self.status, wpos=self.wpos, mpos=self.mpos,
                goal="Idle")
        self.wait_for_idle("Idle", timeout=90)
        self.comms.clear()
        self.send("$X")
        response = self.comms.readline()
        self.send(gcode.G54())
        response = self.comms.readline()
        self._handle_response(response)
        self.send(gcode.G43dot1(z=0))
        response = self.comms.readline()
        self._handle_response(response)
        self.send("$H")
        self.status = "Waiting for Homing"
        self.status_cb(status=self.status, wpos=self.wpos, mpos=self.mpos)
        self.wait_for_idle("Home", timeout=90)
        self.send(gcode.G55())
        response = self.comms.readline()
        self._handle_response(response)
        self.send(gcode.G43dot1(z=self.tool.z))
        response = self.comms.readline()
        self._handle_response(response)

    def reset(self):
        self.status_cb(status="Resetting", wpos=self.wpos, mpos=self.mpos)
        self.timeouts = 0
        _signal.alarm(0)
        self.show_status(cmd="reset")
        self.show_status(cmd="$X")
        self.comms.write("\x18$X\n")
        self.send(gcode.G54())
        response = self.comms.readline()
        self.show_status(cmd="reset")
        self.comms.write("\x18")
        self.status_cb(status="Resetting", wpos=self.wpos, mpos=self.mpos)
        self._handle_post_reset()
        if self.wpos.z < 10 and self.mpos.z > 90:
            self.send(gcode.G1(z=-10,f=10))

    def park(self):
        self.status_cb(status="Parking", wpos=self.wpos, mpos=self.mpos)
        self.timeouts = 0
        cmds = [
            gcode.G1(end={'z':50}, f=20),
            gcode.G0(end={'x':20, 'y':290}),
            ]
        for cmd in cmds:
            self.send(cmd)
            self.wait_for_idle()

__all__ = ['gcode',
           'masks',
           'policy',
           'rasters',
           'shapes',
           'tools',
           'tracers',
           'utility',
           'xyz'
           ]
