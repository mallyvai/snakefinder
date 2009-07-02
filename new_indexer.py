from tokenize import tok_name
from data_structures import Line, UniversalParentURL, URL, BlockGraph
from collections import defaultdict, namedtuple

import helper_functions

import tokenize
import functools
import os
import optparse

class Indexer(object):

    def __init__(self, graph=None):
        if graph is None:
            self.graph = BlockGraph(children=defaultdict(
                                    functools.partial(defaultdict, set)) )
        else:
            self.graph = graph

    def _generate_lines_and_urls(self):
        for line in helper_functions.generate_logical_lines(self.filename):
            url = URL(file=self.filename, lineno=line.row, statement=line.string)
            yield line, url

    def _construct_helper(self, par_line, par_url, cur_line, cur_url):
        self.graph.children[UniversalParentURL][self.next_line.block_type].add(self.next_url)
        self.graph.children[par_url][cur_line.block_type].add(cur_url)
        
        try:
            #Pylint says E: Class _gen_linesurls has no next mem
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
        self.gen = self._generate_lines_and_urls()
        self.next_line, self.next_url = self.gen.next()

        dummy_line = Line(None, None, None, -1)
        self._construct_helper(dummy_line, file_url, self.next_line, self.next_url)

def get_options_and_args():
    parser = optparse.OptionParser()
    usage = "usage: %prog [flags] /dir/1 ... /dir/n"
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
            help="Write index to FILE (default is index.pkl)",
            metavar="FILE")

    parser.set_defaults(
            force_update=False,
            recurse=True,
            index_filename="index.pkl")
    
    options, args = parser.parse_args()
    
    #Now we validate the arguments

    if len(args) < 1:
        parser.error("Needs at least one directory to index!")

    for directory in args:
        if not os.path.isdir(directory):
            parser.error(directory + " is not a valid directory")

    return options, args

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
    The path for a directory.
    
    Examples:
    ./indexer -f ~
    ./indexer -n ~/Code/
    """
    
    filename_matcher = re.compile(".+\.py$")
    options, args = get_options_and_args()

    index = Index()
    if not options.force_update:
        index.graph = load_index(options.index_filename)

    for directory in args:
        for filename in iter_filenames(directory, filename_matcher):
            index.construct(filename)

    print options
    print args

