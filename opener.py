from collections import namedtuple, defaultdict
import pprint
import sys

defs = set()
classes = set()
parents = {}

URL = namedtuple("URL", "file lineno statement")

def line_indentation(line):
    return len(line) - len(line.lstrip())

def construct(text, i, parent_url, parent_indentation):
    this_url, this_indent = URL(filename, i+1, text[i].strip()), line_indentation(text[i])
    parents[this_url] = parent_url

    while len(text) > i+1:
        i += 1
        line = text[i]
        indent = line_indentation(line)
        
        if indent < parent_indentation: #<=?
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
            i = construct(text, i, purl, pindent)
    
        elif len(first) > 0 and first[0] == "class":
            classes.add(url)
            i = construct(text, i, purl, pindent)

    return i

filename = "opener.py"

if len(sys.argv) > 1:
    filename = sys.argv[1]

text = open(filename).readlines()

construct(text, -1, filename, 0)

pp = pprint.PrettyPrinter(indent=4)
print "=========================="
print "defs:"
pp.pprint(defs)
print "------------"
print "classes:"
pp.pprint(classes)
print "------------"
print "parents:"
pp.pprint(parents)


