from tokenize import tok_name
from data_structures import Line, UniversalParentURL, URL, BlockGraph
from collections import defaultdict, namedtuple

import tokenize
import functools
import os
import optparse
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

class Indexer(object):

    def __init__(self):
        self.graph = BlockGraph( children=defaultdict(
                            functools.partial(defaultdict, set)) )

    def _generate_lines_and_urls(self):
        for line in generate_logical_lines(self.filename):
            url = URL(file=self.filename, lineno=line.row, statement=line.string)
            yield line, url

    def _construct_helper(self, par_line, par_url, cur_line, cur_url):
        self.graph.children[UniversalParentURL][self.next_line.block_type].add(next_url)
        self.graph.children[par_url][cur_line.block_type].add(cur_url)
        
        try:
            self.next_line, self.next_url = self.gen.next()
        except StopIteration:
            return

        while True:
            if self.next_line.col < cur_line.col:
                return
            if self.next_line.col == cur_line.col:
                self._construct_helper(par_line, par_url, self.next_line, self.next_url)
            elif self.next_line.col > cur_line.col:
                self._construct_helper(cur_line, cur_url, self.next_line, self.next_url)

    def construct(self, filename):
        self.filename = filename
        base_filename = os.path.basename(filename)
        file_url = URL(filename, -1, base_filename)
        self.graph.children[UniversalParentURL]["file"].add(file_url)
        gen = generate_lines_and_urls()
        self.next_line, self.next_url = gen.next()

        dummy_line = Line(None, None, None, -1)
        construct_helper(dummy_line, file_url, self.next_line, self.next_url)

def setup_parser():
    parser = optparse.OptionParser()

    parser.add_option("-a", "--update-all",
            action="store_true", dest="force_update", 
            help="Force read and indexing of all files")
    parser.add_option("-c", "--update-changed",
            action="store_false", dest="force_update",
            help="Only read and index files if they've changed from last time (default)")

    parser.add_option("-n", "--no-recurse",
            action="store_false", dest="recurse",
            help="Don't recurse down matched directories")
    parser.add_option("-r", "--recurse",
            action="store_true", dest="recurse",
            help="Recurse down matched directories (default)")

    parser.add_option("-i", "--index-file",
            dest="index_filename",
            help="Write index to FILE (default is index.dat)",
            metavar="FILE")

    parser.set_defaults(
            force_update=False,
            recurse=True,
            index_filename="index.pkl")

    return parser

if __name__ == "__main__":
    """
    Usage:
    ./indexer [Options][DirPattern]
    Flags:
    -f  Force read/indexing of all files.
        (By default, only indexes if file has been
        update since index was last read)
    -n  No recursion (recurses by default)

    DirPattern:
    A python regex for a directory.
    A directory name alone is a valid regex.

    Examples:
    ./indexer -f ~
    ./indexer -n ~/Code/
    """

    parser = setup_parser()
    options, args = parser.parse_args()
    print options
    print args

