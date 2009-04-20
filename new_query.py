from query_exceptions import MalformedQueryException, NoTypeException
sep_parts = ","
sep_st = "="

def get_matching_children(part, index, parent_url):
    type, matcher = get_type_and_matcher(part)
    
    results = set()
    if type is "all": #Manually loop over the union of the blocktype sets. We save memory this way since we don't have to keep pointers of all children.
        for partition in index.children[parent_url]:
            for child in partition:
                if matcher.match(child):
                    results += child
    else:
        for child in index.children[parent_url][type]:
            if matcher.match(child):
                results += child
    return results

def get_matching_ancestors(part, index, parent_url):
    type, matcher = get_type_and_matcher(part)

    if type is "all":
        uninvestigated_children = []
        results = set()
        for partition in index.children[parent_url]:
            for child in partition:
                if matcher.match(child):
                    results += child
                uninvestigated_children.append(child)
        #We have an initial list of uninvestigated children we need to step through
        while len(uninvestigated_children) > 0:
            cur_parent = uninvestigated_children.pop()
            for partition in index.children[parent_url]:
                for child in partition:
                    if matcher.match(child):
                        results += child
                    uninvestigated_children.append(child)

        results = set()
        uninvestigated_children = [ child for partition in index.children[parent_url] for child in partition ]
        while len(uninvestigated_children) > 0:
            cur = uninvestigated_children.pop()
            if matcher.match(cur):
                results += cur
            uninvestigated_children.extend([for partition in index.children[cur] for child in partition])
                    
    


#memoize this thing!
def get_type_and_matcher(part):
    split = part.split(sep_st)
    if len(split is 1):
        return "all", re.compile(part)
    elif len(split) != 2:
        raise MalformedQueryException(part)
    else:
        if split[0] not in block_types:
            raise MalformedQueryException(part)
        return split[0], re.compile(split[1])

def get_parts(component):
    return component.split(sep_parts)
def get_components(query):
    return re.split(query, ">|>>")

def query_handler(query)
    components = get_components(query)
    start_component = components.pop(0)
    start_parts = get_parts(start_component)

    result_set = set()
    for part in parts:
        for url in index.universal_sets:
            result_set += get_matching_descendants(url
        

    result_set = index.universal_sets
    
    
    for component in components:
        descendant_result_set = set()
        if depth is ">>":
            for result in result_set:
                for part in component:
                    descendant_result_set += get_matching_descendants(result, part, index)
        elif depth is ">":
            for result in result_set:
                for part in component:
                    descendant_result_set += get_matching_children(result, part, index)
        result_set = descendant_result_set
    return result_set   

