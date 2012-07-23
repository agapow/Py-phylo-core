
import itertools
from tree import Tree


def find_node (tree, pred, iter=None, from_node=None):
	"""
	Find the first node that matches the conditional function.
	"""
	for n in iter_find_nodes (tree, pred, iter, from_node):
		return n
	return None


def find_all_nodes (tree, pred, iter=None, from_node=None):
	return [n for n in iter_find_nodes (tree, pred, iter, from_node)]


def iter_find_nodes (tree, pred, iter=None, from_node=None):
	if iter == None:
		iter = Tree.iter_nodes
	if from_node == None:
		iterable = iter (tree)
	else:
		iterable = iter (tree, from_node) 
	for n in itertools.ifilter (pred, iterable):
		yield n




def iter_internal_nodes (self):
	"""
	Traverse the internal nodes of the tree.
	
	The order of iteration isn't guaranteed to be consistent. Notice that in
	rooted trees, the root is included unless it is a singleton.
	"""
	return self.iter_nodes_if (lambda t, n: (1 < t.count_adjacent_nodes (n)))

def iter_tip_nodes (self):
	return self.iter_nodes_if (lambda t, n: (t.count_adjacent_nodes (n) == 1))


def iter_nodes_postorder (self, start, from_node=None):
	"""
	Do a postorder (children / tips first) traversal of the nodes.
	"""
	# TODO: use `_iter_adjacent_nodes_except`
	if (start is None):
		raise StopIteration
	for neighbour in self.iter_adjacent_nodes (start):
		if (neighbour is not from_node):
			for child in iter_nodes_postorder (self, neighbour, start):
				yield child
	yield start
	
def iter_branches_postorder (self, start, from_node=None):
	"""
	Do a postorder (children / tips first) traversal of the branches.
	"""
	# TODO: use `_iter_adjacent_nodes_except`
	if (start is None):
		raise StopIteration
	for neighbour in self.iter_adjacent_nodes (start):
		if (neighbour is not from_node):
			for child_br in iter_branches_postorder (self, neighbour, start):
				yield child_br
		yield self.get_branch (start, neighbour)

def iter_nodes_preorder (self, start, from_node=None):
	"""
	Do a postorder (children / tips first) traversal of the nodes.
	"""
	# TODO: use `_iter_adjacent_nodes_except`
	# TODO: why did I do this? See below.
	if (start is None):
		raise StopIteration
	yield start
	for neighbour in self.iter_adjacent_nodes (start):
		if (neighbour is not from_node):
			for child in self.iter_nodes_preorder (neighbour, start):
				yield child



# rooted traversal
def iter_nodes_subtree (self, start):
	"""
	Traverse all nodes in a subtree.
	
	Note that no consistent order is guaranteed.
	"""
	return self.iter_nodes_postorder_subtree (self, start)	

def iter_subtree_postorder (self, start):
	"""
	Traverse nodes postorder (children / tips first) down from this node.
	
		:Params:
			start
				The node to start traversal from.
				
		:Returns:
			A tree node.
	
	Notice that traversal includes - and finishes with - the start node, at
	the head of the tree.
	
	"""
	## Preconditions & preparation:
	assert (self.is_rooted()), "method requires a rooted tree"
	## Main:
	parent = self.get_parent (start)
	# actually yield nodes
	for child in self.iter_adjacent_nodes_except (start, parent):
		for curr_node in self._iter_nodes_postorder_subtree (child, parent):
			yield curr_node
	yield start
	
def _iter_subtree_postorder (self, start, parent):
	"""
	Traverse the nodes postorder within a subtree.
	
	"""
	# actually yield nodes
	for child in self.iter_adjacent_nodess_except (start, parent):
		for curr_node in self._iter_nodes_postorder_subtree (child):
			yield curr_node
	yield start
		

def iter_subtree_preorder (self, start):
	"""
	Traverse nodes preorder (ancestors first) down from this node.

		:Params:
			start
				The node to start traversal from.

		:Returns:
			A tree node.

	Notice that traversal includes - and starts with - the start node, at
	the head of the tree. 

	"""
	## Preconditions & preparation:
	assert (self.is_rooted()), "method requires a rooted tree"
	## Main:
	parent = self.get_parent (start)
	# actually yield nodes
	yield start
	for child in self.iter_adjacent_nodes_except (start, parent):
		for curr_node in self._iter_nodes_postorder_subtree (child, parent):
			yield curr_node

def _iter_subtree_preorder (self, start, parent):
	"""
	Traverse the nodes preorder within a subtree.


	"""
	# actually yield nodes
	yield start
	for child in self.iter_adjacent_nodess_except (start, parent):
		for curr_node in self._iter_nodes_postorder_subtree (child):
			yield curr_node
