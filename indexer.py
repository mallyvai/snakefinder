from collections import defaultdict
import pprint
import os, sys
from os.path import join, abspath as abs
import re
from cPickle import dump
import functools
from query_ds import URL, BlockGraph, Children_ToReduce, Children_FromReduce
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

DBG_FILENAME = None
class Indexer:
    def __init__(self, block_graph=None):
        if block_graph is None:
            block_graph = BlockGraph(defs=set(),
                                    classes=set(),
                                    files=set(),
                                    parents=dict(),
                                    children=defaultdict(functools.partial(defaultdict, set)) )
                                    #children=defaultdict( lambda:defaultdict(set) ))
            # This last one is equal to defaultdict(functools.partial(defaultdict, set)) ()
            # Note the extra brackets at the end. really need to learn more FP...
        self.block_graph = block_graph
        copy_reg.pickle(functools.partial, Children_ToReduce)

    def construct_helper(self, text, i, parent_url, parent_indentation, block_type):
        global DBG_FILENAME
        """Recursively analyzes a file and generates the parent/child graph 
        and flat lists for functions and classes.
        """

        this_url, this_indent = URL(filename, i+1, text[i].strip()), line_indentation(text[i])
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

            if indent == parent_indentation:
                purl, pindent = parent_url, parent_indentation
            elif indent > parent_indentation:
                purl, pindent = this_url, indent
            
            # We now add the URL to its appropriate universal set
            # based on its block type
            block_type = None
            if len(tokens) > 0:
                block_type = tokens[0]
            
            if block_type == "def":
                line = line.replace("def", "", 1).strip()
                url = URL(filename, i+1, line)
                print line
                self.block_graph.defs.add(url)
                i = self.construct_helper(text, i, purl, pindent, block_type)
        
            elif block_type == "class":
                print "before:", line
                line = line.replace("class", "", 1).strip()
                print "after:", line
                print line
                url = URL(filename, i+1, line.strip())

                self.block_graph.classes.add(url)
                i = self.construct_helper(text, i, purl, pindent, block_type)

        return i

    def construct(self, filename):
        """ Sets up the call to construct_helper that generates the graph for this file."""
        global DBG_FILENAME
        DBG_FILENAME = filename
        file_url = URL(filename, -1,filename) 
        fh = open(filename, 'r')
        lines = fh.readlines()
        fh.close()

        #It's possible to have empty .py files (__init__.py) 
        if len(lines) > 0:
            self.construct_helper(lines, -1, file_url, 0, "file")


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

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(index.block_graph.parents)

# Thanks to http://mail.python.org/pipermail/python-list/2000-January/021385.html
# For a wonderful little multi-dimensional dictionary hack that i never actually ended up using.
