import tokenize
from tokenize import tok_name
import collections

RowCol = collections.namedtuple("RowCol", "row col")
NamedToken  = collections.namedtuple("NamedToken", "type string start end line")

Line = collections.namedtuple("Line", "string indent")

def generate_named_tokens(filename):
    """
    Accepts a python script's filename

    Wraps tokenize.generate_tokens to
    return the token, but in namedtuple
    form:
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
    (line, indent)
    for each class or function declaration
    in the script.

    Lines are "logical lines". 
    All whitespaces, including newlines,
    are removed. F.ex:

    def func(a = 222,
            b, d)

    will be yielded as

    (func(a=222,b,d), 0)
    """
    line_started = False
    
    for tok in generate_named_tokens(filename):

        # Flag it if the token's a new class or def declaration
        if not line_started and tok.type == tokenize.NAME:
            if tok.string == "class" or tok.string == "def":
                line_started = True
                line, indent = "", tok.start.col
        
        elif line_started:
        # If a logical newline, we're done with the definition
            if tok.type == tokenize.NEWLINE or tok.type == tokenize.ENDMARKER:
                if len(line) > 0:
                    yield Line(string=line, indent=indent)
                line_started = False

            # Otherwise we're in the middle of a line, so we 
            # need to append the next non-empty token
            elif not tok.string.isspace():
                line += tok.string
