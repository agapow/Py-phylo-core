
# create a test tree
from phylo.core.tree import Tree
t = Tree()
a = t.add_root ({'title': 'A'})
b, br = t.add_node (a, {'title': 'B'})
c, br = t.add_node (a, {'title': 'C'})
d, br = t.add_node (b, {'title': 'D'})
e, br = t.add_node (b, {'title': 'E'})
f, br = t.add_node (c, {'title': 'F'})
g, br = t.add_node (c, {'title': 'G'})

 
start = t.find_node (lambda x: x.title == 'D')
n_path = [n for n in t.iter_nodes_to_root (start)]
n_titles = [x.title for x in n_path]
assert (n_titles == ['D', 'B', 'A']), "expected nodes D-B-A, actually got '%s'" % n_titles

