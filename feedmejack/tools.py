#!/usr/bin/python3

class Tool(object):
    def __init__(self, width=0.8, max_feed_rate=100):
        self._width = float(width)
        self._max_feed_rate = int(max_feed_rate)

    @property
    def width(self):
        return self._width

    @property
    def max_feed_rate(self):
        return self._max_feed_rate
