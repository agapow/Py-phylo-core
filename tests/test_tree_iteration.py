#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'phylore.core.tree.tree_iteration_mixin', using nose.

"""


### IMPORTS ###

from phylo.core.tree import Tree


## CONSTANTS & DEFINES ###

### TESTS ###

class TestIterationFind (object):

	def setup(self):
		# create a test tree
		t = Tree()
		a = t.add_root ({'title': 'A'})
		b, br = t.add_node (a, {'title': 'B'})
		c, br = t.add_node (a, {'title': 'C'})
		d, br = t.add_node (b, {'title': 'D'})
		e, br = t.add_node (b, {'title': 'E'})
		f, br = t.add_node (c, {'title': 'F'})
		g, br = t.add_node (c, {'title': 'G'})
		self.tree = t

	
	def test_find_node (self):
		n = self.tree.find_node (lambda x: x.title == 'B')	
		assert n.title == 'B', "should only find matched node not '%s'" % n 
		n = self.tree.find_node (lambda x: x.title == 'Z')	
		assert (n == None), "should find None not '%s'" % n
	
	def test_find_all_nodes (self):
		ns = self.tree.find_all_nodes (lambda x: x.title in ['B', 'C'])	
		for n in ns:
			assert (n.title in ['B', 'C']), \
				"should only find matched nodes not '%s'" % n
		ns = self.tree.find_all_nodes (lambda x: x.title == 'Z')	
		assert (ns == []), "should return empty list not '%s'" % ns
	
	def test_iter_nodes (self):
		for n in self.tree.iter_find_nodes (lambda x: x.title in ['B', 'C']):
			assert (n.title in ['B', 'C']), \
				"should only find matched nodes not '%s'" % n
		for n in self.tree.iter_find_nodes (lambda x: x.title == 'Z'):
			assert (False),  "should find no nodes not '%s'" % n

	def test_iter_nodes_to_root (self):
		start = self.tree.find_node (lambda x: x.title == 'D')
		n_path = [n for n in self.tree.iter_nodes_to_root (start)]
		n_titles = [x.title for x in n_path]
		assert (n_titles == ['D', 'B', 'A']), \
			"expected nodes D-B-A, actually got '%s'" % n_titles
	
	def teardown(self):
		pass


class TestTreeIteration (object):
	def setup (self):
		"""
		Build a tree that starts from root, radiates to ABC and DE and thence to AB (and
		A & B) and D and E.
		
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
		
	def teardown (self):
		pass
		
	def test_postorder (self):
		path = ['A', 'B', 'AB', 'C', 'ABC', 'D', 'E', 'DE', 'root']
		actual_path = [n.title for n in self.tree.iter_nodes_postorder()]
		assert (path == actual_path)
			
	def test_preorder (self):
		path = ['root', 'ABC', 'AB', 'A', 'B', 'C', 'DE', 'D', 'E']
		actual_path = [n.title for n in self.tree.iter_nodes_preorder()]
		assert (path == actual_path)
