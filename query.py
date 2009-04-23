"""
Query mechanism to complement indexer.py's indexing mechanism.
Usage:

./query.py
with no arguments for interactive query mode

./query.py some_query >> here > for stuff
provide query at run time
"""

from data_structures import *
from indexer import Indexer
import sys
import re
import pickle
import itertools
import pprint

sep_parts = "~"
sep_st = "="

class Query:
    def _get_type_and_matcher(self, part):
        """
        Given a "part" of a query of the form
        <block_type>=<regex> | <regex>
        return a regex matcher and the desired
        block type.

        If the block type is invalid, then
        the whole part gets treated as a regex.
        If the block type is valid, then a 
        non-empty regex must be provided.
        """
        block_type, regex = "", ""
        done_with_block_type = False
        split = ""
        for c in part:
            if done_with_block_type:
                regex += c
            elif not done_with_block_type and c == sep_st:
                done_with_block_type = True
                split = c
            elif not done_with_block_type and c != sep_st:
                block_type += c

        if len(block_type) is 0:
           raise MalformedQueryException(part)
        
        # If the block type is non-existent, treat the 
        # whole part as a regex
        if block_type not in block_types:
            return "all", re.compile(block_type+split+regex)
        
        #Valid block type; ensure the regex exists
        if len(regex) > 0:
            return block_type, re.compile(regex)
        raise MalformedQueryException(part)
   
    def _get_matching_children(self, part, parent_url):
        """
        Given a part and some URL, finds all immediate
        children of that URL that match the part's regex.
        """
        block_type, matcher = self._get_type_and_matcher(part)
        parent_index = self.index.children[parent_url]
        results = set()

        check = lambda a, b: True
        if block_type != "all":
            check = lambda uat, t: uat.type == t

        results = set()  
        
        if block_type == "all":
            for partition_type, children in parent_index.iteritems():
                for child in children:
                    if matcher.match(child.statement):
                        uat = URLandType(child, partition_type)
                        yield uat

        else:
            for child in parent_index[block_type]:
                if matcher.match(child.statement):
                    uat = URLandType(child, block_type)
                    yield uat

    def _get_matching_descendants(self, part, parent_url):
        """
        Given a part and some URL, finds all descendants
        of that url that match the part's regex.
        """
        block_type, matcher = self._get_type_and_matcher(part)
        
        if parent_url not in self.index.children:
            return set()

        parent_index = self.index.children[parent_url]
        uninvestigated_children = []

        # We use this as a kind of switch; if we are scanning everything,
        # always return true. Otherwise return true only if the block type
        # matches the block type we are looking for.
        check = lambda a,b: True 
        if block_type != "all":
            check = lambda uat, bt: uat.type == bt 

        results = set()
        while True:
            next_batch = []
            for partition_type, children in parent_index.iteritems():
                for child in children:
                    uat = URLandType(child, partition_type)
                    next_batch.append(uat)
            uninvestigated_children.extend(next_batch)
            if len(uninvestigated_children) is 0: #Leave; no more stuff to look at.
                break
            #Get the next one in line and its dictionary.
            cur_uat = uninvestigated_children.pop()
            parent_index = self.index.children[cur_uat.url]
            #If it's the type we're looking for, and the regex matches the source snippet, it works.
            if check(cur_uat, block_type) and matcher.match(cur_uat.url.statement):
                results.add(cur_uat)
        return results
   
    def _iter_components(self, query):
        """
        A straightforward custom parser
        for yielding all of the
        components in a plaintext query
        """

        depth = None
        depth_done = True
        component = ""

        for c in query:
            if c == ">" and not depth_done:
                depth += c
            elif c != ">" and not depth_done:
                component += c
                depth_done = True
            elif c != ">" and depth_done:
                component += c
            elif depth_done and c == ">":
                #We finished this component.
                component = component.strip()
                if len(component) is 0:
                    raise MalformedQueryException(component)
                elif depth is not None and len(depth) > 2:
                    raise MalformedQueryException(component)
                
                yield depth, component
                component = ""
                depth = ""
                depth += c
                depth_done = False

        component = component.strip()
        yield depth, component

    def test_iter_components(self):
        """
        A basic test for verifying the correctness
        of the parser that generated components.
        """
        good_queries = {}
        #Query => correct set of components
        good_queries["abdsa=329 > 3929, arg=129 >> 939"] = (
                (None, "abdsa=329"),
                (">",  "3929, arg=129"),
                (">>", "939"))
        good_queries["abcsd"] = (
                ( None,"abcsd"),)
        good_queries["a=b, >> ad3, 292 >> 2=13"] = (
                (None, "a=b,"),
                (">>", "ad3, 292"),
                (">>", "2=13"))

        for query, correct_split in good_queries.iteritems():
            i = self._iter_components(query)
            for actual, good in  itertools.izip_longest(i, correct_split, fillvalue=None):
                if actual != good:
                    print "FAIL GOODQUERY", actual, good

        bad_queries = ("a >> b >> >"), ("11>>> >")
        for bad_query in bad_queries:
            try:
                for i in self._iter_components(bad_query):
                    pass
                print "FAIL BADQUERY:", bad_query
            except MalformedQueryException: 
                pass

    def _iter_parts(self, component):
        """
        Given a component, yields all parts
        within it.
        """
        parts = component.split(sep_parts)
        for i in parts:
            if len(i) < 0:
                raise MalformedQueryException(component)
            yield i


    def __init__(self, index):
        """
        Accepts a BlockGraph index to run queries against.
        Constructs the universal parent in it.
        """
        self.index = index
#        self.index.children[UniversalParentURL]["files"] = index.files
#        self.index.children[UniversalParentURL]["defs"] = index.defs
#        self.index.children[UniversalParentURL]["classes"] = index.classes

    def handle_query(self, query):
        """
        Given a plain query, returns the resulting set of
        URLs match it. Recursive, but the recursion limit
        shouldn't be a problem here.
        """
        result_set = set()
        first = True
        for depth, component in self._iter_components(query):
            if first:
                first = False
                for part in self._iter_parts(component):
                    result_set |= self._get_matching_descendants(part, UniversalParentURL)
            else:
                for part in self._iter_parts(component):
                    next_result_set = set()
                    if depth is ">>":
                        for url in result_set:
                            next_result_set |= self._get_matching_descendants(url, part)
                    elif depth is ">":
                        for url in result_set:
                            next_result_set |= self._get_matching_children(url, part)
                    result_set = next_result_set
        
        return result_set

def load_and_run(query):
    """
    Load the index file and loop for query input.
    """
    index_file = "index.pkl"
    fh_input = open(index_file, 'r') 
    index = pickle.load(fh_input)
    q = Query(index)

    def print_query_response(next_query):
        responses = q.handle_query(next_query)
        for uat in responses:
            print uat.type, uat.url.file+":", uat.url.statement
        return len(responses)

    if query is not None:
        print_query_response(query)
        return

    while True:
        query = raw_input(">> ")
        print_query_response(query)

if __name__ == "__main__":
    print sys.argv
    if len(sys.argv) == 1:
        load_and_run(None)
    else:
        print "else"
        query = ' '.join(sys.argv[1:])
        load_and_run(query)
    
