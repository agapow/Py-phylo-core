"""
Algorithms and analyses for trees.

Placed in a seperate module for orthogonality and to allow multiple tree
implementations.
"""

### IMPORTS

import triters


### IMPLEMENTATION ###

### OVERALL TREE SHAPE

def is_bifurcating (tree, assume_root_branch=True):
	"""
	Is this a strictly binary tree?

	Many algorithms require binary trees. We test this by counting the
	number of neighbours of each node.  A twist is introduced in the
	case of rooted trees, as the root has an inferred extra neighbour. 
	
	"""
	# TODO: allow modification of root behaviour
	## Main:
	# walk the tree and look for a node that isn't binary
	root = tree.root
	for node in tree.iter_nodes():
		num_neighbours = tree.count_adjacent_nodes (node)
		# root must have 2 neighbours
		if (assume_root_branch and (node is root)):
			if (num_neighbours != 2):
				return False
		# non-root nodes must have 3 neighbours or be tips
		else:
			if (num_neighbours not in [1, 3]):
				return False					
	return True


def has_singletons (tree, assume_root_branch=True):
	"""
	Does this tree contain internal nodes with only a single child?

	Many algorithms or parsers assume that all nodes have at least 2 
	descendants (e.g. most Newick readers). In reconstructed phylogenies,
	this holds because internal nodes are evidenced by at least two
	children. But when simulating the growth of phylogenies, in cases of
	phyletic transformation or extinction, we can often end up with
	internal nodes that have only two neighbours, i.e. where a node has
	given rise to a single other node. This function checks for those
	exceptions by counting neighbours. Again, there is an complexity in the
	case of rooted trees, as the root has an inferred extra neighbour.

	Note: there must be a technical term for this but I haven't found
	it.
	"""
	# TODO: allow modification of root behaviour
	## Main:
	# walk the tree an look for a node that isn't binary
	root = tree.root
	for node in tree.iter_nodes():
		num_neighbours = tree.count_adjacent_nodes (node)
		if (assume_root_branch and (node is root)):
			if (num_neighbours == 1):
				return True
		else:
			if (num_neighbours == 2):
				return True
	return False


def has_polytomies (tree, assume_root_branch=True):
	"""
	Does this tree contain internal nodes with evidence of mutltiple splits?

	Are there any nodes at which there appears to have been a split into
	more than 2 children? Again, some algorithms don't behave well in these
	cases and so we check for them. This is not quite the obverse of
	``is_bifurcating`` - tree may contain no polytomies, but may not be
	bifurcating. And again, rooted trees behave differently.
	"""
	## Main:
	# walk the tree and look for a node that is higher than order 3
	root = tree.root
	for node in tree.iter_nodes():
		num_neighbours = tree.count_adjacent_nodes (node)
		if (assume_root_branch and (node is root)):
			if (2 < num_neighbours):
				return True
		else:
			if (3 < num_neighbours):
				return True
	return False


### SUBTREE SHAPE

def mrca (tree, nodes):
	"""
	Find the most recent common ancestor of a set of nodes.

	:Params:
		tree
			a rooted phylogenetic tree
		nodes
			an iterable of nodes, iternal or tips
	:Returns:
		The most recent common ancestor of the nodes passed in.

	If only a single node is passed in, it is returned as the answer (being the
	common ancestor of itself).	
	
	Of course, this only works with rooted trees.
	"""
	## Preconditions:
	assert (tree.is_rooted), "requires a rooted tree"

	## Main:
	# We do this by walking from the first node to the root. This gives an
	# list of possible mrcas. Then we walk up from every other node and
	# check where they intersect with that list.
	root_path = [n for n in triters.iter_nodes_to_root (tree, nodes[0])]
	mrca_or_below = [root_path[0]]
	possible_higher_mrca = root_path[1:]
	root = possible_higher_mrca[-1]
	
	for n in nodes[1:]:
		# if there are no more possible mrcas, then we have walked all the way
		# to the root and evrything is included
		if len (possible_higher_mrca) == 0:
			return root
		# otherwise, walk up to root and see where it intersects previously
		# explored nodes or the possible higher mrca list		
		for p in triters.iter_nodes_to_root (tree, n):
			if p in mrca_or_below:
				# this node is below one we have already examined
				break 
			elif p in possible_higher_mrca:
				# this node interesects above the previous mrca
				p_index = possible_higher_mrca.index (p)
				mrca_or_below.extend (possible_higher_mrca[:p_index+1])
				possible_higher_mrca = possible_higher_mrca[p_index+1:]
				break
			else:
				# this must be below the mrca
				mrca_or_below.append (p)

	## Postconditions & return:
	# the most recent addition to the mrca list should be the highest one
	return mrca_or_below[-1]


def is_monophyletic (tree, nodes):
	"""
	Do these nodes form a coherent subtree with no other tips included?

	:Params:
		tree
			a rooted tree
		nodes
			a list of nodes within that tree
	
	:Returns:
		a boolean

	Note that you can pass internal nodes in the list of nodes without causing
	as error, but the answer will be False unless all tips descended from that
	node are also included.

	(It is actually debatable how internal nodes should be treated in this
	context. You could argue that passing an internal node is equivalent to
	including all below it, so it may be more sensible  
	"""
	# XXX: a cumbersome way to solve this, but it works
	## Preconditions:
	assert (tree.is_rooted()), "monophyley requires a root"
	## Main:
	# find the common ancestor of the tips
	m = mrca (tree, nodes)
	# for every tip descended from it, does it appear in the passed list?
	iterable = iter_nodes_subtree (tree, m)
	for t in itertools.ifilter (lambda n: tree.is_tip_node (n), iterable):
	   if t not in nodes:
	      return False
	return True


### METRICS

def evol_history (tree, nodes, rooted=True):
	"""
	Calculate evolutionary history in the Nee-May-Faith sense.

	:Params:
		tree
			a tree

	  
	If `rooted`, include the root. Note that the nodes do not have to
	be tips but can be internal.
	"""
	## Preconditions:

	## Main:
	if rooted and tree.root and (tree.root not in nodes):
	   nodes += [tree.root]
	   st = tree.subtree (nodes)
	   x = sum ([b.distance for b in st.iter_branches()])
	   return x


def total_distance (tree):
	"""
	Calculate the total distance encompassed by a tree.
	
	This simply iterates over the branches and sums distances.
	"""
	# TODO: addition functor
	return sum ([b['distance'] for b in t.iter_branches()])


def rooted_subtree_history (rtree, nodes, inc_root=True):
	"""
	Calculate evolutionary history a la May-Nee or Faith.
	
	:Parameters:
		rtree
			a rooted tree
		nodes
			a subtree as defined 
	
	EH can only be calculated over a rooted tree since 
	"""
	## Preconditions:
	assert (rtree.is_rooted), \
		"evolutionary history can only be calculated over a rooted tree"
	## Main::
	stree = rtree.copy_rooted_subtree (nodes)
	
	## Postconditions & return:


### END #######################################################################

