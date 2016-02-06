#!/usr/bin/python3

import copy
import curses
import os
import pprint
import sys
import signal
import time
import traceback

import pdb

class Alarm(Exception):
    pass

class Position(object):
    def __init__(self, name=None, x=0, y=0, z=0):
        self.name = name
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Position(x=self.x + other.x,
                        y=self.y + other.y,
                        z=self.z + other.z)

    def __str__(self):
        s=""
        if self.name:
            s="%s" % (self.name,)
        s = "%s(%0.03f,%0.03f,%0.03f)" % (s,self.x, self.y, self.z)
        return s

    def __repr__(self):
        return self.__str__()

    def higher(self, other):
        return self.z > other.z
    def lower(self, other):
        return zelf.z < other.z

    def left(self, other):
        return self.x < other.x
    def right(self, other):
        return self.x > other.x

    def nearer(self, other):
        return self.y < other.y
    def farther(self, other):
        return self.y > other.y

# ok
# ALARM: Hard limit
# [Reset to continue]
#
# Grbl 0.9j ['$' for help]
# ['$H'|'$X' to unlock]
# <Alarm,MPos:69.576,42.130,-73.089,WPos:69.576,42.130,-73.089>
# error: Alarm lock
# [Caution: Unlocked]
# ok
# ok
#

class Tool(object):
    def __init__(self, length):
        self.length = length

    def __repr__(self):
        return "Z%0.03f" % (self.length,)

    def __str__(self):
        return "Z%0.03f" % (self.length,)

class GCode(object):
    def __init__(self, s):
        self.s = s
        self.sent = False
        self.response = None

    def __str__(self):
        return "%s" % (self.s,)

    def __repr__(self):
        return "%s" % (self.s,)

class GCodeMaker(object):
    _cmd = ""
    _order = []
    _tmpls = []

    def __init__(self, driver):
        self.cmd = self._cmd
        self.order = self._order
        self.tmpls = self._tmpls
        self.driver = driver

    def string(self, **args):
        s = "%s" % (self._cmd,)
        for x in self._order:
            try:
                s += " %s" % (self._tmpls[x] % args[x])
            except KeyError:
                pass

        return "%s" % (s,)

    def print(self, **args):
        s = self.string(**args)
        print("%s" % (s,))

    def go(self, **args):
        driver.exec(self.string(**args))

    def estimate_final_pos(self, **args):
        pass

    def estimate_pct_complete(self, final, status):
        pass

class G0(GCodeMaker):
    _cmd = "G0"
    _order = ['x', 'y', 'z']
    _tmpls = {'x':"X%0.03f", 'y':"Y%0.03f", 'z':"Z%0.03f"}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G1(GCodeMaker):
    _cmd = "G1"
    _order = ['f', 'x', 'y', 'z']
    _tmpls = {'f':"F%0.03f",'x':"X%0.03f", 'y':"Y%0.03f", 'z':"Z%0.03f"}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G2(GCodeMaker):
    _cmd = "G2"
    _order = ['f', 'x', 'y', 'z', 'i', 'j']
    _tmpls = {'x':"X%0.03f", 'y':"Y%0.03f", 'z':"Z%0.03f",
            'f':"F%0.03f", 'i':"I%0.03f",'j':'J%0.03f'}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G3(GCodeMaker):
    _cmd = "G3"
    _order = ['x', 'y', 'z']
    _tmpls = {'x':"X%0.03f", 'y':"Y%0.03f", 'z':"Z%0.03f",
            'f':"F%0.03f", 'i':"I%0.03f",'j':'J%0.03f'}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G21(GCodeMaker):
    _cmd = "G21"
    _order = []
    _tmpls = {}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G43dot1(GCodeMaker):
    _cmd = "G43.1"
    _order = ['z']
    _tmpls = {'z':"Z%0.03f"}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G54(GCodeMaker):
    _cmd = "G54"
    _order = []
    _tmpls = {}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G55(GCodeMaker):
    _cmd = "G55"
    _order = []
    _tmpls = {}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G90(GCodeMaker):
    _cmd = "G90"
    _order = []
    _tmpls = {}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class G92(GCodeMaker):
    _cmd = "G92"
    _order = ['x', 'y', 'z']
    _tmpls = {'x':"X%0.03f", 'y':"Y%0.03f", 'z':"Z%0.03f"}

    def __init__(self, driver):
        GCodeMaker.__init__(self, driver)

class Mill(object):
    def __init__(self, device, screen=None):
        self.fd = os.open(device, os.O_RDWR)
        self.device = os.fdopen(self.fd, "w+b", buffering=0)

        self.screen = screen

        self._f = 100

        self.maxsent = 5
        self.numsent = 0
        self.queue = []

        self.grbl_version = ""
        self.grbl_params = {}

        self.status = "Idle"
        self.mpos = Position(name="MPos", x=150, y=150, z=30)
        self.wpos = Position(name="WPos", x=150, y=150, z=30)

        self.parser_state = set()

        self.tool = Tool(20.25)

        self.logspool = []
        self.respspool = []

        self.running = True
        self.timeouts = 0

        self.homingfails = 0

    @property
    def f(self):
        return int(self._f)

    def stop(self):
        try:
            if curses.LINES > 75:
                tb = traceback.format_stack()[-49:]
                l = len(tb)
                if l > 50:
                    l = 50
                for x in range(0, l):
                    self.screen.addstr(x+25, 0, " " * 80)
                    self.screen.redraw()
                    self.screen.addstr(x+25, 0, tb[x])
                    self.screen.redraw()
        except curses.error:
            raise
        self.running = False
        self.screen.addstr(0, 20, "STOPPED")
        self.screen.redraw()

    def start(self):
        self.running = True
        self.screen.addstr(0, 20, "RUNNING")
        self.screen.redraw()

        try:
            for x in range(0, 50):
                self.screen.addstr(x+25, 0, " " * 80)
                self.screen.redraw()
        except curses.error:
            pass


    def mainloop(self):
        qd = len(mill.queue)
        if qd == 0:
            return False

        if self.numsent > 0:
            line = self._getline()
            if line is True:
                mill.get_status()
                scr.status(mill.status, mill.wpos)
                scr.drawtime()
                return True
            else:
                mill._handle_response(line)
                mill.get_status()
                scr.status(mill.status, mill.wpos)
                scr.drawtime()
                return False

        return False

    def dumpqueue(self):
        self.stop()
        for x in range(0, len(self.queue)):
            self.queue.pop(0)
        self.numsent = 0

    def quiesce(self, num=0):
        self.stop()
        if len(self.queue) <= num:
            self.start()
            return

        while self.numsent > num:
            #self.stop()
            if len(self.queue) == 0:
                break
            self.mainloop()
            self.wait_for_idle(timeout=1)
            #self.start()
        self.start()

    def _getline(self):
        def handler(signum, frame):
            raise Alarm

        waiting = True
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(1)
        try:
            line = self.device.readline().decode('utf8').strip()
            signal.alarm(0)
            waiting = False
            if line:
                self.timeouts = 0
                return line
        except Alarm:
            if waiting:
                waiting = False
                self.timeouts += 1
                self.screen.drawtime()
                if self.timeouts == 10:
                    self.reset()
                else:
                    self.screen.status("Timeout %d" % (self.timeouts,),
                                self.wpos)
                return True
            return line
        # print("got \"%s\"" % (line,))
        return line

    def log(self, msg):
        self.logspool.append(msg)
        if len(self.logspool) > 9:
            self.logspool.pop(0)

        self.screen.addstr(2, 0, "log:")
        self.screen.addstr(3, 0, " " * 40)
        self.screen.addstr(4, 0, " " * 40)
        self.screen.addstr(5, 0, " " * 40)
        self.screen.addstr(6, 0, " " * 40)
        self.screen.addstr(7, 0, " " * 40)
        self.screen.addstr(8, 0, " " * 40)
        self.screen.addstr(9, 0, " " * 40)
        self.screen.addstr(10, 0, " " * 40)
        self.screen.addstr(11, 0, " " * 40)
        self.screen.redraw()
        for x in range(0, len(self.logspool)):
            if x > 11:
                break
            self.screen.addnstr(3+x, 1, self.logspool[x], 39)
        self.screen.redraw()

    def logresp(self, msg):
        self.respspool.append(msg)
        if len(self.respspool) > 9:
            self.respspool.pop(0)

        self.screen.addstr(3, 40, " " * 40)
        self.screen.addstr(4, 40, " " * 40)
        self.screen.addstr(5, 40, " " * 40)
        self.screen.addstr(6, 40, " " * 40)
        self.screen.addstr(7, 40, " " * 40)
        self.screen.addstr(8, 40, " " * 40)
        self.screen.addstr(9, 40, " " * 40)
        self.screen.addstr(10, 40, " " * 40)
        self.screen.addstr(11, 40, " " * 40)
        self.screen.redraw()
        for x in range(0, len(self.respspool)):
            if x > 11:
                break
            self.screen.addnstr(3+x, 41, self.respspool[x], 39)
        self.screen.redraw()

    def send(self, cmd):
        cmd = str(cmd)
        self.log(cmd)
        cmd = "%s\n" % (cmd.strip(),)
        self.device.write(cmd.encode("utf8"))

    def process_queue(self):
        if not self.running:
            return
        if self.numsent < self.maxsent:
            for x in range(len(self.queue)-1,-1,-1):
                if self.numsent >= self.maxsent:
                    break
                try:
                    if self.queue[x].sent == False:
                        self.send(self.queue[x])
                        self.queue[x].sent = True
                        self.numsent += 1

                    self.redraw_queue()
                    self.screen.redraw()
                except:
                    self.screen.finalize()
                    print("x: %d len(self.queue): %d" % (x, len(self.queue)))
                    raise
        self.redraw_queue()
        self.screen.redraw()

    def enqueue(self, *commands, process_queue=True):
        curses.napms(100)
        for command in commands:
            if command.startswith("G0 G54 G17"):
                #self.screen.finalize()
                #pdb.set_trace()
                pass
            self.queue.append(GCode(command))
        if process_queue:
            self.process_queue()

    def dequeue(self, process_queue=True):
        curses.napms(100)
        self.queue.pop(0)
        self.numsent -= 1
        if process_queue:
            self.process_queue()

    def _handle_error(self, response):
        self.device.write("!\x18\n\n\n\n".encode("utf8"))
        self.screen.finalize()
        print("error: \"%s\"" % (response,))
        pdb.set_trace()
        raise RuntimeError

    def _handle_alarm(self, response):
        self.device.write("!\x18\n\n\n\n".encode("utf8"))
        self.screen.finalize()
        print("alarm: \"%s\"" % (response,))
        if response == "ALARM: Homing fail":
            self.homingfails += 1
            if self.homingfails > 3:
                pass
            sys.exit(2)
            #self.dumpqueue()
            #self.device.write("\x18\n\n$X\n\n".encode("utf8"))
            #self._getline()
            #self._getline()
            #self._getline()
            #self._getline()
            #self._getline()
            #self._getline()

            #self.reset()
            #self.home()
        pdb.set_trace()
        raise RuntimeError

    def _handle_post_reset(self, line=None):
        try:
            if line is None:
                line=True
                while line is True:
                    line = self._getline()
                    if not line.startswith("Grbl"):
                        line = True
            try:
                self.grbl_version = line.split(' ')[1]
            except IndexError:
                self.screen.finalize()
                print("line: \"%s\"" % (line,))
                raise
            line = True
            while line is True:
                line = self._getline()
                if line == "":
                    line = True
            if line.startswith("['$H'"):
                self.device.write("$X".encode("utf8"))
                line = None
            for x in range(0, len(self.queue)):
                self.queue[x].sent = False
            self.enqueue("")
        except:
            self.screen.finalize()
            raise

    def _handle_unlock(self):
        self.device.write("!\x18".encode("utf8"))
        self.device.write("$X".encode("utf8"))
        line = self._getline()
        self._handle_response(line, process_queue=False)

    def _handle_response(self, response, process_queue=True):
        self.screen.drawtime()
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
        self.enqueue("$G")
        found = False
        while True:
            response = self._getline()
            if response is True:
                continue
            if response.startswith("["):
                self.parser_state = set(response[1:-1].split(' '))
                response = self._getline()
                found = True

            self._handle_response(response, process_queue=False)
            if found:
                break

    def parse_status(self, line):
        if line.startswith("<") and line.endswith(">"):
            (status, line) = line[1:-1].split(',', maxsplit=1)

            (tosser, line) = line.split(':', maxsplit=1)
            mpos=[0,0,0]
            (mpos[0],mpos[1],mpos[2],line) = line.split(',', maxsplit=3)
            self.mpos = Position(name="MPos", x=float(mpos[0]),
                    y=float(mpos[1]), z=float(mpos[2]))

            wpos=[0,0,0]
            (tosser, line) = line.split(':', maxsplit=1)
            (wpos[0],wpos[1],wpos[2]) = line.split(',', maxsplit=2)
            self.wpos = Position(name="WPos", x=float(wpos[0]),
                    y=float(wpos[1]), z=float(wpos[2]))

            if self.screen.status_updates:
                self.screen.status(status, self.wpos)
            return status
        return None

    def get_status(self):
        self.device.write("?".encode("utf8"))
        count = 0
        while True:
            response = self._getline()
            if response is True:
                self.device.write("?".encode("utf8"))
                continue

            try:
                return self._handle_response(response, process_queue=False)
            except ValueError:
                if count == 10:
                    raise
                count += 1
                continue
            break
        return None

    def wait_for_idle(self, goal="Idle", timeout=10):
        self.screen.status_updates = False
        start = time.monotonic()
        status = self.get_status()
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
                self.send("~")
                #self.screen.finalize()
                #pdb.set_trace()
                #self.reset()
            elif status == "Home":
                pass
            elif status.startswith("Waiting for "):
                pass
            else:
                self.screen.status_updates = True
                raise ValueError("status is \"%s\"" % (self.status,))
            status = self.get_status()
        self.screen.status_updates = True
        if status == goal:
            self.status = status
            self.screen.status(self.status, self.wpos)

    def get_grbl_params(self):
        self.enqueue("$#")
        found_bracket = False
        while True:
            response = self._getline()
            if response is True:
                continue
            if response.startswith("["):
                found_bracket = True
                response = response[1:-1]
                if response.startswith("TLO:"):
                    self.grbl_params['TLO'] = float(response[4:])
                elif response.startswith("PRB:"):
                    tmp,dunno = response[4:].split(':')
                    xyz = tmp.split(',')
                    pos = Position(name=response[:3], x=float(xyz[0]),
                            y=float(xyz[1]), z=float(xyz[2]))
                    self.grbl_params[response[:3]] = {"Pos":pos,
                                                      "Dunno": dunno}
                else:
                    xyz = response[4:].split(',')
                    pos = Position(name=response[:3], x=float(xyz[0]),
                            y=float(xyz[1]), z=float(xyz[2]))
                    self.grbl_params[response[:3]] = pos
            else:
                self._handle_response(response)
                break

    def setup(self):
        self.status = "Waiting for idle"
        self.screen.status(self.status, "%s" % (self.wpos,))
        self.wait_for_idle()
        self.screen.status(" " * 20, "%s" % (self.wpos,))
        #print(" %s,%s,%s" % (self.status, self.mpos, self.wpos))
        self.get_parser_state()
        #pprint.pprint("%s" % (self.parser_state,))
        self.wait_for_idle()
        self.get_grbl_params()
        #pprint.pprint("%s" % (self.grbl_params,))

        self.home()

    def home(self):
        self.status = "Waiting for idle"
        self.screen.status(self.status, "%s" % (self.wpos,))
        self.quiesce()
        self.enqueue("$H")
        self.status = "Waiting for Homing"
        self.screen.status(self.status, "%s" % (self.wpos,))
        self.wait_for_idle("Home", timeout=90)
        self.enqueue("G55")
        self.enqueue("G43.1 Z20.25")
        self.redraw_queue()
        self.screen.redraw()

    def reset(self):
        self.timeouts = 0
        signal.alarm(0)
        self.device.write("\x18".encode("utf8"))
        self.screen.status("Resetting", self.wpos)
        self.screen.redraw()
        self._handle_post_reset()

    def redraw_queue(self):
        self.screen.addstr(13, 0, "queue: sent: %d total: %d" % (self.numsent,
            len(self.queue)))
        self.screen.addstr(14, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(15, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(16, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(17, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(18, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(19, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(20, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(21, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(22, 0, " " * 79)
        self.screen.redraw()
        self.screen.addstr(23, 0, " " * 79)
        self.screen.redraw()
        ql = len(self.queue)
        rows=[]
        for x in range(0, ql):
            if x > 9:
                break
            s=" "
            if self.queue[x].sent:
                s="*"
            s = "%s%s" % (s, self.queue[x])
            rows.append(s)

        for x in range(0, len(rows)):
            self.screen.addstr(14+x, 0, rows[x])
        self.screen.redraw()

class OldMill(object):
    def command(self, s):
        cmd = "%s\n" % (s,)
        print("%s" % (s,))
        os.write(self.device.fileno(), cmd.encode('utf8'))
        response = self._getline()
        print("%s" % (response,))
        return response

    def center(self):
        self.command("G1 Z30 F1000")
        self.gotoxyz(150, 150, 30, 1000)
        self.status()

    def gotoxyz(self, x=None, y=None, z=None, f=None):
        if f is None:
            f = self.f
        if f is None:
            cmd = "G0"
            feed = None
        else:
            cmd = "G1"
            feed = "F%d" % (f,)

        if x:
            cmd = "%s X%0.6f" % (cmd, x)
        if y:
            cmd = "%s Y%0.6f" % (cmd, y)
        if z:
            cmd = "%s Z%0.6f" % (cmd, z)
        if feed:
            cmd = "%s %s" % (cmd, feed)

        self.command(cmd)

        if x:
            self.mpos._x = x
        if y:
            self.mpos._y = y
        if z:
            self.mpos._z = z

    def gotox(self, x, f=None):
        self.gotoxyz(x=x, f=f)

    def gotoy(self, y, f=None):
        self.gotoxyz(y=y, f=f)

    def gotoxy(self, x, y, f=None):
        self.gotoxyz(x=x, y=y, f=f)

    def gotoz(self, z, f=None):
        self.gotoxyz(z=z, f=f)

    def left(self, amt):
        self.gotox(self.mpos.x-amt)

    def right(self, amt):
        self.left(-amt)

    def back(self, amt):
        self.gotoy(self.mpos.y-amt)

    def forward(self, amt):
        self.back(-amt)

    def down(self, amt):
        self.gotoz(self.mpos.z-amt)

    def up(self, amt):
        self.down(-amt)

    def faster(self, amt):
        self._f += amt

    def slower(self, amt):
        self.faster(-amt)

    def homing_cycle(self):
        self.command("G54")
        self.command("$H")
        self.command("G54")
        self.command("G55")
        self.command(self.g43dot1.string(z=42.34))

    def getpos(self):
        os.write(self.device.fileno(), "?".encode('utf8'))
        line = "ok"
        while line == "ok":
            line = self._getline()

    def calibrate(self):
        self.homing_cycle()
        self.getpos()
        self.status()

    def status(self):
        print("position: (%0.6f, %0.6f, %0.6f) feedrate: %d" %
                (self.wpos.x, self.wpos.y, self.wpos.z, self.f))

class Screen(object):
    def __init__(self):
        curses.setupterm()
        self.scr = curses.initscr()
        curses.savetty()
        #curses.def_shell_mode()
        curses.curs_set(0)
        #curses.start_color()
        curses.noecho()
        curses.cbreak()
        self.scr.scrollok(False)
        curses.def_prog_mode()
        self.scr.refresh()
        self.curses_module = curses
        self.last_time = time.monotonic()
        self.status_updates = True

    def finalize(self):
        try:
            self.curses_module.resetty()
        except:
            pass
        try:
            self.curses_module.noraw()
        except:
            pass
        try:
            self.curses_module.echo()
        except:
            pass
        try:
            self.curses_module.nocbreak()
        except:
            pass
        try:
            self.curses_module.reset_shell_mode()
        except:
            pass
        try:
            self.curses_module.endwin()
        except:
            pass

    def __del__(self):
        self.finalize()

    def drawtime(self):
        newtime = time.monotonic()
        if newtime < self.last_time + 1:
            return
        self.last_time = newtime
        self.scr.addstr(2, 40, " " * 40)
        self.scr.refresh()
        s = time.asctime()
        self.scr.addstr(2, 40 + (40-len(s)), s)
        self.scr.refresh()

    def redraw(self):
        self.drawtime()
        self.scr.refresh()

    def addnstr(self, y, x, s, n):
        try:
            self.scr.addnstr(y, x, s, n)
        except curses.error:
            self.finalize()
            raise

    def addstr(self, y, x, s):
        try:
            self.scr.addstr(y, x, s)
        except curses.error:
            self.finalize()
            raise

    def status(self, msg, wpos=None):
        if self.status_updates == True:
            self.addnstr(0, 60, " " * 20, 20)
            self.redraw()
            l = len(msg)
            pos = 60
            if l < 20:
                pos += 20 - l
            self.addnstr(0, pos, msg, 20)
            self.redraw()
        if wpos:
            scr.addnstr(1, 0, " " * 80, 80)
            self.redraw()
            s = "%s" % (wpos,)
            scr.addstr(1, 80-len(s), s)
            self.redraw()

if __name__ == '__main__':
    l = len(sys.argv)
    if l < 3 or l > 4:
        print("usage: mill <commands> <terminal>")
        sys.exit(1)

    should_reset = False
    for x in range(1, l):
        if sys.argv[x] == '--reset' or sys.argv[x] == '-r':
            should_reset = True

    cmdfile=sys.argv[1]
    terminal=sys.argv[2]

    scr = Screen()
    scr.addstr(0, 0, "mill")
    scr.redraw()

    mill = Mill(terminal, scr)
    cmds = open(cmdfile).readlines()

    scr.status(mill.status, str(mill.wpos))
    scr.drawtime()
    if should_reset:
        mill.reset()

    mill.setup()
    mill.get_status()

    curses.napms(100)
    mill.get_status()
    scr.status(mill.status, mill.wpos)
    scr.drawtime()

    try:
        mill.start()
        for cmd in cmds:
            cmd = cmd.strip()
            if cmd.startswith('#'):
                continue
            mill.enqueue(cmd)
        mill.process_queue()
        mill.mainloop()
        if mill.numsent >= mill.maxsent:
            mill.process_queue()

        #def alrm(signum, frame):
        #    return

        #signal.signal(signal.SIGVTALRM, alrm)
        #signal.setitimer(signal.ITIMER_VIRTUAL, 1, 1)

        while True:
            #mill.quiesce(2)
            if len(mill.queue) == 0 and mill.numsent == 0:
                time.sleep(0.5)
                mill.redraw_queue()
                mill.screen.redraw()
                mill.wait_for_idle()
                break
            mill.mainloop()
            if mill.numsent >= mill.maxsent:
                mill.process_queue()
    except KeyboardInterrupt:
        signal.alarm(0)
        scr.finalize()
        pdb.set_trace()
        pass
    except:
        scr.finalize()
        raise
    scr.finalize()
    print("Queue depth is %d numsent is %d, job is done." % (len(mill.queue),
        mill.numsent))
