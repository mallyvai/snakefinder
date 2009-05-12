from tokenize import tok_name
from data_structures import Line, UniversalParentURL, URL, BlockGraph
from collections import defaultdict, namedtuple

import tokenize
import functools
import os


RowCol = namedtuple("RowCol", "row col")
NamedToken  = namedtuple("NamedToken", "type string start end line")


def generate_named_tokens(filename):
    """
    Accepts a python script's filename

    Wraps tokenize.generate_tokens to return the token, but in namedtuple form:
    (type, string, start, end, line).

    where start and end each are
    (row, col)
    """
    fh = open(filename)
    for t in tokenize.generate_tokens(fh.readline):
        next_token = NamedToken(type = t[0],
                            string = t[1],
                            start = RowCol._make(t[2]),
                            end = RowCol._make(t[3]),
                            line = t[4])
        yield next_token
    fh.close()

def generate_logical_lines(filename):
    """
    Accepts a python script's filename
    
    Yields the tuple
    (block_type, line, row, col)
    for each class or function declaration in the script.

    Lines are "logical lines". All whitespaces, including newlines, are removed.
    F.ex:

    def func(a = 222,
            b, d)

    will be yielded as

    ('def', 'func(a=222,b,d)', 0, 0)
    """
    line_started = False
    
    for tok in generate_named_tokens(filename):

        # Flag it if the token's a new class or def declaration
        if not line_started and tok.type == tokenize.NAME:
            if tok.string == "class" or tok.string == "def":
                line_started = True
                block_type = tok.string
                line, row, col = "", tok.start.row, tok.start.col
        
        elif line_started:
        # If a logical newline, we're done with the definition
            if tok.type == tokenize.NEWLINE or tok.type == tokenize.ENDMARKER:
                if len(line) > 0:
                    yield Line(block_type=block_type, string=line, row=row, col=col)
                line_started = False

            # Otherwise we're in the middle of a line, so we 
            # need to append the next non-empty token
            elif not tok.string.isspace():
                line += tok.string

def generate_lines_and_urls(filename):
    for line in generate_logical_lines(filename):
        url = URL(file=filename, lineno=line.row, statement=line.string)
        yield line, url

next_line, next_url = None, None
def construct_helper(filename, gen, index, par_line, par_url, cur_line, cur_url):
    global next_line, next_url
    index.children[UniversalParentURL][next_line.block_type].add(next_url)
    index.children[par_url][cur_line.block_type].add(cur_url)
    next_line, next_url = gen.next()
    while True:
        if next_line.col < cur_line.col:
            return
        if next_line.col == cur_line.col:
            construct_helper(filename, gen, index, par_line, par_url, next_line, next_url)
        elif next_line.col > cur_line.col:
            construct_helper(filename, gen, index, cur_line, cur_url, next_line, next_url)

def construct(filename):
    global next_line, next_url
    index = BlockGraph( children=defaultdict(
                        functools.partial(defaultdict, set)) )
    
    base_filename = os.path.basename(filename)
    file_url = URL(filename, -1, base_filename)
    index.children[UniversalParentURL]["file"].add(file_url)
    gen = generate_lines_and_urls(filename)
    next_line, next_url = gen.next()

    dline = Line(None, None, None, -1)
    try:
        construct_helper(filename, gen, index, dline, file_url, next_line, next_url)
    except StopIteration:
        pass
    finally:
        for a,b in index.children.iteritems():
            print a,"||||",b

construct("small_class.py")


