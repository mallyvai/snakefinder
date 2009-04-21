from query_ds import URL, URLandType, MalformedQueryException, InvalidBlockTypeException, block_types
import re
import itertools
sep_parts = ","
sep_st = "="

class Query:
    def _get_matching_children(self, part, parent_url):
        block_type, matcher = get_type_and_matcher(part)
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
                if matchter.match(child):
                    uat = URLandType(child, block_type)
                    results += uat
            return results


    def _get_matching_ancestors(self, part, parent_url):
        block_type, matcher = get_type_and_matcher(part)
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


    #memoize this thing!
    def _get_type_and_matcher(self, part):
        split = part.split(sep_st)
        if len(split is 1):
            return "all", re.compile(part)
        elif len(split) != 2:
            raise MalformedQueryException(part)
        else:
            if split[0] not in block_types:
                raise MalformedQueryException(part)
            return split[0], re.compile(split[1])
    
    def _iter_components(self, query):
        re.findall("\s+>\s+.+|\s+>>\s+.+", query)

    def __init__(self, index):
        self.index = index
        self.universal_set = itertools.chain(index.files, index.defs, index.classes)
        self.universal_parent = 

    def _unify_sets(self):
        """
        A cheap way to fake a universal set of all URLs.
        """
        for i in itertools.chain(
    

    def handle_query(self, query):
        result_set = set()
        first = True
        for depth, component in self._iter_components(query):
            if first:
                first = False
                for part in self._iter_parts(component):
                    result_set += _get_matching_descendants(part, self.universal_parent)
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

query = ". >> ."

