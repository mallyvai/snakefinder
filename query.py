from cPickle import load

blocks = ["class", "def", "file"]

contains = "CONTAINS"
peers = "OR"
regex_name = "NAME"

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


def get_matching_children(parent_url, matcher):
    matching = [i for i in index.children[parent_url] if matcher.match(i)]
    return matching

def get_matching_ancestors(parent_url, matcher):
    investigated_children = []
    uninvestigated_children = [i for i in index.children[parent_url]]

    while len(uninvestigated_children) > 0:
        child = uninvestigated_children.pop()
        investigated_children.add(child)
        uninvestigated_children.extend([i for i in index.children[child])
    
    #We've found all ancestors. Now let's go ahead and see if any of them match up.
    matching = [i for i in investigated_children if matcher.match(i)]
    return matching

def handle_query(query, index):
    graph = index.block_graph
    parts = component.split()
    start = parts[0]
    pattern = parts[1]

    flat_list = graph.classes #Small optimization
    if start == "class":
        pass #Instead of the standard None - why though? They both seem to have the same effect. Ask... 
    elif start == "def":
        flat_list = graph.defs
    elif start == "file":
        flat_list = graph.files
    elif start == regex_name:
        flat_list |= graph.defs | graph.files
    else:
        raise MalformedQueryException

if __name__ == "__main__":
    fh_input = open(index_file, 'wb')
    index = load(fh_input)
    fh_input.close()


