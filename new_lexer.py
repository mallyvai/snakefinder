import tokenize
from tokenize import tok_name
import collections

RowCol = collections.namedtuple("RowCol", "row col")
NamedToken  = collections.namedtuple("NamedToken", "type string start end line")

def generate_named_tokens(filename):
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
    line = "" 
    line_started = False
    for tok in generate_named_tokens(filename):
        #print tok.type, tok.string
        if not line_started and tok.type == tokenize.NAME and tok.string == "class":
            line_started = True
            line = ""
        elif not line_started and tok.type == tokenize.NAME and tok.string == "def":
            line_started = True
            line = ""

        #If a logical newline; we're done with the definition
        elif line_started and tok.type == tokenize.NEWLINE or tok.type == tokenize.ENDMARKER and len(line) > 0:
            line_started = False
            yield line
            line = ""

        # Otherwise we're in the middle of a line, so we 
        # need to append the token
        elif line_started and not tok.string.isspace():
            line += tok.string
i = 0
for line in generate_logical_lines("small_class.py"):
    i+=1
    print i, "logical line", line
