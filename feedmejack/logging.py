#!/usr/bin/python3
#
# Copyright 2016 Red Hat, Inc.  All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#  Peter Jones <pjones@redhat.com>
#
from decorator import decorator
import pdb
import copy
import time
import types
import sys
import traceback
import inspect

class Logger(object):
    """ This is our logger """
    class __Logger(object):
        def __init__(self, callback, dict_callback=None):
            self.callback = callback
            self.dict_callback = None

        def __call__(self, tracepoint, level, fmt, *args):
            if not isinstance(level, int):
                raise TypeError("log level must be an integer")
            try:
                s = (str(fmt) % args).replace("\n", "\\n")
            except TypeError:
                print("fmt: '%r' args: %r" % (fmt, args))
                pdb.set_trace()
                raise
            s = "%s: %s" % (time.time(), s)
            return self.callback(tracepoint, level, s)

        def logDict(self, tracepoint, level, data:dict):
            return self.dict_callback(tracepoint, level, data)

    instance = None

    def __init__(self, callback, dict_callback=None):
        if not Logger.instance:
            Logger.instance = Logger.__Logger(callback, dict_callback)
        else:
            Logger.instance.callback = callback

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __call__(self, *args):
        self.instance(*args)

def nada(*args, **kwargs): pass

log = Logger(callback=nada)

def resolve_trace_attr(func, obj, name, default):
    # this is probably the default tracepoint, but maybe not.
    dundername = "_%s" % (name,)
    if hasattr(func, dundername):
        value = getattr(func, dundername)
    else:
        value = None
    if not value is None:
        return value
    if hasattr(obj, dundername):
        value = getattr(obj, dundername)
    if value is None:
        return default
    return value

def ingress_logger(func, obj, *args, **kwargs):
    """ A simple logger to log entry to an object """

    # XXX FIXME: figure out a good default level
    level = resolve_trace_attr(func, obj, 'trace_level', 1)

    funcname = "%s.%s"  % (func.__module__, func.__qualname__)

    # argstr = ",".join(['"' + str(arg).replace("\n", "\\n") + '"' for arg in args])
    # kwargstr = ','.join(["%s=%s" % (k,v) for k,v in kwargs.items()])
    # argstr = ",".join([argstr, kwargstr])

    log("ingress", level, "%s(%r)", funcname, (args, kwargs))

def egress_logger(func, obj, ret, *args, **kwargs):
    """ A simple logger to log exit from an object """

    # XXX FIXME: figure out a good default level
    level = resolve_trace_attr(func, obj, 'trace_level', 1)

    funcname = "%s.%s"  % (func.__module__, func.__qualname__)

    log("egress", level, "%s() = %r", funcname, ret)

def traceback_logger(func, obj, *args, **kwargs):
    """ A simple logger to log a traceback on entry of an object. """

    # XXX FIXME: figure out a good default level
    level = resolve_trace_attr(func, obj, 'trace_level', 1)
    funcname = "%s.%s"  % (func.__module__, func.__qualname__)
    stack = inspect.stack()[1:]
    stack = filter(lambda x: x[3] != 'event_tracer', stack)
    for line in stack:
        fmt = traceback.format_stack(line[0], limit=1)[0]
        for s in fmt.split('\n'):
            if s.strip():
                log("traceback", level, "%s:%s", func.__qualname__, s)

eventmap = {
    'traceback':{'ingress_logger':traceback_logger,
                 'before':True},
    'ingress':{'ingress_logger':ingress_logger,
               'before':True},
    'egress':{'egress_logger':egress_logger,
              'after':True},
    }

def event_tracer(func, obj, *args, **kwargs):
    trace_events = {}
    if hasattr(obj, '_trace_events'):
        trace_events.update(obj._trace_events)
    if hasattr(func, '_trace_events'):
        trace_events.update(func._trace_events)
    early = {}
    late = {}

    def before(k):
        v = eventmap[k]
        if 'before' in v:
            return v['before']
        if 'after' in v:
            return not v['after']
        return False

    def after(k):
        v = eventmap[k]
        if 'after' in v:
            return v['after']
        if 'before' in v:
            return not v['before']
        return False

    for k,v in trace_events.items():
        if before(k):
            early[k] = v
        if after(k):
            late[k] = v

    for k, v in early.items():
        eventmap[k]['ingress_logger'](func, obj, *args, **kwargs)
    ret = func(obj, *args, **kwargs)
    for k, v in late.items():
        eventmap[k]['egress_logger'](func, obj, ret, *args, **kwargs)
    return ret

def trace_point(name:str):
    """ Decorator to add a tracepoint type to an object."""
    def run_func_with_trace_point_set(func, level=1):
        setattr(func, '_trace_point', name)
        return func
    return run_func_with_trace_point_set

def trace_level(level:int):
    """ Decorator to add a tracelevel type to an object."""
    level = int(level)
    def run_func_with_trace_level_set(func):
        setattr(func, '_trace_level', level)
        return func
    return run_func_with_trace_level_set

def trace_event(name:str, tracepoint="debug", level=1):
    """ Decorator to add a trace event to an object."""
    def run_func_with_event_list(func):
        if hasattr(func, '_trace_events'):
            events = func._trace_events
        else:
            events = {}
        if not name in events:
            events[name] = {'tracepoint':tracepoint,
                            'level':level
                            }
        setattr(func, '_trace_events', events)
        return func
    return run_func_with_event_list

class LogFunction(object):
    """ This class provides a callable to log some data """

    def __init__(self, tracepoint=None):
        self._trace_point = tracepoint

    # XXX this should use our real log formatter instead
    def __call__(self, level, msg, *args):
        # somebody might want to turn some specific kind of thing on, but
        # silence some particular message.  They can do that with "squelch".
        if self._trace_point != "squelch":
            return log(self._trace_point, level, msg, *args)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return LogFunction(tracepoint=name)

class LoggedObjectMeta(type):
    """ This class object provides you with a metaclass you can use in your
    classes to get logging set up with easy defaults
    """
    _default_trace_events = {
        'ingress': {},
        'egress': {},
        }

    def __new__(cls, name, bases, nmspc):
        for k, v in nmspc.items():
            if isinstance(v, types.FunctionType):
                trace_events = copy.copy(cls._default_trace_events)
                if hasattr(v, '_trace_events'):
                    trace_events.update(v._trace_events)
                setattr(v, '_trace_events', trace_events)
                v = decorator(event_tracer, v)
                nmspc[k] = v

        # We use "None" rather than "default" here so that if somebody /sets/
        # something to default, we won't override it with something with lower
        # precedence.
        tracepoint = nmspc.setdefault("_trace_point", None)
        nmspc['log'] = LogFunction(tracepoint)
        return type.__new__(cls, name, bases, nmspc)

class LoggedObject(metaclass=LoggedObjectMeta):
    """ This provides an object which automatically logs some things """

    def __init__(self, *args, **kwargs):
        pass

#log = LogFunction()
#
#@tracepoint("zoom")
#class Foo(metaclass=LoggedObject):
#    def __init__(self):
#        self.log(1, "this should be log level type zoom")
#        print('1')
#
#    @tracepoint("baz")
#    def foo(self):
#        self.log(3, "this should be log type baz")
#        print('2')
#
#    def zonk(self):
#        self.log.debug(3, "this should be log type debug")
#        print('3')
#        return 0
#
#class Bar(metaclass=LoggedObject):
#    def __init__(self):
#        self.log(9, "this should be log type default")
#
#@tracepoint("incorrect")
#class Baz(metaclass=LoggedObject):
#    @tracepoint("default")
#    def __init__(self):
#        self.log(4, "this should be log type default")
#
#    def zonk(self):
#        self.log(5,"this should be log type incorrect")
#
#@tracepoint("maybe")
#def bullshit():
#    log(4, "does this even work?  maybe...")
#
#x = Foo()
#x.foo()
#x.zonk()
#
#y = Bar()
#
#z = Baz()
#z.zonk()

__all__ = [ "LoggedObject", "LogFunction",
            "trace_point", "trace_level", "trace_event",
            "log", 'eventmap']
