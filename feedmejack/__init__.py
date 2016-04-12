#!/usr/bin/python3

from . import xyz
from . import shapes
from . import masks
from . import rasters
from . import gcode
from . import tracers
from . import tools

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

class Timeout(Exception):
    pass

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
        timeout = 0

        while timeout < limit and not '\n' in self.buf:
            for event, mask in self.selector.select(interval):
                if mask & _selectors.EVENT_READ:
                    timeout = 0
                    x = event.fileobj.read(1).decode('utf8')
                    if x != '\r':
                        self.buf = "%s%c" % (self.buf, x)
                    if '\n' in self.buf:
                        continue
                else:
                    if self.callback:
                        self.callback()
                    timeout += 1
            else:
                if self.callback:
                    self.callback()
                timeout += 1
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
    def __init__(self, device, status_cb=None, tool=None):
        if status_cb:
            self.status_cb = status_cb
        else:
            self.status_cb = _default_status_cb

        self.comms = Comms(device, 115200)
        self.comms.set_callback(self.status_cb)

        self._f = 100

        self.maxsent = 2
        self.numsent = 0
        self.queue = []

        self.grbl_version = ""
        self.grbl_params = {}

        self.status = "Idle"
        self.mpos = xyz.XYZ(x=150, y=150, z=30)
        self.wpos = xyz.XYZ(x=150, y=150, z=30)

        self.parser_state = set()

        if tool:
            self.tool = tool
        else:
            self.tool = list(tools.find_tool(max_width=0.76, min_length=9.4))[0]

        self.timeouts = 0
        self.homingfails = 0

    @property
    def f(self):
        return int(self._f)

    def send(self, cmd):
        cmd = str(cmd)
        cmd = "%s\n" % (cmd.strip(),)
        self.comms.write(cmd)

    def _handle_error(self, response):
        self.comms.write("!\x18\n\n\n\n")
        print("error: \"%s\"" % (response,))
        _pdb.set_trace()
        raise RuntimeError

    def _handle_alarm(self, response):
        self.comms.write("!\x18\n\n\n\n")
        print("alarm: \"%s\"" % (response,))
        if response == "ALARM: Homing fail":
            self.homingfails += 1
            if self.homingfails > 3:
                pass
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
                line=True
                while line is True:
                    line = self.comms.readline()
                    if not line.startswith("Grbl"):
                        line = True
            try:
                self.grbl_version = line.split(' ')[1]
            except IndexError:
                print("line: \"%s\"" % (line,))
                raise
            line = True
            while line is True:
                line = self.comms.readline()
                if line == "":
                    line = True
            if line.startswith("['$H'"):
                self.comms.write("$X\n")
                line = None
            for x in range(0, len(self.queue)):
                self.queue[x].sent = False
            self.comms.write("\n")
        except:
            raise

    def _handle_unlock(self):
        self.comms.write("!\x18")
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
                self.parser_state = set(response[1:-1].split(' '))
                response = self.comms.readline()
                found = True
            elif response == "ok":
                return

            self._handle_response(response, process_queue=False)
            if found:
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

            self.status_cb(status=status, wpos=self.wpos)
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

    def wait_for_idle(self, goal="Idle", timeout=10):
        start = _time.monotonic()
        while True:
            try:
                status = self.get_status()
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
                status = goal
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
            self.status_cb(status=self.status, wpos=self.wpos)

            while True:
                try:
                    self.comms.readline(limit=2, interval=0.25)
                except Timeout:
                    self.comms.clear()
                    break

    def get_grbl_params(self):
        self.comms.write("$#\n")
        found_bracket = False
        while True:
            response = self.comms.readline()
            if response.startswith("["):
                found_bracket = True
                response = response[1:-1]
                if response.startswith("TLO:"):
                    self.grbl_params['TLO'] = _Decimal(response[4:])
                elif response.startswith("PRB:"):
                    tmp,dunno = response[4:].split(':')
                    pos = tmp.split(',')
                    pos = xyz.XYZ(x=pos[0], y=pos[1], z=pos[2])
                    self.grbl_params[response[:3]] = {"Pos":pos,
                                                      "Dunno": dunno}
                else:
                    pos = response[4:].split(',')
                    pos = xyz.XYZ(x=pos[0], y=pos[1], z=pos[2])
                    self.grbl_params[response[:3]] = pos
            else:
                self._handle_response(response)
            if found_bracket:
                break

    def setup(self):
        self.status = "Waiting for idle"
        self.status_cb(status=self.status, wpos=self.wpos)

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
        self.status_cb(status=" " * 20, wpos=self.wpos)
        #print(" %s,%s,%s" % (self.status, self.mpos, self.wpos))
        self.get_parser_state()
        #pprint.pprint("%s" % (self.parser_state,))
        self.wait_for_idle()
        self.get_grbl_params()
        #pprint.pprint("%s" % (self.grbl_params,))

        self.home()

    def home(self):
        self.status = "Waiting for idle"
        self.status_cb(status=self.status, wpos=self.wpos)
        self.wait_for_idle("Idle", timeout=90)
        self.comms.clear()
        self.send("$H")
        self.status = "Waiting for Homing"
        self.status_cb(status=self.status, wpos=self.wpos)
        self.wait_for_idle("Home", timeout=90)
        self.send(gcode.G55())
        response = self.comms.readline()
        self._handle_response(response)
        self.send(gcode.G43dot1(z=self.tool.z))
        response = self.comms.readline()
        self._handle_response(response)

    def reset(self):
        self.timeouts = 0
        _signal.alarm(0)
        self.comms.write("\x18")
        self.status_cb(status="Resetting", wpos=self.wpos)
        self._handle_post_reset()

__all__ = ['gcode', 'masks', 'rasters', 'shapes', 'tools', 'tracers', \
           'xyz']
