#!/usr/bin/python3

import sys
import math

from decimal import Decimal

from .utility import clean
from . import utility
from .tools import get_tool
from .exceptions import *

class Settings():
    def __init__(self, d=None, max_feed_rate=math.inf):
        self.__dict__ = d
        self._max_feed_rate = max_feed_rate

    @property
    def feed(self):
        candidates = [self.mill.f, self._max_feed_rate]
        if 'tool' in self.__dict__:
            candidates.append(self.tool.max_feed_rate)
        if 'feed' in self.__dict__:
            candidates.append(self.__dict__['feed'])
        candidates = filter(lambda x: x not in [None, 0, math.inf], candidates)
        if not candidates:
            raise InvalidFeedRate

        return min(candidates)

def default_tool_settings(width=50.0, length=2.0, cls=None, offset=0.0,
                          feed=None):
    return {'tool_width': width,
            'tool_len': length,
            'tool_class': cls,
            'tool_offset': offset,
            'feed': feed,
            }

def parse_tool_settings(settings=None, argv=sys.argv):
    if not settings:
        settings = Settings()

    removes=[]
    args = {}
    n = 0
    end = len(argv)
    for m in range(1, len(argv)):
        i = n + m
        if i >= end:
            break
        x = argv[i]
        if x in ["--tool"]:
            args['tool_width'] = clean(argv[i+1])
            args['tool_len'] = clean(argv[i+2])
            removes += [i, i+1, i+2]
            n += 2
        elif x in ["--tool-class", "--toolclass", "--class"]:
            args['tool_class'] = argv[i+1]
            removes += [i, i+1]
            n += 1
        elif x in ["--tool-offset", "--tooloffset"]:
            args['tool_offset'] = clean(argv[i+1])
            removes += [i, i+1]
            n += 1
        elif x in ["--feed", "-f", "--feedrate", "--feed-rate"]:
            args['feed'] = clean(argv[i+1])
            removes += [i, i+1]
            n += 1

    removes.reverse()
    for remove in removes:
        del argv[remove]

    settings.__dict__.update(args)
    settings.tool = get_tool(settings)
    return settings

def default_position_settings(label=None, x=None, y=None, z=None):
    args = {}
    if label:
        if not x is None:
            args['%s_x' % (label,)] = x
        if not y is None:
            args['%s_y' % (label,)] = y
        if not z is None:
            args['%s_y' % (label,)] = y
    else:
        if not x is None:
            args['%s'] = x
        if not y is None:
            args['%s'] = y
        if not z is None:
            args['%s'] = y
    return args

def parse_position_settings(label=None, optional=False, settings=None,
                            argv=sys.argv):
    if not settings:
        settings = Settings()

    removes=[]

    args = {}
    if label:
        settings.__dict__['%s_position_present' % (label,)] = False
        n = 0
        end = len(argv)
        for m in range(1, len(argv)):
            i = m + n
            if i >= end:
                break
            x = argv[i]
            if x in ["--%s" % (label,)]:
                try:
                    args['%s_x' % (label,)] = clean(argv[i+1])
                    args['%s_y' % (label,)] = clean(argv[i+2])
                    args['%s_z' % (label,)] = clean(argv[i+3])
                    removes += [i, i+1, i+2, i+3]
                    n += 3
                    settings.__dict__['%s_position_present' % (label,)] = True
                except IndexError:
                    if not optional:
                        raise
    else:
        try:
            settings.__dict__['position_present'] = True
            args.update({'x': clean(argv[1]),
                         'y': clean(argv[2]),
                         'z': clean(argv[3]),
                    })
            removes += [1, 2, 3]
        except IndexError:
            if optional:
                settings.__dict__['position_present'] = False
            else:
                raise

    removes.reverse()
    for remove in removes:
        del argv[remove]

    settings.__dict__.update(args)
    return settings

def default_comms_settings(reporter_tty='/dev/serial/by-name/wyse',
                           reporter_tty_speed = 115200,
                           mill_tty='/dev/serial/by-name/cnc-mill',
                           mill_tty_speed = 115200):
    return {'reporter_tty': reporter_tty,
            'reporter_tty_speed': reporter_tty_speed,
            'mill_tty': mill_tty,
            'mill_tty_speed': mill_tty_speed,
            }

def parse_comms_settings(settings=None, argv=sys.argv):
    if not settings:
        settings = Settings()

    removes=[]
    args = {}
    n = 0
    end = len(argv)
    for m in range(1, len(argv)):
        i = m + n
        if i >= end:
            break
        x = argv[i]
        if x in ["--reporter_tty", "--reporter", "--reporter-tty"]:
            args['reporter_tty'] = argv[i+1]
            removes += [i, i+1]
            n += 1
        if x in ["--reporter-tty-speed"]:
            args['reporter_tty_speed'] = int(argv[i+1])
            removes += [i, i+1]
            n+= 1
        if x in ["--mill-tty-speed"]:
            args['mill_tty_speed'] = int(argv[i+1])
            removes += [i, i+1]
            n+= 1
        if x in ["--mill_tty", "--mill", "--mill-tty"]:
            args['mill_tty'] = argv[i+1]
            removes += [i, i+1]
            n += 1

    removes.reverse()
    for remove in removes:
        del argv[remove]

    settings.__dict__.update(args)
    return settings

def parse_settings(defaults={}, settings=None, argv=sys.argv):
    if not settings:
        settings = Settings()

    removes=[]
    args = {}

    numbers = tuple([x.__class__ for x in [1, 1.1, Decimal('1')]])

    for name in defaults.keys():
        truename = "--%s" % (name.lower(),)
        falsename = "--no-%s" % (name.lower(),)
        if isinstance(defaults[name], True.__class__):
            if truename in argv:
                args[name] = True
                argv.remove(truename)
            elif falsename in argv:
                args[name] = False
                argv.remove(falsename)
            else:
                args[name] = defaults[name]
        elif isinstance(defaults[name], numbers):
            try:
                index = argv.index(truename)
                args[name] = clean(argv[index+1])
                del argv[index+1]
                del argv[index]
            except ValueError:
                args[name] = clean(defaults[name])
        elif isinstance(defaults[name], "".__class):
            try:
                index = argv.index(truename)
                args[name] = str(argv[index+1])
                del argv[index+1]
                del argv[index]
            except ValueError:
                args[name] = defaults[name]
        else:
            try:
                index = argv.index(truename)
                args[name] = argv[index+1]
                del argv[index+1]
                del argv[index]
            except ValueError:
                args[name] = defaults[name]

    removes.reverse()
    for remove in removes:
        del argv[remove]

    settings.__dict__.update(args)
    return settings

def finalize(settings):
    settings.reporter = utility.Reporter(settings)
    if not hasattr(settings, 'home'):
        settings.home = False
    if not hasattr(settings, 'park'):
        settings.home = False
    global global_settings
    global_settings = settings
    return settings

__all__ = ['default_tool_settings', 'parse_tool_settings',
           'default_position_settings', 'parse_position_settings',
           'default_comms_settings', 'parse_comms_settings',
           'Settings',
           ]
