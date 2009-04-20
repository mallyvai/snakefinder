from functools import partial
from pickletools import dis
from pickle import loads, dumps
from collections import namedtuple
from copy_reg import pickle

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

block_types = set(["file", "class", "def"])


# I did *not* write this code; it is courtesy of nabit-hab http://codepad.org/BSYSEJC7/fork
import functools, collections, pickle, pickletools, copy_reg

def Children_FromReduce(obj_type, func, args, kwargs):
    return obj_type(func, *args, **kwargs)

def Children_ToReduce(obj):
    return (Children_FromReduce, (type(obj), obj.func, obj.args, obj.keywords or {}))

"""pickle(partial, to_reduce)

dd = defaultdict(partial(defaultdict, set))
s = dumps(dd)
print s
dis(s)
print loads(s)"""
