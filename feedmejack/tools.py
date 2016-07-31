#!/usr/bin/python3

import math

from .utility import *

class Tool(object):
    _strname = "Tool"

    def __init__(self, location, name, width, length, offset, \
            max_feed_rate=math.inf, min_feed_rate=0, notes=None):
        self.location = location
        self.name = name
        self.width = clean(width)
        self.length = clean(length)
        self.max_feed_rate = max_feed_rate
        if max_feed_rate != math.inf:
            self.max_feed_rate = clean(self.max_feed_rate)
        self.min_feed_rate = clean(min_feed_rate)
        self.notes = notes

        self._z = offset
        self._dynamic_z = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s %s>' % (self._strname, self.name, self.location)

    def set_dynamic_offset(self, offset=0):
        self._dynamic_z = offset

    @property
    def z(self):
        return self._z + self._dynamic_z

class EndMill(Tool):
    _strname = "EndMill"

class CuttingMill(Tool):
    _strname = "CuttingMill"

class CompressionMill(Tool):
    _strname = "CompressionMill"

class GearCutter(Tool):
    _strname = "GearCutter"

class Engraver(Tool):
    _strname = "Engraver"

class Dovetail(Tool):
    _strname = "Dovetail"

class BottomCleaning(Tool):
    _strname = "BottomCleaning"

tools = [
        EndMill("case C", "light pink 1mm", 1.0, 9.5, 20, max_feed_rate=100.0),
        EndMill("case B", "black 0.75mm", 0.75, 9.5, 20),
        EndMill("case A", "white 1.2mm", 1.2, 10, 19),
        EndMill("case A", "gray 1.1mm", 1.1, 10, 20),
        EndMill("case A", "green 0.95mm", 0.95, 9.5, 19.3),
        EndMill("case A", "orange 0.85mm", 0.85, 7.5, 19.8),
        EndMill("case A", "pink 0.8mm", 0.8, 9, 19.6),
        EndMill("case A", "yellow 0.75mm", 0.75, 9, 19.8),
        EndMill("case A", "purple 0.65mm", 0.65, 8, 19.7),
        EndMill("case A", "dark purple 0.6mm", 0.6, 7, 19.8),
        EndMill("case A", "dark yellow 0.55mm", 0.55, 6, 19.9),
        EndMill("case A", "light green 0.35mm", 0.35, 4.75, 19.8),
        EndMill("free", "1/4in Onrsud upcut", 6.35, 28, 42),
        CuttingMill("free", "1/8in cutter", 3.175, 14, 22.5),
        CompressionMill("free", "3mm compression bit", 3.0, 14, 10.5,
                        notes="inventables part 30668-01"),
        GearCutter("free", "1/4in ACME Gear Cutter", 5.0, 1.5, 30,
                   notes="Micro-100 Super Carbide SAT-400-16"),
        GearCutter("free", "1/4in Gear Cutter", 4.75, 1.5, 30,
                   notes="Micro-100 Super Carbide IT-180500"),
        Engraver("black case", "1/4 pointy engraving bit", 0.1, 0.1, 30,
                notes="the point is quite a bit longer than 0.1"),
        Dovetail("wood bit selector", "1/2\" dovetail bit", 12.7, 12.7, 27,
                notes="1/4\" at the top"),
        BottomCleaning("free", "3/4 inch bottom cleaning bit", 19.05, 12.7, 25,
                notes="Roman Carbide DC1257"),
        ]

def find_tool(max_width=None, min_length=None, tool_class=None):
    classes = set()
    if tool_class:
        for tool in tools:
            if tool.__class__.__name__.lower() == tool_class.lower():
                classes.add(tool.__class__)
        for tool in tools:
            if issubclass(tool.__class__, tuple(classes)):
                classes.add(tool.__class__)
    else:
        for tool in tools:
            classes.add(tool.__class__)
    classes = tuple(classes)

    for tool in tools:
        if max_width and max_width < tool.width:
            continue
        if min_length and min_length > tool.length:
            continue
        if tool_class and not isinstance(tool, classes):
            continue
        yield tool
    raise StopIteration

def get_tool(settings):
    tool_args = {}
    if settings.tool_width >= 0:
        tool_args['max_width'] = settings.tool_width
    if settings.tool_len >= 0:
        tool_args['min_length'] = settings.tool_len
    if settings.tool_class != None:
        tool_args['tool_class'] = settings.tool_class
    tools = list(find_tool(**tool_args))
    if not tools:
        raise RuntimeError("no tool found for %s" % (tool_args))
    tool = tools[0]
    if settings.tool_offset != 0:
        tool.set_dynamic_offset(settings.tool_offset)
    return tool

__all__ = [ "CompressionMill", "CuttingMill", "Dovetail", "Engraver",
            "GearCutter",
            "find_tool", "get_tool", "Tool", "EndMill"]
