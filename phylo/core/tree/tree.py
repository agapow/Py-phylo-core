#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A simple but complete class for phylogenetic trees.

"""
# TODO: need a tree construction mixin?

__docformat__ = 'restructuredtext en'


### IMPORTS ###

__all__ = [
	'Tree',
]

from exceptions import NotImplementedError
from copy import deepcopy

from phylo.core.impl.odict import Odict
from node import Node
from branch import Branch


### IMPLEMENTATION ###

class Tree (IterableTreeMixin):
	"""
	A simple tree implementation.

	This is a dead simple and (dead dumb) implementation of a phylogeny class.
	More specifcally, it's the machinery required to store and manipulate nodes
	and branches. Here it is done as a series of ordered dictionaries, with nodes
	and branches as keys. This is not especially fast, but is fast enough for
	most circumstances.
	
	Obviously other (faster or better) implementations are possible, for which
	this can serve as a reference.

	Additional functionality, that uses this core, is bought in from the mixins
	classes.

	"""
	# TODO: default node and branch properties for the tree?
	# TODO: tree should function as factory for b & n to achieve this?
	# TODO: for rooted trees & some display, nodes have to order. Odict?
	# TODO: c'tor should provide / allow translation table & impl
	# TODO: c'tor should provide / allow distance math & default blen?

	## LIFECYCLE:
	# The tree must support initialisation, destruction and copying.
	
	def __init__ (self, dist_type=float):
		"""
		Create a tree.
		
		Args:
			dist_type (Type): how branchlengths are measured in the tree. Currently
				unused.
			
		Returns:
			a new and empty tree
		
		"""
		# nested dict to go from node pairs to branches d[n1][n2] -> b
		self._nodes = {}
		# single layer dict to go from branch to nodes d[b] -> (n1, n2)
		self._branches = {}
		# the tree root if defined
		self._root = None
		self._root_branch = None
		# TODO: implementA simple 
		# self._dist_type = dist_type
		
	def __del__ (self):
		"""
		Clean up the tree before deletion.
		
		This is necessary for peace of mind due to some internal cyclic data
		structures. Note that there are circumstances in Python where object
		destruction isn't orderly (e.g. when a session is closed) causing the
		issuing of alarming but harmless errors (e.g. "no attribute
		called _branches")  
		"""
		# destroy all references to nodes and branches
		self._branches.clear()
		# TODO: this is accidentally clearing the nodes not the hash of nodes
		#for n in self._nodes:
		#	n.clear()
		self._nodes.clear()

	def __copy__ (self):
		"""
		Return a copy of this tree.

		This makes a copy of the tree (i.e. the topology). All node and branch
		properties are kept and shared between the new and old tree.
		"""
		new_tree = self.__class__()
		new_tree._nodes, new_tree._branches = self._copy_nodes_and_branches()
		return new_tree
	
	def __deepcopy__ (self):
		"""
		Return a wholly independent copy of this tree.

		This makes a copy of all tree elements tree (i.e. topology, node and
		branch contents).
		"""
		## Main:
		new_tree = self.__class__()
		new_tree._nodes, new_tree._branches, newold_map = \
			self._deepcopy_nodes_and_branches()
		## Postconditions & return:
		return new_tree
		

	## ACCESSORS:
	# Tree size accessors:
		
	def count_nodes (self):
		"""
		How many nodes does this tree contain?
		
		"""
		return len (self._nodes)

	def count_branches (self):
		"""
		How many branches does this tree contain?

		This will be equal to ``count_nodes() - 1``, but we calculate it
		independently. Note this doesn't count any theoretical branch running
		off the root.

		"""
		return len (self._branches)
	
	def __len__ (self):
		"""
		What size is this tree (how many nodes does it contain)?
		
		"""
		return self.count_nodes()

	def is_empty (self):
		"""
		Does the tree have no nodes?

		Then how does it smell?
		
		"""
		return (len (self) == 0)

	# Tree root accessors:
	
	def is_rooted (self):
		"""
		Is a root defined for this tree?
		"""
		# TODO: if the root is deleted, this should update
		return (self.root is not None)
		
	# Tree content accessors:
	
	def iter_nodes (self):
		"""
		Traverse all nodes in the tree.

		The order of iteration isn't guaranteed to be consistent.
		"""
		for n in self._nodes.keys():
			yield n
		
	nodes = property (lambda s: [n for n in s.iter_nodes()])
	
	def iter_branches (self):
		"""
		Traverse all branches in the tree.

		The order of iteration isn't guaranteed to be consistent.
		"""
		for b in self._branches.iterkeys():
			yield b
	
	branches = property (lambda s: [b for n in s.iter_branches()])
	
	
	# Node accessors:
	def node_parent (self, node):
		"""
		Return the parent of this node.
		
		This is an experimental method, to gauge the efficacy of determining
		parents on the fly. Parentage throughout a tree is defined solely by
		the position of the root and so a lot of internal paperwork can be saved
		by *just* recording the root. 
		"""
		# NOTE: it may be easier to traverse from the target to the root,
		# rather than vice-versa
		## Preconditions:
		assert (self.is_rooted()), "this method requires a rooted tree"
		## Main:
		prev_node = None
		for n in self.iter_nodes_preorder():
			if (n is node):
				return prev_node
			else:
				prev_node = n
		assert (False), "node '%s' is not a member of this tree" % node
		
	def node_children (self, node):

	def node_neighbours (self, node):
		"""
		How many nodes are directly adjacent to this one?

		In graph theory terms, this gives the *order* of the node.
		"""
		return len (self._nodes[node])

	def is_node_tip (self, node):
		"""
		Is this a terminating (leaf) node?
		"""
		# NOTE: we allow for singleton root nodes
		return (self.root != node) and (len (self.node_neighbours (node)) == 1)

	def get_nodes (self, branch):
		"""
		Return the nodes abutting either end of a branch.

		Returns:
			A tuple of the two nodes. Order is not specified.

		"""
		return self._branches[branch]

	# Branch accessors:
	def get_branch (self, node1, node2):
		"""
		Return the branch running between two nodes.
		"""
		return self._nodes[node1][node2]

	## MUTATORS
	# Tree construction:
	
	def add_node (self, parent=None, node_props=None, distance=None,
			branch_props=None):
		"""
		Create a node and connect it to the rest of the tree.

		Args:
			parent (Node): The node to connect the new node to. If this is the
				first node, this argument should be unused.

			dist: The distance of the newly created branch between the parent and
				new node. If this is the first node, this argument should be unused.

			node_props (Dict or mapping): Annotations on the newly created node.

			branch_props (Dict or mapping):  Annotations on the newly created
				branch between the parent and new node. If this is the first node,
				this argument should be unused.

		Returns:
			The newly added node and branch

		"""
		# TODO: what if we want to add an existing node?
		## Main:
		# if this is the first node, don't need parent or branch_props
		if (self.count_nodes() == 0):
			assert ((parent is None) and (branch_props is None)), \
				"no branch can be created for initial node"
			new_node = self._create_node (node_props)
			new_branch = None
		else:
			assert (parent is not None), \
				"Subsequent nodes must be connected to the rest of the tree"
			new_node = self._create_node (node_props)
			new_branch = self._create_branch (distance, branch_props)
			self._link_nodes (parent, new_branch, new_node)
		## Postconditions & return:
		return new_node, new_branch

	def add_first_node (self, node_props=None):
		"""
		Create the first node in the tree.

		A convenience method wrapping ``add_node``, given that its arguments
		concerning branches are not used when creating the first node.

		"""
		# TODO: accept a distance and use it as a node annotation on the root?
		return self._create_node (node_props)
		
	def add_root (self, node_props=None):
		"""
		Create the first node in a rooted tree.

		A convenience method wrapping ``add_node``, given that its arguments
		concerning branches are not used when creating the first node. It also
		sets this first node as the root.

		"""
		root = self.add_first_node (node_props)
		self.root = root
		return root
	
	
	## INTERNAL
	# Root manipulation:
	
	def _get_root (self):
		return self._root
	
	def _set_root (self, new_root):
		## Preconditions:
		assert (new_root is None) or (new_root in self._nodes), \
			"can't set %s (%s) as tree root" % (type (new_root), new_root)
		## Main:
		self._root = new_root
		self._reroot_tree()
		
	root = property (_get_root, _set_root)
	
	def _reroot_tree (self):
		"""
		'Rehang' a tree so the nodes correctly point to their parent.
		
		When a tree is rerooted, the parent-child relationship between
		two nodes may reverse. This internal method should be called after
		a rerooting to ensure every node is pointing at the right parent.
		
		"""
		# TODO: should branches store direction information too?
		def rehang_children (tree, parent, node):
			"""
			Direct all children of a node to point to it. 
			
			We move out recursively from the new root, resetting nodes, and pass
			the parent of this node to ensure it is not reset.
			
			"""
			for c in tree.iter_adjacent_nodes (node):
				if c is not parent:
					indx = [x for x in tree.iter_adjacent_nodes (c)].index (n)
					tree._nodes[c].rotate (-indx)
					rehang_children (tree, node, c)
			
		rehang_children (self, None, self.root)
	
	# Tree construction:
	
	def _create_node (self, props=None):
		"""
		Make a node and record supporting data.
		
		Args:
			props (mapping): a list of properties of the new node
			
		Returns:
			the new node
			
		Internal method: instantiates the node and makes a slot in the internal
		node dictionary.
		
		"""
		# TODO: need to allow for pre-existing nodes being passed in
		if (props is None):
			new_node = Node()
		else:
			new_node = Node (props)
		self._nodes[new_node] = Odict()
		return new_node

	def _create_branch (self, distance=None, props=None):
		"""
		Make a branch and record supporting data.
		
		Args:
			props (mapping): a list of properties of the new branch
			
		Returns:
			the new branch
			
		Internal method: instantiates the branch, makes a slot in the internal
		branch dictionary, and stores the branch in nodes dict for the nodes at
		both ends.
		
		"""
		if (props is None):
			new_branch = Branch ()
		else:
			new_branch = Branch (props)
		if (distance is not None):
			new_branch['distance'] = distance
		self._branches[new_branch] = None
		return new_branch

	def _link_nodes (self, node_1, branch, node_2):
		"""
		Links two nodes together via a branch.
		
		Args:
			node_1 (Node): a (parent) node
			branch (Branch): the branch linking the parent and child
			node_2 (Node): a (child) node
		
		This internal method performs the low-level 'linking' of two nodes
		via a branch. Notice that that all objects (nodes and branches) are
		presumed to already exist and that incautious use can lead to trees with
		cycles. Also note that node order is only important in a rooted tree.
		
		"""
		# TODO: can we keep track of nodes in only 1 way, rather than both ways
		self._branches[branch] = (node_1, node_2)
		self._nodes[node_2][node_1] = self._nodes[node_1][node_2] = branch

	def _unlink_nodes (self, node_1, node_2):
		"""
		Break the connection between two nodes.
		
		Args:
			node_1 (Node): a node
			node_2 (Node): another node, that is a neighbour of the first
			
		Returns:
			the branch linking the two
		
		This internal method is intended for low-level deletion of topology.
		It destroys the implementation details that link the two nodes and will
		result in the deletion of the connecting branch and either of the nodes,
		if they are not referred to elsewhere. Notice that incautious use can lead
		to the cleaving of a tree into unconnected nodes.
		 
		"""
		old_branch = self._nodes[node_1][node_2]
		del self._nodes[node_1][node_2]
		del self._nodes[node_2][node_1]
		del self._branches[old_branch]
		return old_branch

	# TODO: how do we handle deletions? Need to wipe out a subtree, all
	# connected data


### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
