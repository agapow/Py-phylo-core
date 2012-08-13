#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'phylore.core.tree.tree', using nose.

"""


### IMPORTS ###

from phylo.core.tree import Tree


## CONSTANTS & DEFINES ###

### TESTS ###

def are_lists_equal (l1, l2):
	return (sorted(l1) == sorted(l2))
	

class TestTreeTraversal (object):
	def setup (self):
		"""
		Build a tree that starts from root, radiates to AB, CD. EF and then
		A to F. 
		"""
		t = Tree()
		r = t.add_root ({'title': 'root'})
		nab, b = t.add_node (r, {'title': 'AB'}, branch_props={'title': 'root-AB', 'distance': 1.0})
		na, b = t.add_node (nab, {'title': 'A'}, branch_props={'title': 'A-AB', 'distance': 1.1})
		nb, b = t.add_node (nab, {'title': 'B'}, branch_props={'title': 'B-AB', 'distance': 1.2})
		ncd, b = t.add_node (r, {'title': 'CD'}, branch_props={'title': 'root-CD', 'distance': 1.3})
		nc, b = t.add_node (ncd, {'title': 'C'}, branch_props={'title': 'C-CD', 'distance': 1.4})
		nd, b = t.add_node (ncd, {'title': 'D'}, branch_props={'title': 'D-CD', 'distance': 1.5})
		nef, b = t.add_node (r, {'title': 'EF'}, branch_props={'title': 'root-EF', 'distance': 1.6})
		ne, b = t.add_node (nef, {'title': 'E'}, branch_props={'title': 'E-EF', 'distance': 1.7})
		nf, b = t.add_node (nef, {'title': 'F'}, branch_props={'title': 'F-EF', 'distance': 1.8})
		self.tree = t
	
	def teardown (self):
		pass
	
#	def test_subtree (self):
#		subtree_nodes = [n for n in self.tree.iter_nodes()
#			if n.title in ['A', 'C', 'E']]
#		st = self.tree.subtree (subtree_nodes)
#		st._validate()
#		assert (len(st) == 7)


class TestNodeAccessors (object):
	def setup (self):
		"""
		Build a tree that starts from root, radiates to AB, CD. EF and then
		A to F. 
		
		Our tree is:
		
		- root
			- ABC
				- AB
					- A
					- B
				- C
			- DE
				- D
				- E
		
		"""
		t = Tree()
		r = t.add_root ({'title': 'root'})
		node_abc, b = t.add_node (r, {'title': 'ABC'})
		node_de, b = t.add_node (r, {'title': 'DE'})
		node_ab, b = t.add_node (node_abc, {'title': 'AB'})
		node_c, b = t.add_node (node_abc, {'title': 'C'})
		node_a, b = t.add_node (node_ab, {'title': 'A'})
		node_b, b = t.add_node (node_ab, {'title': 'B'})
		node_d, b = t.add_node (node_de, {'title': 'D'})
		node_e, b = t.add_node (node_de, {'title': 'E'})
		
		# record for use in test functions
		self.tree = t
		self.nodes = {}
		for n in [r, node_a, node_b, node_c, node_d, node_e, node_ab, node_abc, node_de]:
			self.nodes[n.title] = n
			
		self.solo_tree = Tree()
		self.solo_tree.add_root()
		
	def teardown (self):
		pass
		
	def test_neighbours (self):
		neighbours = [
			['ABC', ['root', 'AB', 'C']],
			['AB', ['ABC', 'A', 'B']],
			['A', ['AB']],
			['B', ['AB']],
			['DE', ['root', 'D', 'E']],
			['D', ['DE']],
			['E', ['DE']],
			['root', ['ABC', 'DE']],
		]
		for r in neighbours:
			n = self.nodes[r[0]]
			names = [ne.title for ne in self.tree.node_neighbours (n)]
			assert are_lists_equal (names, r[1]), "'%s' is not '%s'" % (names, r[1])
			
		# test the odd case of a tree with a single node
		solo_node = self.solo_tree.nodes[0]
		print self.solo_tree.node_neighbours(solo_node)
		assert (self.solo_tree.node_neighbours(solo_node) == [])

		
	def test_children (self):
		children = [
			['ABC', ['AB', 'C']],
			['AB', ['A', 'B']],
			['A', []],
			['B', []],
			['DE', ['D', 'E']],
			['D', []],
			['E', []],
			['root', ['ABC', 'DE']],
		]
		for r in children:
			print "Testing %s ..." % r
			n = self.nodes[r[0]]
			print "Node is %s ..." % n
			names = [ne.title for ne in self.tree.node_children (n)]
			assert are_lists_equal (names, r[1]), "'%s' is not '%s'" % (names, r[1])
			
		# test the odd case of a tree with a single node
		solo_node = self.solo_tree.nodes[0]
		assert (self.solo_tree.node_children(solo_node) == [])
					
	def test_parents (self):
		parents = [
			['ABC', 'root'],
			['AB', 'ABC'],
			['A', 'AB'],
			['B', 'AB'],
			['DE', 'root'],
			['D', 'DE'],
			['E', 'DE'],
			['root', None],
		]
		for r in parents:
			n = self.nodes[r[0]]
			node = self.tree.node_parent (n)
			if node:
				node = node.title
			assert (node == r[1]), "'%s' is not '%s'" % (node, r[1])
					
		# test the odd case of a tree with a single node
		solo_node = self.solo_tree.nodes[0]
		assert (self.solo_tree.node_parent(solo_node) == None)
		
	def test_is_tip (self):
		nodes = [
			['ABC', False],
			['AB', False],
			['A', True],
			['B', True],
			['DE', False],
			['D', True],
			['E', True],
			['root', False],
		]
		for r in nodes:
			assert (self.tree.is_node_tip (self.nodes[r[0]]) == r[1])
			
		# test the odd case of a tree with a single node
		solo_node = self.solo_tree.nodes[0]
		assert (self.solo_tree.is_node_tip(solo_node))
					
	def test_is_internal (self):
		nodes = [
			['ABC', True],
			['AB', True],
			['A', False],
			['B', False],
			['DE', True],
			['D', False],
			['E', False],
			['root', True],
		]
		for r in nodes:
			assert (self.tree.is_node_internal (self.nodes[r[0]]) == r[1])
			
		# test the odd case of a tree with a single node
		solo_node = self.solo_tree.nodes[0]
		assert (self.solo_tree.is_node_internal(solo_node) == False)
		
	def test_is_root (self):
		nodes = [
			['ABC', False],
			['AB', False],
			['A', False],
			['B', False],
			['DE', False],
			['D', False],
			['E', False],
			['root', True],
		]
		for r in nodes:
			assert (self.tree.is_node_root (self.nodes[r[0]]) == r[1])			
			
		# test the odd case of a tree with a single node
		solo_node = self.solo_tree.nodes[0]
		assert (self.solo_tree.is_node_root(solo_node))
							
				


### END ####################################################################