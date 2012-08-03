#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A class for phylogenetic trees.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from exceptions import NotImplementedError
from copy import deepcopy

#from relais.dev.common import *

from phylo.core.impl.odict import Odict
from node import Node
from branch import Branch

__all__ = [
	'Tree',
]


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

	def get_centroid_nodes (self):
		"""
		Return the nodes which are closest to the tree centroid.

		As per Jordan (1869), the centroid is the point at which the number of
		nodes on either side are most equal, the best possible balance. A tree
		will have either one or two centroids. If two, they will be neigbours,
		and both are returned.

		We calculate this by 'eating away' at the tips of the tree, until only 1
		or 2 are left. Put another way, we list the nodes and their order,
		remove the nodes with order 1 and lower the order of any nodes they are
		attached to, and repeat until 1 or 2 are left.

		There are some apparent conflicts with definition. According to
		Mathworld, the 'weight' of a node is equal to the distance to the
		furtherest node, and the centroid is the node with the lowest 'weight'.

		:Returns:
			A list of the centroids.

		"""
		## Main:
		# get a dict of nodes and orders
		residue_nodes = dict ([(n, self.count_adjacent_nodes (n)) \
			for n in self.iter_nodes()])

		while (2 < len (residue_nodes)):
			outer_nodes = [n for n, v in residue_nodes.iteritems() if (v == 1)]
			for node in outer_nodes:
				del residue_nodes[node]
				for neighbour in self.iter_adjacent_nodes (node):
					if (residue_nodes.has_key (neighbour)):
						residue_nodes[neighbour] -= 1

		## Return:
		return residue_nodes.keys()

	def get_dists_from_node (self, node, dist_fxn=None):
		"""
		Return the distance that nodes lie from a given node.

		"""
		# TODO: allow multiple nodes?
		## Preparations:
		if (dist_fxn is None):
			dist_fxn = lambda a, b: self.get_distance (a, b)
		## Main:
		remaining_nodes = [n for n in self.iter_nodes() if n is not node]
		pending_nodes = [node]
		all_nodes = {node: 0}
		while pending_nodes:
			curr_node = pending_nodes.pop(0)
			dist = all_nodes[curr_node]
			for curr_neighbour in self.iter_adjacent_nodes (curr_node):
				if (curr_neighbour in remaining_nodes):
					all_nodes[curr_neighbour] = dist + \
						dist_fxn (curr_node, curr_neighbour)
					pending_nodes.append (curr_neighbour)
					remaining_nodes.remove (curr_neighbour)
		return all_nodes

	def subtree (self, nodes):
		"""
		Given a list of nodes, construct a tree consisting of just those nodes.
		
		Note that this shares the actual nodes and branches with the original
		tree. If you want to start messing with it, make a copy.
		"""
		## Main:
		st = self.__class__ (dist_type=self._dist_type)
		
		# the "solution" - branches will link the nodes, but not in order
		nodes_in_subtree = nodes[0:1]
		branches_in_subtree = []
		# the nodes still to be fouond or linked into the subtree
		nodes_to_process = nodes[1:]
		
		def extend_path (t, p):
			"""
			Extend the node paths passed by a single node. 
			
			:Parameters:
				t
					a tree
				path
					a list of node that traverses the tree
					
			:Returns:
				All paths the original can be grown into
					
			This extends the path by any means possible and returns a list of the
			new paths. It drops those paths that are deadends.
			"""
			new_paths = []
			last = p[-1]
			if 1 < len (p):
				next_to_last = p[-2]
			else:
				next_to_last = None
			for next_node in t.iter_adjacent_nodes (last):
				if next_node is next_to_last:
					pass
				else:
					new_paths.append (p + [next_node])
			return new_paths
		
		for start in nodes_to_process:
			if start in nodes_in_subtree:
				continue
			
			# the list of growing paths
			paths_to_explore = [[start]]
			connected = False
			while connected is False:
				new_paths = []
				for o in paths_to_explore:
					new_paths += extend_path (self, o)
				for np in new_paths:
					if np[-1] in nodes_in_subtree:
						nodes_in_subtree.extend(np[:-1])
						new_branches = [self._nodes[np[i]][np[i+1]]
							 for i in range (len (np) - 1)]
						branches_in_subtree.extend (new_branches)
						connected = True
						break
				if connected:
					break
				paths_to_explore = new_paths
				
		
		stree = self.__class__(dist_type=self._dist_type)
		for n in nodes_in_subtree:
			stree._nodes[n] = Odict()
		for b in branches_in_subtree:
			n1, n2 = self._branches[b]
			stree._link_nodes (n1, b, n2)
		
		## Return:
		return stree

	def mrca (self, nodes):
		assert (self.is_rooted()), "only works on rooted tree"
		assert (2 <= len (nodes)), "need a list of nodes"
		# make a path from the first node to the root
		root_path = []
		curr_node = node[0]
		while curr_node:
			root_path.append (curr_node)
			curr_node = self.get_parent (curr_node)
			
		

		

	
	def calc_evol_history (self, nodes, rooted=True):
		"""
		Calculate evolutionary history in the Nee-May-Faith sense.
		
		If `rooted`, include the root. Note that the nodes do not have to be tips,
		but can be internal.
		"""
		if rooted and self.root and (self.root not in nodes):
			nodes += [self.root]
		st = self.subtree (nodes)
		x = sum ([b.distance for b in st.iter_branches()])
		return x
		

	def is_monophyletic (self, tips):
		"""
		Does the list of tips form a coherent subtree with no other tips included?
		"""
		st = self.subtree (tips)
		for t in self.get_tips_subtended (st.root):
			if t not in tips:
				return False
		return True
		


	def get_tips_subtended (self, center):
		"""
		How many tip nodes eventually derive from this node.

		We define tips to subtend themselves (and therefore be valued as 1) and
		the 'center' of the tree to subtend all tips.

		:Returns:
			A dictionary of node - number of tips.

		"""
		# TODO: should be iter_subtree_tips?
		## Preparations:

		## Main:
		from triters import iter_nodes_postorder
		tips_subtended = {}
		for node in iter_nodes_postorder (self, center):
			if (self.is_node_tip (node)):
				tips_subtended[node] = 1
			else:
				sum_tips = 0
				for child in self.iter_adjacent_nodes (node):
					sum_tips += tips_subtended.get (child, 0)
				tips_subtended[node] = sum_tips
		return tips_subtended

	def get_distance_from_node (self, center, dist_fxn=None):
		"""
		Return the distance that nodes lie from a given node.

		By definition, the node itself lies 0 distance.
		"""
		# TODO: allow multiple nodes?
		## Preparations:
		if (dist_fxn is None):
			dist_fxn = lambda a, b: self.get_distance (a, b)
		## Main:
		dist_from_center = {}
		for node in self.iter_nodes_preorder (center):
				sum_dist = 0.0
				for parent in self.iter_adjacent_nodes (node):
					if dist_from_center.has_key (parent):
						sum_dist = dist_from_center[parent] + \
							dist_fxn (node, parent)
				dist_from_center[node] = sum_dist
		return dist_from_center

	## MUTATORS:
	def unroot (self):
		self.root = None
		


	def insert_node_between (self, parent, child, node_props=None, distance=None,
			branch_props=None):
		"""
		Insert a node between the two given.

		In other programs, this is referred to as bisect. It behaves like the
		other node creation functions, and asides from the insertion, does not
		alter the tree structure (i.e. branchlengths on other nodes are not
		touched). The child node (the one being inserted above), stays the same
		distance away from the new node as it was from its old parent. In effect
		this stretches away the node below with the introduction of the new.

		While we talk here about placing a new node above a child and below it's
		parent, this usage is arbitrary. By swapping the order of the nodes, the
		same distance could be maintained from the parent to the new node.
		Note that currently ordering is not maintained.
		"""
		# NOTE: parent --(new_branch)--> new_node --(old_branch)--> child
		# do upper (new) branch
		new_node = self._create_node (node_props)
		new_branch = self._create_branch (distance, branch_props)
		self._link_nodes (parent, new_branch, new_node)
		# move lower (old) branch
		old_branch = self._nodes[parent][child]
		del self._nodes[parent][child]
		del self._nodes[child][parent]
		self._nodes[new_node][child] = self._nodes[child][new_node] = old_branch
		self._branches[old_branch] = (new_node, child)
		## Return:
		return new_node

	def collapse_node_into (self, dead_node, new_neighbour):
		"""
		Remove a node, moving any connections to a given neighbour.
		
		This is intended for use in creating polytomies, or destroying singletons
		that may create algorithmic problems or internal nodes that may not exist.
		The opposite of `insert_node`, this essentially "retracts" a node
		into its parent, swapping it for its children. This is exactly like
		collapsing into a polytomy. In effect the branch connecting the child
		to the parent disappears.
		This deletes a node and its branch to another node while preserving
		all other objects by reconnecting them to that neighbour. For example,
		given nodes ``{X, A, B, C}`` where ``A``, ``B`` and ``C`` are connected to ``X`` by branches
		a, b & c respectively::
		
			collapse_into (X, A)
			
		would result in the deletion of ``X`` and ``a``, with nodes ``B`` & ``C`` now adjacent
		``A`` with branches ``b`` & ``c``.
		
		"""
		# TODO: allow for distance transformation
		# TODO: assert connection?
		## Main:
		# gather the nodes & branches to be preserved
		neighbours = [n for n in self.iter_adjacent_nodes (dead_node)]
		branches = [self._unlink_nodes (dead_node, neighbour) for n in neighbours]
		for n, b in zip (neighbours, branches):
			if (n is not new_neighbour):
				self._link (new_neighbour, b, n)

	def add_nodes_from (self, nested_seq, node_props_fn=None, dist_fn=None, branch_props_fn=None):
		"""
		Add nodes and branches from a series of nested sequences.
		"""
		# TODO: allow adding for mappings?
		# TODO: allow appending onto pre-existing nodes? Needs a start-point.
		# TODO: allow functions as non-callables (constants) and wrap?
		## Preconditions & preparations:
		if (node_props_fn is None):
			node_props_fn = lambda x: None
		if (dist_fn is None):
			dist_fn = lambda x: None
		if (branch_props_fn is None):
			branch_props_fn = lambda x: None
		## Main:
		initial_node = add_first_node (node_props_fn (nested_seq))
		for child in nested_seq:
			self._add_nodes_from_seq (initial_node, child, node_props_fn,
				dist_fn, branch_props_fn)

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
