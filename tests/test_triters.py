#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'phylore.core.tree.triters', using nose.

"""


### IMPORTS ###

import phylo.core.triters as triters


## CONSTANTS & DEFINES ###

### TESTS ###

class TestTritersFind (object):

	def setup(self):
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
		self.tree = t

	
	def test_find_node (self):
		n = triters.find_node (self.tree, lambda x: x.title == 'B')	
		assert n.title == 'B', "should only find matched node not '%s'" % n 
		n = triters.find_node (self.tree, lambda x: x.title == 'Z')	
		assert (n == None), "should find None not '%s'" % n
	
	def test_find_all_nodes (self):
		ns = triters.find_all_nodes (self.tree, lambda x: x.title in ['B', 'C'])	
		for n in ns:
			assert (n.title in ['B', 'C']), \
				"should only find matched nodes not '%s'" % n
		ns = triters.find_all_nodes (self.tree, lambda x: x.title == 'Z')	
		assert (ns == []), "should return empty list not '%s'" % ns
	
	def test_iter_nodes (self):
		for n in triters.iter_find_nodes (self.tree, lambda x: x.title in ['B', 'C']):
			assert (n.title in ['B', 'C']), \
				"should only find matched nodes not '%s'" % n
		for n in triters.iter_find_nodes (self.tree, lambda x: x.title == 'Z'):
			assert (False),  "should find no nodes not '%s'" % n

	def test_iter_nodes_to_root (self):
		start = triters.find_node (self.tree, lambda x: x.title == 'D')
		n_path = [n for n in triters.iter_nodes_to_root (self.tree, start)]
		n_titles = [x.title for x in n_path]
		assert (n_titles == ['D', 'B', 'A']), \
			"expected nodes D-B-A, actually got '%s'" % n_titles
	
	def teardown(self):
		pass



