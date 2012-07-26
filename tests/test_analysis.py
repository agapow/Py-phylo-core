#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'phylore.core.tree.alg', using nose.

"""


### IMPORTS ###

import phylo.core.analysis as alg

import phylo.core.triters as triters


## CONSTANTS & DEFINES ###

### TESTS ###

class TestAlg (object):

	def setup(self):
		# make up a dummy tree to test upon
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
		# record the nodes for later convenience
		self.nodes = dict ([(n.title, n) for n in t.nodes()])

	
	def test_mrca (self):
		# find mrca of single tip node, i.e. self
		g_node = self.nodes['G']
		m = alg.mrca (self.tree, [g_node])
		assert (m == g_node), "MRCA of single internal node should be self"

		# find mrca of single internal node, i.e. self
		c_node = self.nodes['C']
		m = alg.mrca (self.tree, [c_node])
		assert (m == c_node), "MRCA of single internal node should be self"

		# find mrca in simple case
		f_node = self.nodes['F']
		m = alg.mrca (self.tree, [f_node, g_node])
		assert (m == c_node), "MRCA should be 'C', not '%s'" % m

		# find mrca in more complex case 
		d_node = self.nodes['D'] 
		m = alg.mrca (self.tree, [d_node, f_node, g_node])
		assert (m == self.tree.root), "MRCA should be the root, not '%s'" % m

		# just check order
		m = alg.mrca (self.tree, [f_node, g_node, d_node])
		assert (m == self.tree.root), "MRCA should be the root, not '%s'" % m


	def test_is_monophyletic (self):
		# for a single tip, by definition true
		g_node = self.nodes['G']
		assert (alg.is_monophyletic (self.tree, [g_node])), "single tip should be monophyletic"

		# for a single internal node, answer is false
		c_node = self.nodes['C']
		assert (not alg.is_monophyletic (self.tree, [c_node])), "single internal should not be monophyletic"

		# for all sibling tips, answer is true
		f_node = self.nodes['F']
		assert (alg.is_monophyletic (self.tree, [f_node, g_node])), "set of sibling tips should be monophyletic"

		# for all in a subtree , answer is true
		c_node = self.nodes['C']
		assert (alg.is_monophyletic (self.tree, [c_node, f_node, g_node])), "all in subtree should be monophyletic"

	def teardown(self):
		pass



