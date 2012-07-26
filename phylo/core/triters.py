"""
Tree iterators and functions for searching within a tree.

Tree iterators should follow the general form:

	iter_object_[direction] (tree, start=None, stop=None)

where:

* iterators are named as ``iter_object[_direction]``, where ``object`` is the
  type being returned by the iterator (e.g. ``node`` or ``branch``) and
  ``direction`` indicates what order the iteration takes place in (e.g.
  ``postorder``, ``to_root``).

* ``start`` is where traversal begins, i.e. the first value returned. If
  ``None`` is passed, a logical starting point is selected, usually the root.

* ``stop`` is where traversal halts. If given, this value will not be returned,
  i.e. iteration stops just before the value, in line with other Python
  iterators. If ``None`` is passed, traversal continues until the iterator is
  exhausted. 

"""


### IMPORTS

import itertools
from tree import Tree


### IMPLEMENTATION ###

### FIND
# For locating nodes that match a given predicate

def find_node (tree, pred, iter=None, start=None, stop=None):
	"""
	Find the first node that matches the conditional function.
	"""
	for n in iter_find_nodes (tree, pred, iter, start=start, stop=stop):
		return n
	return None


def find_all_nodes (tree, pred, iter=None, start=None, stop=None):
	"""
	Return a list of all nodes that match the conditional function.
   """
	return [n for n in iter_find_nodes (tree, pred, iter, start=start, stop=stop)]


def iter_find_nodes (tree, pred, iter=None, start=None, stop=None):
	"""
	Iterate over all nodes that match the conditional function.
	"""
	if iter == None:
		iter = Tree.iter_nodes
	if start == None:
		iterable = iter (tree)
	else:
		iterable = iter (tree, start=start, stop=stop) 
	for n in itertools.ifilter (pred, iterable):
		yield n


### MISC

def iter_nodes_to_root (tree, start):
	## Preconditions:
	assert (tree.is_rooted()), "traversal requires root for destination"
	## Main:
	root = tree.root
	curr_node = start
	while curr_node != root:
		yield curr_node
		curr_node = tree.parent_node (curr_node)
	yield root
	

### NODE TYPES

def iter_internal_nodes (self):
	"""
	Traverse the internal nodes of the tree.
	
	The order of iteration isn't guaranteed to be consistent. Notice that in
	rooted trees, the root is included unless it is a singleton.
	"""
	return self.iter_nodes_if (lambda t, n: (1 < t.count_adjacent_nodes (n)))


def iter_tip_nodes (self):
	return self.iter_nodes_if (lambda t, n: (t.count_adjacent_nodes (n) == 1))


### ORDER-BASED
# XXX: currently restrict ordered traversal to rooted trees. Unclear if
# it makes sense in other contexts or how it can be consistently
# implemented
# XXX: do we need order branch traversal?

def iter_nodes_postorder (self, start=None):
	"""
	Do a postorder (children / tips first) traversal of the nodes.
	"""
	## Preconditions & preparation:
	assert (tree.is_rooted()), "traversal requires rooted tree"
	start = start or tree.root
	## Main:
	for neighbour in self.iter_child_nodes (start):
		for child in iter_nodes_postorder (self, neighbour, start):
			yield child
	yield start

	

def iter_nodes_preorder (self, start=None):
	"""
	Do a postorder (children / tips first) traversal of the nodes.
	"""
	## Preconditions & preparation:
	assert (tree.is_rooted()), "traversal requires rooted tree"
	start = start or tree.root
	## Main:
	yield start
	for neighbour in self.iter_child_nodes (start):
		for child in self.iter_nodes_preorder (neighbour, start):
			yield child



### ROOTED (SUBTREE) TRAVERSAL

def iter_nodes_subtree (tree, start):
	"""
	Traverse all nodes in a subtree.
	
	Note that no consistent order is guaranteed.
	"""
	return iter_nodes_subtree_postorder (tree, start)	


def iter_nodes_subtree_postorder (self, start):
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
	parent = self.parent_node (start)
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
