import functools, collections, pickle, pickletools, copy_reg

Line = namedtuple("Line", "block_type string row col")
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

# I did *not* write this code; it is courtesy of nabit-hab http://codepad.org/BSYSEJC7/fork
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

