"""
Algorithms and analyses for trees.

Placed in a seperate module for orthogonality and to allow multiple tree
implementations.
"""

### IMPORTS

import triters


### IMPLEMENTATION ###

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


def calc_evol_history (self, nodes, rooted=True):
	"""
	Calculate evolutionary history in the Nee-May-Faith sense.
	  
	If `rooted`, include the root. Note that the nodes do not have to
	be tips but can be internal.
	"""
	if rooted and self.root and (self.root not in nodes):
	   nodes += [self.root]
	   st = self.subtree (nodes)
	   x = sum ([b.distance for b in st.iter_branches()])
	   return x


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



### END #######################################################################

