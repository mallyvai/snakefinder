import query_ds
from query_ds import URL, URLandType, MalformedQueryException, InvalidBlockTypeException, block_types, Children_ToReduce, Children_FromReduce
import re
import pickle
from indexer import Indexer
import itertools
sep_parts = "~"
sep_st = "="

class Query:
    def _get_type_and_matcher(self, part):
        """
        Given a "part" of a query of the form
        <block_type>=<regex> or regex
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
                    if matcher.match(child):
                        uat = URLandType(child, partition_type)
                        results += uat
            return results

        else:
            for child in parent_index[block_type]:
                if matcher.match(child):
                    uat = URLandType(child, block_type)
                    results += uat
            return results


    def _get_matching_descendants(self, part, parent_url):
        block_type, matcher = self._get_type_and_matcher(part)
        parent_index = self.index.children[parent_url]
        uninvestigated_children = []

        check = lambda a,b: True #Assume it's "all" initially. It will always be pass.
        if block_type != "all":
            check = lambda uat, t: uat.type == t #Return true if the URLandType has an equal type to the one passed in

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
                results += cur_uat
        return results


    """def _get_type_and_matcher(self, part):
        split = part.split(sep_st)
        if len(split is 1):
            return "all", re.compile(part)
        elif len(split) != 2:
            raise MalformedQueryException(part)
        else:
            if split[0] not in block_types:
                raise MalformedQueryException(part)
            return split[0], re.compile(split[1])"""
    
    def _iter_components(self, query):
        """
        I'm not getting caught in regex hell again.
        Custom parser is fine.
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
        parts = component.split(sep_parts)
        for i in parts:
            if len(i) < 0:
                raise MalformedQueryException(component)
            yield i


    def __init__(self, index):
        self.index = index
        self.universal_parent = itertools.chain(index.files, index.defs, index.classes)

    def _unify_sets(self):
        """
        A cheap way to fake a universal set of all URLs.
        """
       # for i in itertools.chain(

    def handle_query(self, query):
        result_set = set()
        first = True
        for depth, component in self._iter_components(query):
            if first:
                first = False
                for part in self._iter_parts(component):
                    result_set += self._get_matching_descendants(part, self.universal_parent)
            else:
                for part in self._iter_parts(component):
                    next_result_set = set()
                    if depth is ">>":
                        for url in result_set:
                            next_result_set += self._get_matching_descendants(url, part)
                    elif depth is ">":
                        for url in result_set:
                            next_result_set += self._get_matching_children(url, part)
                    result_set = next_result_set
        
        return result_set   

if __name__ == "__main__":
    index_file = "index.pkl"
    fh_input = open(index_file, 'r') 
    index = pickle.load(fh_input)
    q = Query(index)
    #q.test_iter_components()

