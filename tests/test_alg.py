#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'phylore.core.tree.alg', using nose.

"""


### IMPORTS ###

import phylo.core.tree.alg as alg

import phylo.core.tree.triters as triters


## CONSTANTS & DEFINES ###

### TESTS ###

class TestAlg (object):

	def setup(self):
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

	
	def test_mrca (self):
		# find mrca of single tip node, i.e. self
		g_node  = triters.find_node (self.tree, lambda x: x.title == 'G')
		m = alg.mrca (self.tree, [g_node])
		assert (m == g_node), "MRCA of single internal node should be self"

		# find mrca of single internal node, i.e. self
		c_node  = triters.find_node (self.tree, lambda x: x.title == 'C')
		m = alg.mrca (self.tree, [c_node])
		assert (m == c_node), "MRCA of single internal node should be self"

		# find mrca in simple case
		f_node  = triters.find_node (self.tree, lambda x: x.title == 'F')
		m = alg.mrca (self.tree, [f_node, g_node])
		assert (m == c_node), "MRCA should be 'C', not '%s'" % m

		# find mrca in more complex case 
		d_node  = triters.find_node (self.tree, lambda x: x.title == 'D')
		m = alg.mrca (self.tree, [d_node, f_node, g_node])
		assert (m == self.tree.root), "MRCA should be the root, not '%s'" % m

		# just check order
		m = alg.mrca (self.tree, [f_node, g_node, d_node])
		assert (m == self.tree.root), "MRCA should be the root, not '%s'" % m

	def test_is_monophyletic (self):
		# for a single 

	def teardown(self):
		pass



