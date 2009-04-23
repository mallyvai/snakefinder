"""
An indexer for python source.

Usage: ./indexer.py <directory>

Where directory will be recursively
searched to find all .py files to indexed
in indexfile. The index file is recreated on
every run. This version does not support any form
of incremental indexing.

The index itself is just a
pickled BlockGraph
namedtuple
object.

"""

from collections import defaultdict
from os.path import join, abspath as abs
from cPickle import dump
from data_structures import *
import pprint
import os, sys
import re
import functools
import copy_reg

def line_indentation(line):
    """Get a line's left whitespace count."""
    return len(line) - len(line.lstrip())

def iter_filenames(pathname, filename_matcher):
    """Yield every filename in the path that matches the pattern"""
    for root, directories, filenames in os.walk(pathname):
        for filename in filenames:
            full = abs(join(root, filename))
            if filename_matcher.match(filename):
                yield full

class Indexer:
    """
    A class which incapsulates most indexing functionality
    """
    def __init__(self, block_graph=None):
        if block_graph is None:
            block_graph = BlockGraph(parents=dict(),
                                    children=defaultdict(functools.partial(defaultdict, set)) )
            # This last one is equal to children=defaultdict( lambda:defaultdict(set) ))
            # Note the extra brackets at the end. TODO: Learn more FP.
        
        # Make explicit the fact that the files, defs, and classes members
        # together form the universal set of elements. There is redundancy
        # here, but it adds semantic value to the data structure.
        self.block_graph = block_graph
        copy_reg.pickle(functools.partial, Children_ToReduce)

    def construct_helper(self, text, i, parent_url, parent_indentation, block_type, this_url):
        """Recursively analyzes a file and generates the parent/child graph 
        and flat lists for functions and classes.
        """
        
        this_indent = line_indentation(text[i])
        self.block_graph.parents[this_url] = (parent_url)
        self.block_graph.children[parent_url][block_type].add(this_url)


        while len(text) > i+1:
            i += 1
            line = text[i]
            indent = line_indentation(line)
            
            if indent < parent_indentation:
                return i

            line = text[i]
            tokens = line.split()

            # Are we still in the parent?
            # Or did we go back a level?
            if indent == parent_indentation:
                purl, pindent = parent_url, parent_indentation
            elif indent > parent_indentation:
                purl, pindent = this_url, indent
            
            # We now add the URL to its appropriate universal set
            # based on its block type
            block_type = None
            if len(tokens) > 0:
                block_type = tokens[0]
            
            # Strip out the 'def' statement itself (to save space)
            # and add it.
            if block_type == "def":
                line = line.replace("def", "", 1).strip()
                next_url = URL(filename, i+1, line)

                self.block_graph.children[UniversalParentURL]["class"].add(next_url)
                i = self.construct_helper(text, i, purl, pindent, block_type, next_url)
        
            # Strip out the 'class' itself and add the rest
            # of the line.
            elif block_type == "class":
                line = line.replace("class", "", 1).strip()
                next_url = URL(filename, i+1, line.strip())

                self.block_graph.children[UniversalParentURL]["class"].add(next_url)
                i = self.construct_helper(text, i, purl, pindent, block_type, next_url)

        return i

    def construct(self, filename):
        """ Sets up the call to construct_helper that generates the graph for this file."""
        file_url = URL(filename, -1,filename)
        fh = open(filename, 'r')
        lines = fh.readlines()
        fh.close()

        self.block_graph.children[UniversalParentURL]["file"].add(file_url)
        #It's possible to have empty .py files (__init__.py)
        if len(lines) > 0:
            self.construct_helper(lines, -1, EmptyURL, 0, "file", file_url)

if __name__ == "__main__":
    pathname = sys.argv[1]
    pathname = abs(pathname) 

    regex = re.compile(".+\.py$")

    index = Indexer()
    for filename in iter_filenames(pathname, regex):
        index.construct(filename)

    index_file = "index.pkl"
    fh_output = open(index_file, 'wb')
    dump(index.block_graph, fh_output)
    fh_output.close()

# Thanks to http://mail.python.org/pipermail/python-list/2000-January/021385.html
# For a wonderful little multi-dimensional dictionary hack that i never actually ended up using.
