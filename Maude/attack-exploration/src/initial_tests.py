import random
import string
import networkx as nx

from zone import Record

# parameters for random zone generation
DEGREE = 4
CNAME_PROB = 0.5
DNAME_PROB = 0.5
OTHER_TYPES = ['A', 'TXT']
OTHER_TYPES_PROB = [0.5, 0.5]

CNAME_NX_TARGET_PROB = 0.5

TTL = 3600

NODE_ATTRS = ['types', 'records']

# test variables
TEST_OTHER_NAMES = ['', 'com.', 'victim.com.', 'www.victim.com.', 'abc.victim.com.']

def random_label(n):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(n))


def zone_add_labels(g: nx.DiGraph, name: str) -> None :
    g.nodes[0]['name'] = name
    for child in g.successors(0):
        zone_add_labels_rec(g, child, name)

def zone_add_labels_rec(g: nx.DiGraph, root: int, path: str) -> None :
    label = random_label(3)
    new_path = f'{label}.{path}'
    g.nodes[root]['name'] = new_path
    for child in g.successors(root):
        zone_add_labels_rec(g, child, new_path)
    
def tree_str(g: nx.DiGraph, root: int, level: int) -> str :
    res = node_str(g, root, level) + '\n'
    for child in g.successors(root):
        res += tree_str(g, child, level + 1)
    return res

def node_str(g: nx.DiGraph, root: int, level: int) -> str :
    res = ' ' * 8 * level + f'({g.nodes[root]["name"]}): '
    
    if 'types' in g.nodes[root]:
        res += f'types={g.nodes[root]["types"]}'
    
    if 'records' in g.nodes[root]:
        for record in g.nodes[root]['records']:
            res += '\n' + ' ' * 8 * level + ' ' * 4 + str(record)

    res += '\n'

    return res

def node_choose_rrsets(g: nx.DiGraph, root: int) -> None :
    
    if root == 0:
        g.nodes[root]['types'] = ['SOA', 'NS']    
    else:
        g.nodes[root]['types'] = []
    
    delegated = False
    if g.out_degree(root) == 0:
        # node is a leaf
        
        # TODO: choose if delegated
        if delegated:
            # do something
            pass
        
        else:
            if random.random() < DNAME_PROB:
                g.nodes[root]['types'].append('DNAME')

    
    if not delegated:
        # choose if there is a CNAME
        if not g.nodes[root]['types'] and random.random() < CNAME_PROB:
            g.nodes[root]['types'].append('CNAME')

        else:
            for type, prob in zip(OTHER_TYPES, OTHER_TYPES_PROB):
                if random.random() < prob:
                    g.nodes[root]['types'].append(type)

def get_TXT_rrset(owner):
    return [Record(owner, 'TXT', TTL, 'Hello World.')]

def get_A_rrset(owner):
    return [Record(owner, 'A', TTL, '1.2.3.4')]

def get_CNAME_rrset(owner, other_names):
    target = random.choice(other_names)
    
    if random.random() < CNAME_NX_TARGET_PROB:
        target = 'nxdomain.' + target   # choose an existing domain and add a non-existent label

    return [Record(owner, 'CNAME', TTL, target)]

def get_DNAME_rrset(owner, other_names):
    target = random.choice(other_names)
    
    if random.random() < CNAME_NX_TARGET_PROB:
        target = 'nxdomain.' + target   # choose an existing domain and add a non-existent label

    return [Record(owner, 'DNAME', TTL, target)]

def node_create_rrsets(g: nx.DiGraph, root: int) -> None :
    g.nodes[root]['records'] = []

    owner = g.nodes[root]['name']
    types = g.nodes[root]['types']

    if 'TXT' in types:
        g.nodes[root]['records'] += get_TXT_rrset(owner)

    if 'A' in types:
        g.nodes[root]['records'] += get_A_rrset(owner)

    if 'CNAME' in types:
        g.nodes[root]['records'] += get_CNAME_rrset(owner, TEST_OTHER_NAMES)

    if 'DNAME' in types:
        g.nodes[root]['records'] += get_DNAME_rrset(owner, TEST_OTHER_NAMES)

def go():

    directed_trees = []

    trees = nx.nonisomorphic_trees(DEGREE)

    for tree in trees:

        print(nx.forest_str(tree))

        nonisomorphic_roots = [0]
        for i in range(1, DEGREE):
            # print(f'nonisomorphic_roots: {nonisomorphic_roots}')

            added_roots = []
            isomorphic = False
            for j in nonisomorphic_roots:
                # print(f'{i}, {j}: ', end='')
                iso = nx.algorithms.isomorphism.rooted_tree_isomorphism(tree, i, tree, j)
                # print(iso)
                if iso:
                    isomorphic = True

            if not isomorphic:
                nonisomorphic_roots.append(i)

        for root in nonisomorphic_roots:

            directed_trees.append(nx.convert_node_labels_to_integers(nx.bfs_tree(tree, root)))
        
        print('====================')

    for directed_tree in directed_trees:
        print(nx.forest_str(directed_tree))

    print('>>>>>>>>>>>>>>>>>>')
    g = directed_trees[0]
    print(nx.forest_str(g))
    zone_add_labels(g, 'attacker.com.')
    print(tree_str(g, 0, 0))

    for i in range(10):
        for node in g.nodes:
            node_choose_rrsets(g, node)
            node_create_rrsets(g, node)
        
        print(tree_str(g, 0, 0))

if __name__ == '__main__':
    go()
