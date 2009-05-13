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
are the set of all elements.

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

Line = namedtuple("Line", "block_type string row col")
URL = namedtuple("URL", "file lineno statement")
URLandType = namedtuple("URLandType", "url type")
#BlockGraph = namedtuple("BlockGraph", "parents children")
BlockGraph = namedtuple("BlockGraph", "children")

block_types = set(["file", "class", "def"])

EmptyURL = URL("", "", "")
UniversalParentURL = "UniversalParentURL"

