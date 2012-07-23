#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'phylore.core.tree.triters', using nose.

"""


### IMPORTS ###

import phylo.core.tree.triters as triters


## CONSTANTS & DEFINES ###

### TESTS ###

class TestTritersFind (object):

	def setup(self):
		# create a test tree
		from phylo.core.tree import Tree
		t = Tree()
		a = t.add_first_node ({'title': 'A'})
		b, br = t.add_node (a, {'title': 'B'})
		c, br = t.add_node (a, {'title': 'C'})
		d, br = t.add_node (b, {'title': 'D'})
		e, br = t.add_node (b, {'title': 'E'})
		f, br = t.add_node (c, {'title': 'F'})
		g, br = t.add_node (c, {'title': 'G'})
		self.tree = t

	
	def test_find_node (self):
		n = triters.find_node (self.tree, lambda x: x.title == 'B')	
		assert n.title == 'B'
	
	def teardown(self):
		pass



