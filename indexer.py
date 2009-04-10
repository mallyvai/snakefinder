
from collections import namedtuple, defaultdict
import pprint
import os, sys
from os.path import join, abspath as abs
import re
import cPickle

URL = namedtuple("URL", "file lineno statement")
BlockGraph = namedtuple("BlockGraph", "defs classes files parents children")

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
    def __init__(self, block_graph=None):
        if block_graph is None:
            block_graph = BlockGraph(defs=set(),
                                    classes=set(),
                                    files=set(),
                                    parents=dict(),
                                    children=defaultdict(set))

        self.block_graph = block_graph

    def construct_helper(self, text, i, parent_url, parent_indentation):
        """Recursively analyzes a file and generates the parent/child graph 
        and flat lists for functions and classes.
        """
        this_url, this_indent = URL(filename, i+1, text[i].strip()), line_indentation(text[i])
        self.block_graph.parents[this_url] = (parent_url)
        self.block_graph.children[parent_url].add(this_url)

        while len(text) > i+1:
            i += 1
            line = text[i]
            indent = line_indentation(line)
            
            if indent < parent_indentation:
                return i

            line = text[i]
            url = URL(filename, i+1, line.strip()) 
            first = line.split()
            
            if indent == parent_indentation:
                purl, pindent = parent_url, parent_indentation
            elif indent > parent_indentation:
                purl, pindent = this_url, indent
            
            if len(first) > 0 and first[0] == "def":
                self.block_graph.defs.add(url)
                i = self.construct_helper(text, i, purl, pindent)
        
            elif len(first) > 0 and first[0] == "class":
                self.block_graph.classes.add(url)
                i = self.construct_helper(text, i, purl, pindent)

        return i

    def construct(filename):
        """ Sets up the call to construct_helper that generates the graph for this file."""
        file_url = URL(filename, -1, filename)
        fh = open(filename, 'r')
        lines = fh.readlines()
        fh.close()

        self.construct_helper(lines, -1, file_url, 0)


if __name__ == "__main__":
    pathname = sys.argv[1]

    pathname = abs(pathname) 

    regex = re.compile(".+\.py")

    index = Indexer()
    for filename in iter_filenames(pathname, regex):
        index.construct(filename)

    index_file = "index.pkl"
    output = open(index_file, 'wb')
    pickle.dump(index, output)

