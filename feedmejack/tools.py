#!/usr/bin/python3

from decimal import Decimal as _Decimal

class Tool(object):
    _strname = "Tool"

    def __init__(self, location, name, width, length, offset, \
            max_feed_rate=100):
        self._location = location
        self._name = name
        self._width = _Decimal(width)
        self._length = _Decimal(length)
        self._max_feed_rate = int(max_feed_rate)
        self.feed_rate_limit = None
        self._z = offset

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s %s>' % (self._strname, self.name, self.location)

    @property
    def location(self):
        return self._location

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    @property
    def length(self):
        return self._length

    @property
    def max_feed_rate(self):
        if self.feed_rate_limit:
            return min(self.feed_rate_limit, self._max_feed_rate)
        return self._max_feed_rate

    @property
    def z(self):
        return self._z

class EndMill(Tool):
    _strname = "EndMill"

class CuttingMill(Tool):
    _strname = "CuttingMill"

tools = [
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
        EndMill("free", "1/4in Onrsud", 6.35, 28, 42),
        CuttingMill("free", "1/8in cutter", 3.175, 14, 22.5),
        ]

def find_tool(max_width=None, min_length=None, tool_class=None):
    for tool in tools:
        if max_width and max_width < tool.width:
            continue
        if min_length and min_length > tool.length:
            continue
        if tool_class and not isintance(tool, tool_class):
            continue
        yield tool
    raise StopIteration

__all__ = ["Tool", "EndMill", "find_tool"]
