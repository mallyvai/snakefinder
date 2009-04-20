from cPickle import load

q_blocks = ["class", "def", "file"]

q_contains = "CONTAINS"
q_peers = "OR"
q_regex_name = "NAME"
q_regex_name_val_sep = "="
q_regex_within = ">"
q_regex_peersep = ","

m_component_splitter = re.compile('|'.join(q_regex_within))


start_elts = blocks + regex_name

class MalformedQueryException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def enforce_eq(one, two):
    if one != two:
        raise MalformedQueryException(one+" != "+two)
def enforce_in(elt, items):
    if elt not in items:
        raise MalformedQueryException(elt+" not in "+items)


def get_matching_children(parent_url, matcher, index):
    matching = [i for i in index.children[parent_url] if matcher.match(i)]
    return set(matching)

def get_matching_descendants(parent_url, matcher, index):
    investigated_children = []
    uninvestigated_children = [i for i in index.children[parent_url]]

    while len(uninvestigated_children) > 0:
        child = uninvestigated_children.pop()
        investigated_children.add(child)
        uninvestigated_children.extend([i for i in index.children[child])
    
    #We've found all descendants. Now let's go ahead and see if any of them match up.
    matching = [i for i in investigated_children if matcher.match(i)]
    return set(matching)

_STARTING = -1
def handle_query_part(query_part, index, parent_set):
    graph = index.block_graph
    parts = query_part.split()
    
    start = parts[0]
    raw_pattern = parts[0].split(q_regex_name_val_sep)[1]
    flat_list = graph.classes #Small optimizations

    if start == "class":
        pass #Instead of the standard None - why though? They both seem to have the same effect. Ask... 
    elif start == "def":
        flat_list = graph.defs
        raw_pattern = parts[1].split(q_regex_name_val_sep)[1]
    elif start == "file":
        flat_list = graph.files
        raw_pattern = parts[1].split(q_regex_name_val_sep)[1]
    elif start == regex_name:
        flat_list |= graph.defs | graph.files
    else:
        raise MalformedQueryException
    
    matcher = re.compile(raw_pattern)
        
    matching = set([i for i in for url in flat_list if matcher.match(i)])
    return matching

get_matching_descendatns

def real_query_handler(query_part, index, parent_sets, matcher)
    result_set = index.universal_set
    
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

def handle_query(query):
    """
    Sample queries: class=asdfj > def=234*
    class = asdf , class = johnnyClass , def=funcName
    We split on the spaces and note that there shouldn't ever be spaces in the regex.
    """

    result_set = set(_STARTING)
    query_chunks = query.split(q_regex_within) #">"
    for query_chunk in query_chunks: #class=3242*[afd] is a chunk. class=324 
        peers = query_chunk.split(q_regex_peersep)
        matching_set = ()
        for peer in peers:
            matching_set |= handle_query_part(query_part, index, result_set)
        result_set |= matching_set
    
    return result_set


if __name__ == "__main__":
    fh_input = open(index_file, 'wb')
    index = load(fh_input)
    fh_input.close()

