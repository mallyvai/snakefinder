from collections import namedtuple

class MalformedQueryException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class InvalidBockTypeException(MalformedQueryException):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

URL = namedtuple("URL", "file lineno statement")
URLandType = namedtuple("URLandType", "url type")
BlockGraph = namedtuple("BlockGraph", "defs classes files parents children")

