#!/usr/bin/python3

import math

from .utility import *

class Tool(object):
    _strname = "Tool"

    def __init__(self, location, name, CED, CEL, depth_from_spindle, \
            max_feed_rate=100.0, min_feed_rate=0, overall_length=0,
            shank_diameter=None,
            notes=None):
        self.location = location
        self.name = name
        self.max_feed_rate = max_feed_rate
        if max_feed_rate != math.inf:
            self.max_feed_rate = clean(self.max_feed_rate)
        self.min_feed_rate = clean(min_feed_rate)
        self.notes = notes

        self.depth_from_spindle = quantity(depth_from_spindle)
        self.cutting_diameter = quantity(CED)
        self.overall_length = quantity(overall_length)
        self.flute_length = quantity(CEL)
        if shank_diameter is None:
            self.shank_diameter = quantity(self.cutting_diameter)
        else:
            self.shank_diameter = quantity(shank_diameter)

        self._dynamic_z = 0

    def attr_as_mm(self, name):
        q = getattr(self, name)
        m = q.to("mm").magnitude
        return clean(m, "10000000000.0000")

    @property
    def CED(self):
        return self.attr_as_mm("cutting_diameter")

    @property
    def width(self):
        try:
            return self.attr_as_mm("cutting_diameter")
        except:
            import pdb
            pdb.set_trace()
            pass

    @property
    def diameter(self):
        return self.attr_as_mm("cutting_diameter")

    @property
    def radius(self):
        return self.attr_as_mm("cutting_diameter") / clean("2", "10000.000")

    @property
    def CEL(self):
        return self.attr_as_mm("flute_length")

    @property
    def length(self):
        return self.attr_as_mm("flute_length")

    @property
    def SHK(self):
        return self.attr_as_mm("shank_diameter")

    @property
    def OAL(self):
        return self.attr_as_mm("overall_length")


    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s %s>' % (self._strname, self.name, self.location)

    def set_dynamic_offset(self, offset=0):
        if offset is None:
            raise ValueError
        self._dynamic_z = offset

    @property
    def raw_z(self):
        return self.attr_as_mm("depth_from_spindle")

    @property
    def z(self):
        #print("self._z: %s self._dynamic_z: %s" % (self._z, self._dynamic_z))
        return self.raw_z + self._dynamic_z

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
        EndMill("free", "1/4in Onsrud upcut", CED="0.25 inch", CEL="0.625 inch",
            depth_from_spindle="42mm",
            shank_diameter="0.25 inch", overall_length="2.75 inch",
            max_feed_rate=1000.0, notes="LMT Onsrud 40-105"),
        EndMill("case C", "light pink 1mm", 1.0, 9.5, 20, max_feed_rate=100.0),
        EndMill("case B", "black 0.75mm", 0.75, 9.5, 20),
        EndMill("case A", "white 1.2mm", 1.2, 10, 19),
        EndMill("Inventables PCB Set", "orange 1.1mm", 1.1, 11, 20.5,
                max_feed_rate=150.0, notes="inventables set 30326-01"),
        EndMill("case A", "green 0.95mm", 0.95, 9.5, 19.3, max_feed_rate=100.0),
        EndMill("case A", "orange 0.85mm", 0.85, 7.5, 19.8),
        EndMill("case A", "pink 0.8mm", 0.8, 9, 19.6),
        EndMill("case A", "yellow 0.75mm", 0.75, 9, 19.8),
        EndMill("case A", "purple 0.65mm", 0.65, 8, 19.7),
        EndMill("case A", "dark purple 0.6mm", 0.6, 7, 19.8),
        EndMill("case A", "dark yellow 0.55mm", 0.55, 6, 19.9),
        EndMill("case A", "light green 0.35mm", 0.35, 4.75, 19.8),
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
        BottomCleaning("free", "3/4 inch bottom cleaning bit",
                CED="0.75 inch", CEL="0.5 inch", depth_from_spindle="25.5 mm",
                max_feed_rate=2000.0,
                notes="Roman Carbide DC1257"),
        ]

def find_tool(min_width=None, max_width=math.inf,
              min_length=None, max_length=math.inf,
              tool_class=None):
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
        if tool_class and not isinstance(tool, classes):
            continue
        if not min_width is None and min_width > tool.width:
            print("skipping %s (min width %s > %s)" % (tool,
                                                    min_width, tool.width))
            continue
        if max_width != math.inf and max_width < tool.width:
            print("skipping %s (max width %s < %s)" % (tool,
                                                    max_width, tool.width))
            continue
        if not min_length is None and min_length > tool.length:
            print("skipping %s (min length %s > %s)" % (tool,
                                                    min_length, tool.length))
            continue
        if max_length != math.inf and max_length < tool.length:
            print("skipping %s (max length %s < %s)" % (tool,
                                                    max_length, tool.length))
            continue
        print("yielding %s (length=%s width=%s)" % (tool, tool.width,
            tool.length))
        yield tool
    raise StopIteration

def get_tool(settings):
    tool_args = {}
    if not settings.tool_width_min is None:
        tool_args['min_width'] = settings.tool_width_min
    if settings.tool_width_max < math.inf:
        tool_args['max_width'] = settings.tool_width_max
    if not settings.tool_length_min is None:
        tool_args['min_length'] = settings.tool_length_min
    if settings.tool_length_max < math.inf:
        tool_args['max_length'] = settings.tool_length_max
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
