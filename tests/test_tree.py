#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'phylore.core.tree.tree', using nose.

"""


### IMPORTS ###

from phylo.core.tree import Tree


## CONSTANTS & DEFINES ###

### TESTS ###

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
		


### END ####################################################################