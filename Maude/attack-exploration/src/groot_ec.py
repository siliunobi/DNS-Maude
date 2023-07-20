import networkx as nx

from zone import Record
from query import Query

SYMBOLIC_LABEL_PREFIX = '_alpha'
MAX_DOMAIN_BYTE_LENGTH = 100 # in reality, this is 255; a lower value produces fewer ECs in case of a DNAME loop

def test():

    TTL = 3600

    # GRoot example
    records = [
        # records at ns2.fnni.net.
        Record('www.bankcard.com.', 'A', TTL, '204.58.233.75'),
        Record('email.bankcard.com.', 'A', TTL, '66.161.21.26'),
        Record('*.bankcard.com.', 'CNAME', TTL, 'www.bankcard.com.'),
        Record('mybankcard.com.', 'NS', TTL, 'ns1.fnni.com.'),
        Record('mybankcard.com.', 'NS', TTL, 'ns2.fnni.net.'),
        Record('mybankcard.com.', 'DNAME', TTL, 'bankcard.com.'),
        
        # DNAME with inexistent target name
        # Record('myinexistentbankcard.com.', 'DNAME', TTL, 'nxdomain.com.'),

        # introduce (bounded) DNAME loop
        # Record('email.bankcard.com.', 'DNAME', TTL, 'mybankcard.com.'),

        # introduce (unbounded) DNAME loop
        # Record('bankcard.com.', 'DNAME', TTL, 'mybankcard.com.'),

        # records at a.gtld-servers.net.
        Record('mybankcard.com.', 'NS', TTL, 'ns1.fnni.com.'),
        Record('mybankcard.com.', 'NS', TTL, 'ns2.fnni.net.'),
        Record('ns1.fnni.com.', 'A', TTL, '216.205.207.204'),
    ]

    label_graph = create_label_graph(records)

    for edge in label_graph.edges:
        print(edge)

    print('=======================')
    types = ['A', 'CNAME']
    queries = get_ec_queries(records, types, 1)
    for query in queries:
        print(query)

def get_ec_queries(records, types, num_symbolic_labels):
    """
    Returns one query for each equivalence class.
    Note that the same name gives rise to multiple ECs, one for each type.
    """

    g = create_label_graph(records)
    qnames = list(set(enumerate_paths(g, num_symbolic_labels)))

    # sort for reproducibility
    qnames.sort()

    queries = []
    for qname in qnames:
        for type in types:
            queries.append(Query(1, qname, type))

    return queries

def create_label_graph(records):
    """
    Creates a label graph from the given list of records.
    The label graph consists of all the owner names appearing in the records (and all prefixes of those names).
    There are two kinds of edges: The normal edges from parent to child (forming a tree), and DNAME edges (from owner name
    to target name).
    Note that the label graph does not contain symbolic (non-existent) labels; these are "added" during path enumeration.
    """

    g = nx.DiGraph()

    # add root
    g.add_node('')
    g.nodes['']['label'] = ''

    # first pass: add nodes and normal edges
    for record in records:
        owner = record.owner
        labels = owner.split('.')
        
        # add nodes for all labels in the owner name and edges between them
        current = ''
        for label in reversed(labels[:-1]):
            g.add_edge(current, f'{label}.{current}', is_dname=False)
            current = f'{label}.{current}'
            g.nodes[current]['label'] = label

    # second pass: add DNAME edges
    for record in records:
        if record.rtype == 'DNAME' and record.rdata in g:
            # target exists elsewhere in the label graph
            g.add_edge(record.owner, record.rdata, is_dname=True)

    return g

def enumerate_paths(g: nx.DiGraph, num_symbolic_labels: int):
    """
    Enumerates paths through the given label graph.
    Conceptually, an additional subtree is added at each node before enumerating paths. This subtree consists of
    num_symbolic_labels non-existent labels, in the form of a path graph.
    """

    paths = ['']
    
    for child in g.successors(''):
        paths += _enumerate_paths_rec(g, child, '', [], num_symbolic_labels)

    # symbolic label directly under root
    paths += [f'{sym}.' for sym in _symbolic_label_paths(num_symbolic_labels)]
    
    return paths

def _enumerate_paths_rec(g: nx.DiGraph, node, path, dname_path_labels, num_symbolic_labels: int):
    """
    Recursive helper function for path enumeration.
    Keeps track of the DNAME path that has been followed to detect (infinite) DNAME loops.
    """

    label = g.nodes[node]['label']

    if dname_path_labels:
        # reached node via DNAME edge

        # check if we're in an infinite loop
        if label in dname_path_labels:
            return []

        new_path = path
        paths = []
    else:
        # reached node via normal edge (not DNAME)

        new_path = f'{label}.{path}'

        # check if max domain length is exceeded
        if domain_byte_length(new_path) > MAX_DOMAIN_BYTE_LENGTH:
            return []

        paths = [new_path]

    # add paths for children (recursively)
    for child in g.successors(node):
        if g.edges[node, child]['is_dname']:
            new_dname_path_labels = dname_path_labels + [label]
        else:
            new_dname_path_labels = []

        child_paths = _enumerate_paths_rec(g, child, new_path, new_dname_path_labels, num_symbolic_labels)
        paths += child_paths

    # add paths for non-existent subdomains
    symbolic_paths = [f'{sym}.{new_path}' for sym in _symbolic_label_paths(num_symbolic_labels)]
    paths += symbolic_paths
    return paths

def _symbolic_label_paths(num_symbolic_labels: int):
    """
    Returns a list of path prefixes consisting of non-existent labels.
    For example, if num_symbolic_labels == 2, this would return ['_alpha1', '_alpha1._alpha2'].
    """

    paths = []
    labels = [f'{SYMBOLIC_LABEL_PREFIX}{i}' for i in range(1, num_symbolic_labels + 1)]

    for i in range(1, num_symbolic_labels + 1):
        path = '.'.join(labels[:i])
        paths.append(path)

    return paths

def domain_byte_length(domain: str):
    """
    Returns the length of the byte representation of a domain name.
    Each label has a length byte plus the bytes for the actual characters. The root label consists only of the length byte
    (zero). For symbolic labels, we assume they consist of one character (i.e., 2 bytes including the length byte).
    """

    return sum(map(label_byte_length, domain.split('.')))

def label_byte_length(label: str):
    # TODO: make this more robust
    if label[:len(SYMBOLIC_LABEL_PREFIX)] == SYMBOLIC_LABEL_PREFIX:
        return 2 # for symbolic labels, we assume one character plus the length byte
    else:
        return 1 + len(label) # note that this also works for the root (empty) label

if __name__ == '__main__':
    test()

