
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

for n in t.nodes:
	print n
	print t.node_children (n)
	print 

