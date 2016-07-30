#!/usr/bin/python3

class Timeout(Exception):
    pass

class InvalidFeedRate(ValueError):
    pass

class InvalidGCodeTemplate(ValueError):
    def __init__(self, *args):
        ValueError.__init__(self, *args)

    def __str__(self):
        return "InvalidGCodeTemplate %s" % (self.args,)

    def __repr__(self):
        return self.__str__()

class InvalidGCodeValue(ValueError):
    def __init__(self, *args):
        ValueError.__init__(self, *args)

    def __str__(self):
        return "InvalidGCodeValue %s" % (self.args,)

    def __repr__(self):
        return self.__str__()

__all__ = [
           "InvalidFeedRate",
           "InvalidGCodeTemplate",
           "InvalidGCodeValue",
           "Timeout",
           ]

