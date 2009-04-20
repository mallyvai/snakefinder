from query_exceptions import MalformedQueryException, NoTypeException
from query_ds import URL, URLandType
sep_parts = ","
sep_st = "="

def get_matching_children(part, index, parent_url):
    type, matcher = get_type_and_matcher(part)
    parent_index = index.children[parent_url]
    results = set()

    check = lambda a, b: True
    if type != "all":
        check = lambda uat, t: uat.type == t

    results = set()
    while True:
        for partition_type, children in parent

def get_matching_ancestors(part, index, parent_url):
    type, matcher = get_type_and_matcher(part)
    parent_index = index.children[parent_url]
    uninvestigated_children = []

    check = lambda a,b: True #Assume it's "all" initially. It will always be pass.
    if type != "all":
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
        parent_index = index.children[cur_uat.url]
        #If it's the type we're looking for, and the regex matches the source snippet, it works.
        if check(cur_uat, type) and matcher.match(cur_uat.url.statement):
            results += cur_uat
    return results

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

