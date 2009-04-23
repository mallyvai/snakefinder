"""
Contains lightweight data structures and constants for the index/query
mechanism.

URL: Represents a URL.

URLandType: A temporary structure that stores a URL and its block type.

BlockGraph: The primary data structure that stores the index itself.
Every URL has an entry in the "children" and "parents" matrices.
Each entry is mapped to a list of that URL's child and parent nodes.
Also contains the universal lists of functions, classes, and files.

EmptyURL: an instance of URL that's intended to be passed as the
parent parameter to a file's URL constructor.

UniversalParentURL: Represents the abstract URL whose children
are the set of all elements. Unused by the index, but created by
the query handler.

MalformedQueryException: Raised by the query handler.
InvalidBlockTypeException: Raised by the query handler.
"""


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

class InvalidBlockTypeException(MalformedQueryException):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

URL = namedtuple("URL", "file lineno statement")
URLandType = namedtuple("URLandType", "url type")
BlockGraph = namedtuple("BlockGraph", "defs classes files parents children")

block_types = set(["file", "class", "def"])

EmptyURL = URL("", "", "")
UniversalParentURL = "UniversalParentURL"

# I did *not* write this code; it is courtesy of nabit-hab http://codepad.org/BSYSEJC7/fork
import functools, collections, pickle, pickletools, copy_reg

def Children_FromReduce(obj_type, func, args, kwargs):
    return obj_type(func, *args, **kwargs)

def Children_ToReduce(obj):
    return (Children_FromReduce, (type(obj), obj.func, obj.args, obj.keywords or {}))

"""
Usage:
pickle(partial, to_reduce)

dd = defaultdict(partial(defaultdict, set))
s = dumps(dd)
print s
dis(s)
print loads(s)
"""
