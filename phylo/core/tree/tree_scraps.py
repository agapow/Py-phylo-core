#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A class for phylogenetic trees.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

__all__ = [
	'Tree',
]

from exceptions import NotImplementedError
from copy import deepcopy

#from relais.dev.common import *

from phylo.core.impl.odict import Odict
from node import Node
from branch import Branch



### IMPLEMENTATION ###

class Tree (object):
	"""
	An base class for phylogenetic trees.
	
	This class encapsulates both rooted and unrooted trees, so the two may be
	easily interconverted and compared. As a consequence, not all methods apply 
	for all instances (e.g. subtree traversal can only be used on rooted
	trees). This class can also serves as an interface or base to other, more
	specialised tree classes. 
	
	In-order iteration isn't provided, as it is meaningless outside strictly
	bifurcating trees.
	
	For example::
	
		# make the tree (A, (B, C))
		>>> t = Tree()
		>>> t.count_nodes()
		0
		>>> r, x = t.add_node (None, {'name': 'root'})
		>>> a, x = t.add_node (r, {'name': 'A'})
		>>> i, x = t.add_node (r, {'name': 'BC'})
		>>> b, x = t.add_node (i, {'name': 'B'})
		>>> c, x = t.add_node (i, {'name': 'C'})
		>>> t.count_nodes()
		5
		>>> t.count_branches()
		4
		

	"""
	# TODO: default node and branch properties for the tree?
	# TODO: tree should function as factory for b & n to achieve this?
	# TODO: for rooted trees & some display, nodes have to order. Odict?
	# TODO: c'tor should provide / allow translation table & impl
	# TODO: c'tor should provide / allow distance math & default blen?

	## LIFECYCLE:
	def __init__ (self, dist_type=float):
		# nested dict to go from node pairs to branches d[n1][n2] -> b
		self._nodes = {}
		# single layer dict to go from branch to nodes d[b] -> (n1, n2)
		self._branches = {}
		# the tree root if defined
		self._root = None
		self._root_branch = None
		self._dist_type = dist_type
		
	def __del__ (self):
		"""
		Clean up the tree before deletion.
		
		This is necessary for piece of mind due to some internal cyclic data
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
		# TODO: test
		new_tree = BaseTree()
		new_tree._nodes, new_tree._branches = self._copy_nodes_and_branches()
		return new_tree
	
	def __deepcopy__ (self, visit={}):
		"""
		Return a wholly independent copy of this tree.

		This makes a copy of all tree elements tree (i.e. topology, node and
		branch contents).
		"""
		## Main:
		new_tree = BaseTree()
		new_tree._nodes, new_tree._branches, newold_map = \
			self._deepcopy_nodes_and_branches()
		## Postconditions & return:
		return new_tree
		

	## ACCESSORS:
	# Tree accessors:
	def is_rooted (self):
		"""
		Is a root defined for this tree?
		"""
		# TODO: if the root is deleted, this should update
		return (self._root is not None)
		
	def count_nodes (self):
		"""
		How many nodes does this tree contain?
		
		"""
		return len (self._nodes)

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
		return (self.count_nodes() == 0)

	def count_branches (self):
		"""
		How many branches does this tree contain?

		This will be equal to ``count_nodes() - 1``, but we calculate it
		independently. Note this doesn't count any theoretical branch running
		off the root.

		"""
		return len (self._branches)

	def count_tip_nodes (self):
		"""
		How many tips / leaves / terminal nodes does this tree have?
		
		"""
		# TODO: need count_internal_nodes?
		return len ([1 for n in self.iter_tip_nodes()])


	# Node accessors:
	def get_parent (self, node):
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

	def count_adjacent_nodes (self, node):
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
		return (self._root != node) and (self.count_adjacent_nodes (node) == 1)

	def get_nodes (self, branch):
		"""
		Return the nodes abutting either end of a branch.

		:Returns:
			A tuple of the two nodes. Order is not specified.

		"""
		return self._branches[branch]

	# Branch accessors:
	def get_branch (self, node1, node2):
		"""
		Return the branch running between two nodes.
		"""
		return self._nodes[node1][node2]




	def clear (self):
		"""
		Empty the tree, removing all nodes and branches.
		"""
		# NOTE: this may be needed to break circular references
		self._branches.clear()
		for item in self._nodes.values():
			item.clear()
		self._nodes.clear()
		
	def shift_neighbours (self, node, shift=1):
		"""
		Change the ordering of connections to adjacent nodes.
		"""
		# TODO: finish
		num_neighbours = self.count_neighbours (node)
		shift = shift % num_neighbours

	## ITERATORS & TRAVERSAL
	# Across the whole tree
	
	def iter_nodes (self):
		"""
		Traverse all nodes in the tree.

		The order of iteration isn't guaranteed to be consistent.
		
		"""
		for n in self._nodes.iterkeys():
			yield n

	def iter_tips (self):
		"""
		Traverse all tips in the tree.

		The order of iteration isn't guaranteed to be consistent.
		
		"""
		for n in self._nodes.iterkeys():
			if self.is_node_tip (n):
				yield n

	def iter_branches (self):
		"""
		Traverse all branches in the tree.

		The order of iteration isn't guaranteed to be consistent.
		"""
		for b in self._branches.iterkeys():
			yield b

	def tips (self):
		return [t for t in self.iter_tips()]

	def nodes (self):
		return self._nodes.keys()
	
	
	# In relation to a given node
	
	def parent_node (self, n):
		"""
		Return the parent of this node, or None if root.
		
		Note: only sensible if tree is rooted.
		"""
		neighbours = self._nodes[n].keys()
		if len(neighbours):
			return self._nodes[n].keys()[0]
		else:
			return None
	
	def iter_child_nodes (self, n):
		"""
		Traverse all direct children of a node.
		
		Note that unlike other iterators, this requires a explicit starting
		node.
		
		"""
		## Preconditions & preparation:
		assert (self.root), "this method requires a rooted tree"
		## Main:
		parent = self.get_parent (n)
		for c in self.iter_adjacent_nodes (n):
			if c is parent:
				continue
			else:
				yield c
		
	def iter_adjacent_nodes (self, n):
		"""
		Traverse directly adjacent nodes. 

		See `iter_nodes` for further notes.
		
		"""
		for n in self._nodes[n].keys():
			yield n
	
	
	## INTERNALS
	def _copy_nodes_and_branches (self):
		"""
		Return copies of the node and branch data structures.

		Internal method, for use in copying the tree. Nodes and branches
		are left alone, only the topology is copied. This is written as a
		separate method for possible use in derived classes.

		:Returns:
			The node and branch dictionaries.

		"""
		# copy topology from previous tree, keeping nodes and branches
		node_dict = {}
		branch_dict = {}
		for node, neighbour_dict in self._nodes.iteritems():
			new_neighbours = {}
			for neighbour, branch in neighbour_dict.iteritems():
				new_neighbours[neighbour] = branch
				branch_dict._branches[branch] = (node, neighbour)
			node_dict._nodes[node] = new_neighbours
		return node_dict, branch_dict
	
	def _deepcopy_nodes_and_branches (self):
		"""
		Return deepcopies of the node and branch data structures.

		Internal method, for use in deepcopying the tree. All nodes and branches
		are new and independent of the originals. This is written as a separate
		method for possible use in derived classes.

		:Returns:
			The node and branch dictionaries and a dictionary mapping the
			original nodes to the new ones.

		"""
		# TODO: test
		# TODO: copy property values as well?
		## Main:
		# create cache to map old objects to new
		copied_objs = {}
		def get_copy (orig_obj):
			new_obj = copied_objs.get (orig_obj, None)
			if (new_obj == None):
				new_obj = deepcopy (orig_obj)
				copied_objs[orig_obj] = new_obj
			return new_obj
		# reconstruct data structures, replacing old objs with new
		node_dict = {}
		branch_dict = {}
		for node, neighbour_dict in self._nodes.iteritems():
			new_node = get_copy (node)
			new_neighbours = {}
			for neighbour, branch in neighbour_dict.iteritems():
				new_neigh = get_copy (neighbour)
				new_branch = get_copy (branch)
				new_neighbours[new_neigh] = new_branch
				branch_dict[new_branch] = (new_node, new_neigh)
			node_dict[new_node] = new_neighbours
		## Postconditions & return:
		return node_dict, branch_dict, copied_objs
	

	
		
		


	def _validate (self):
		"""
		A self diagnosis function that checks the tree is in a valid state.

		This is intended for use during development, so various tree-building
		and reading functions can be tested to check they are internally
		consistent and correct. It is not intended to be fast or computationally
		cheap.

		"""
		# check branch data correlates with nodes
		for branch in self.iter_branches():
			a, b = self.get_nodes (branch)
			assert (self._nodes[a].has_key(b)), "a doesn't have b as neighbour"
			assert (self._nodes[b].has_key(a)), "b doesn't have a as neighbour"
			assert (self._nodes[a][b] is branch), "ab doesn't link to branch"
			assert (self._nodes[b][a] is branch), "ba doesn't link to branch"

		# check node data correlates with each other and branches
		for node in self.iter_nodes():
			neighbours = self._nodes[node].keys()
			for n in neighbours:
				assert (self._nodes[n].has_key(node)), "neighbour doesn't link to node"
				assert (self._nodes[node][n] is self._nodes[n][node]), "node and neighbour don't agree on branch"
				branch = self._nodes[node][n]
				assert (self._branches.has_key (branch)), "branch is not stored"
				assert (node in self._branches[branch]), "node not linked by branch"
				assert (n in self._branches[branch]), "neighbour not linked by branch"

	def _dump (self):
		"""
		A crude function to aid debugging structural problems
		"""
		i = 1;
		for n in self.iter_nodes():
			n['_dumpid'] = 'n%s' % i
			i += 1
		for b in self.iter_branches():
			b['_dumpid'] = 'b%s' % i
			i += 1

		print ("Nodes:")
		for n in self._nodes.keys():
			print ("* dumpid %s: %s" % (n.get ('_dumpid'), n))
			for c, b in self._nodes[n].iteritems():
				print ("   - %s (branch %s, dist %s)" % (c.get ('_dumpid'), b.get ('_dumpid'), b.distance))
		print ("Branches:")
		for b, node_list in self._branches.iteritems():
			print ("* dumpid %s: %s" % (b.get ('_dumpid'), b))
			for n in node_list:
				print ("   - %s" % n.get ('_dumpid'))
				


### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
