from collections import namedtuple, defaultdict
import pprint
import os, sys
from os.path import join, abspath as abs
import re

defs = set()
classes = set()
files = set()

parents = {}
child = {}

URL = namedtuple("URL", "file lineno statement")

def line_indentation(line):
    return len(line) - len(line.lstrip())

def construct_helper(text, i, parent_url, parent_indentation):
    this_url, this_indent = URL(filename, i+1, text[i].strip()), line_indentation(text[i])
    parents[this_url] = parent_url

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
        
        if len(first) > 0 and first[0] == "def": #Add to the flatlist
            defs.add(url)
            i = construct_helper(text, i, purl, pindent)
    
        elif len(first) > 0 and first[0] == "class":
            classes.add(url)
            i = construct_helper(text, i, purl, pindent)

    return i

def construct(filename):
    file_url = URL(filename, -1, filename)
    fh = open(filename, 'r')
    construct_helper(fh.readlines(), -1, file_url, 0)
    fh.close()


def iter_filenames(pathname, filename_matcher):
    for root, directories, filenames in os.walk(pathname):
        for filename in filenames:
            full = abs(join(root, filename))
            if filename_matcher.match(filename):
                yield full

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pathname = sys.argv[1]

    pathname = abs(pathname) 

    regex = re.compile(".+\.py")
    for filename in iter_filenames(pathname, regex):
        construct(filename)

