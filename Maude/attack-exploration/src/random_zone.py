import random
import string
import networkx as nx

from zone import Record, Zone
from conversion_utils import addr_op_name_from_domain
from utils import get_domain_prefixes

TTL = 3600 # TTL for generated records
SOA_MINIMUM = 3600 # SOA MINIMUM field (TTL for negative caching)
NUM_NX_LABELS = 1 # number of inexistent labels to add when choosing an inexistent name as target of a record
ALLOW_DNAME_TARGETS_ABOVE_OWNER = False
ALLOW_TARGETS_IN_SAME_ZONE = False
ALLOW_PREFIX_TARGETS = False # whether PREFIXES of existing domains are valid targets, not just the full existing domains
ALLOW_CNAME_LOOPS = False # enforce that there are no CNAME loops within a zone
ALLOW_OBVIOUS_NS_LOOPS = False # enforce that there are no "obvious" NS loops within a zone

CNAME_NX_TARGET_PROB = 0.1
DNAME_NX_TARGET_PROB = 0.5
NS_NX_TARGET_PROB = 0.5

ALLOWED_NS_RRSET_SIZES = [
    1,
    2,
    # 5,
    10,
]

# The record type combinations allowed for the different kinds of nodes
ALLOWED_APEX_TYPES = [
    [],
    ['A'],
    # ['TXT'],
    # ['A', 'TXT'],
]
ALLOWED_NONTERMINAL_TYPES = [
    [],
    ['CNAME'],
    ['A'],
    # ['TXT'],
    # ['A', 'TXT'],
]
ALLOWED_TERMINAL_TYPES = [
    ['NS'], # delegation
    ['DNAME'],
    ['CNAME'],
    ['A'],
    ['A', 'DNAME']
    # ['TXT'],
    # ['A', 'TXT'],
]


def test():
    TEST_OTHER_NAMES = ['', 'com.', 'victim.com.', 'www.victim.com.', 'abc.victim.com.', '*.victim.com.']

    zones = get_random_zones(['attacker1.com.', 'attacker2.com.'], [None, None], 4, TEST_OTHER_NAMES)

    # zones = get_random_zones(['attacker1.com.'], [None], 6, [])

    print('==================')
    for zone in zones:
        print(zone)

def get_random_zones(names, parent_zones, num_nodes: int, other_names):
    """
    Returns a list of random zones.
    """

    trees = get_random_zone_trees(names, num_nodes, other_names)

    zones = []
    for i, tree in enumerate(trees):
        records = []
        for node in tree:
            records += tree.nodes[node]['records']

        zones.append(Zone(names[i], parent_zones[i], records))

    return zones

def get_random_zone_trees(names, num_nodes: int, other_names):
    """
    Returns a list of random zones as domain trees, where each node has the corresponding records attached.
    """

    trees = {}
    names_in_zone = {}

    # first pass: create the underlying trees for all zones and assign owner names
    for name in names:

        trees[name] = get_random_tree(num_nodes)
        assigned_names = add_labels(trees[name], name)

        ns_owner = f'ns.{name}'
        assigned_names.append(ns_owner)

        if ALLOW_PREFIX_TARGETS:
            names_in_zone[name] = get_domain_prefixes(assigned_names)
        else:
            names_in_zone[name] = assigned_names

    # second pass: create RRsets, using the names appearing elsewhere as candidates for NS/CNAME/DNAME values
    for name in names:
        tree = trees[name]

        if ALLOW_PREFIX_TARGETS:
            target_name_candidates = get_domain_prefixes(other_names)
        else:
            target_name_candidates = other_names.copy()

        for inner_name in names:
            if ALLOW_TARGETS_IN_SAME_ZONE or inner_name != name:
                target_name_candidates += names_in_zone[inner_name]

        target_name_candidates = list(set(target_name_candidates))

        # sort for reproducibility
        target_name_candidates.sort()
        print(f'target_name_candidates for {name}: {target_name_candidates}')

        # add random RRsets until we obtain a zone free of CNAME/"obvious NS" loops
        add_random_rrsets(tree, target_name_candidates)
        while (not ALLOW_CNAME_LOOPS and has_cname_loop(tree)) or (not ALLOW_OBVIOUS_NS_LOOPS and has_obvious_ns_loop(tree)):
            print('CNAME/NS loop. Retrying...')
            add_random_rrsets(tree, target_name_candidates)

        # add apex records
        tree.nodes[0]['records'].append(Record(name, 'SOA', TTL, SOA_MINIMUM))
        tree.nodes[0]['records'].append(Record(name, 'NS', TTL, f'ns.{name}'))

        # add name server node
        ns_owner = f'ns.{name}'
        tree.add_edge(0, 'ns')
        tree.nodes['ns']['owner'] = ns_owner
        tree.nodes['ns']['label'] = 'ns'

        # add the address record for the name server
        addr = addr_op_name_from_domain(ns_owner)
        tree.nodes['ns']['records'] = [Record(ns_owner, 'A', TTL, addr)]

    print()

    return list(trees.values())

def add_labels(tree: nx.DiGraph, name: str) -> None :
    """
    Assign owner names to all nodes in the tree. The root will have the given name.
    The labels consist of repetitions of the same random letter. The number of repetitions indicates the level below the root.
    For example, nodes directly below the root get labels 'a', 'b', etc., whereas nodes two levels of the root get labels
    'aa', 'bb', etc.
    Nodes on the same level cannot have the same label. Thus, this function handles a maximum of 26 nodes per level.
    Returns a list of all the owner names that have been assigned.
    """

    tree.nodes[0]['owner'] = name
    owner_names = [name]

    letters = string.ascii_lowercase
    labels = random.sample(letters, tree.out_degree(0))

    for i, child in enumerate(tree.successors(0)):
        owner_names += _add_labels_rec(tree, child, f'{labels[i]}.{name}', 1)

    return owner_names

def _add_labels_rec(tree: nx.DiGraph, node: int, name: str, level: int) -> None :
    tree.nodes[node]['owner'] = name
    owner_names = [name]

    letters = string.ascii_lowercase
    selected_letters = random.sample(letters, tree.out_degree(node))
    labels = [letter * (level + 1) for letter in selected_letters]

    for i, child in enumerate(tree.successors(node)):
        owner_names += _add_labels_rec(tree, child, f'{labels[i]}.{name}', level + 1)

    return owner_names

def get_random_tree(num_nodes: int) -> nx.DiGraph:
    """
    Chooses uniformly at random among all non-isomorphic, rooted trees with the given number of nodes.
    """

    directed_trees = []
    trees = nx.nonisomorphic_trees(num_nodes)

    for tree in trees:
        nonisomorphic_roots = [0]

        for i in range(1, num_nodes):
            isomorphic = False
            for j in nonisomorphic_roots:
                # for all roots already added, check if isomorphic with new candidate root
                iso = nx.algorithms.isomorphism.rooted_tree_isomorphism(tree, i, tree, j)
                if iso:
                    isomorphic = True

            if not isomorphic:
                nonisomorphic_roots.append(i)

        # convert to directed graph and re-number the nodes
        for root in nonisomorphic_roots:
            directed_trees.append(nx.convert_node_labels_to_integers(nx.bfs_tree(tree, root)))

    # print(f'Non-isomorphic trees of degree {degree}:')
    # for directed_tree in directed_trees:
    #     print(nx.forest_str(directed_tree))

    return random.choice(directed_trees)

def add_random_rrsets(tree: nx.DiGraph, other_names):
    """
    Adds random RRsets to all nodes in the tree. The types that can be present at a node differ depending on the kind of node
    (apex, intermediate, leaf). These types, as well as the exact approach for generating RRsets, is defined in the functions
    below.
    """

    for node in tree:
        owner = tree.nodes[node]['owner']

        records = []
        if tree.in_degree(node) == 0:
            # zone apex
            types = get_random_types_for_apex()
            for type in types:
                records += get_random_rrset(owner, type, other_names)

        elif tree.out_degree(node) == 0:
            # node is a leaf
            types = get_random_types_for_terminal()
            for type in types:
                records += get_random_rrset(owner, type, other_names)

        else:
            # inner node
            types = get_random_types_for_nonterminal()
            for type in types:
                records += get_random_rrset(owner, type, other_names)

        tree.nodes[node]['types'] = types
        tree.nodes[node]['records'] = records


def get_random_types_for_apex():
    return random.choice(ALLOWED_APEX_TYPES)

def get_random_types_for_nonterminal():
    return random.choice(ALLOWED_NONTERMINAL_TYPES)

def get_random_types_for_terminal():
    return random.choice(ALLOWED_TERMINAL_TYPES)

def get_random_rrset(owner, type, other_names):
    if type == 'TXT':
        return get_TXT_rrset(owner)
    elif type == 'A':
        return get_A_rrset(owner)
    elif type == 'CNAME':
        return get_CNAME_rrset(owner, other_names)
    elif type == 'DNAME':
        return get_DNAME_rrset(owner, other_names)
    elif type == 'NS':
        return get_NS_rrset(owner, other_names)
    else:
        return []

def get_TXT_rrset(owner):
    return [Record(owner, 'TXT', TTL, '...')]

def get_A_rrset(owner):
    return [Record(owner, 'A', TTL, '1.2.3.4')]

def get_CNAME_rrset(owner, other_names):

    target = random.choice(other_names)
    # exclude owner as target
    while target == owner:
        target = random.choice(other_names)
    
    if random.random() < CNAME_NX_TARGET_PROB:
        target = f'{get_nx_labels(NUM_NX_LABELS, "")}.{target}' # add a non-existent labels to existing domain

    return [Record(owner, 'CNAME', TTL, target)]

def get_DNAME_rrset(owner, other_names):

    target = random.choice(other_names)
    # exclude owner as target
    while target == owner:
        target = random.choice(other_names)
    
    if random.random() < DNAME_NX_TARGET_PROB:
        target = f'{get_nx_labels(NUM_NX_LABELS, "")}.{target}' # add a non-existent labels to existing domain

    elif not ALLOW_DNAME_TARGETS_ABOVE_OWNER:
        # if DNAME targets above the owner are disallowed, retry until we have a valid target
        owner_prefixes = get_domain_prefixes([owner])
        while target in owner_prefixes:
            target = random.choice(other_names)

    return [Record(owner, 'DNAME', TTL, target)]

def get_NS_rrset(owner, other_names):
    records = []
    size = random.choice(ALLOWED_NS_RRSET_SIZES)

    # either use existing or non-existing names for ALL records in the RRset
    nxdomain = random.random() < NS_NX_TARGET_PROB

    if nxdomain:
        # add non-existent labels to existing domain
        # uniqueness is ensured by the non-existent labels, so the existing name can repeat
        targets = [f'{get_nx_labels(NUM_NX_LABELS, i)}.{random.choice(other_names)}' for i in range(size)]
    else:
        # for existing domains, we need to sample without replacement

        # we cannot have more NS records than possible target names
        size = min(size, len(other_names))
        targets = random.sample(other_names, size)

    for target in targets:
        records.append(Record(owner, 'NS', TTL, target))

    return records

def get_nx_labels(num_labels: int, suffix):
    labels = [f'nxdomain{suffix}-{i}' for i in range(1, num_labels + 1)]
    return '.'.join(labels)

def has_cname_loop(tree):
    """
    Returns whether the given zone tree has a CNAME loop.
    """

    records = []
    for node in tree:
        records += tree.nodes[node]['records']

    cname_records = [rec for rec in records if rec.rtype == 'CNAME']

    G = nx.DiGraph()
    for record in cname_records:
        G.add_edge(record.owner, record.rdata)

    return not nx.is_directed_acyclic_graph(G)

def has_obvious_ns_loop(tree):
    """
    Returns whether the given zone tree has an "obvious" NS loop.
    By obvious, we mean loops like < a.com, NS, b.com > < b.com, NS, a.com >,
    i.e., without considering rewriting or names "below" the owner of other NS records.
    """

    records = []
    for node in tree:
        records += tree.nodes[node]['records']

    ns_cname_records = [rec for rec in records if rec.rtype in ['NS', 'CNAME']]

    G = nx.DiGraph()
    for record in ns_cname_records:
        G.add_edge(record.owner, record.rdata)

    return not nx.is_directed_acyclic_graph(G)

def tree_str(g: nx.DiGraph, node: int, level: int) -> str :
    """
    Returns a string representation of a zone tree.
    """

    res = node_str(g, node, level) + '\n'
    for child in g.successors(node):
        res += tree_str(g, child, level + 1)
    return res

def node_str(g: nx.DiGraph, node: int, level: int) -> str :
    """
    Returns a string representation of a node in a zone tree.
    """

    res = ' ' * 8 * level + f'({g.nodes[node]["owner"]}): '
    
    if 'types' in g.nodes[node]:
        res += f'types={g.nodes[node]["types"]}'
    
    if 'records' in g.nodes[node]:
        for record in g.nodes[node]['records']:
            res += '\n' + ' ' * 8 * level + ' ' * 4 + str(record)

    res += '\n'

    return res


if __name__ == '__main__':
    test()
