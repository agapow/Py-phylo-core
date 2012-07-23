#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'phylore.core.tree.alg', using nose.

"""


### IMPORTS ###

import phylo.core.tree.alg as alg


## CONSTANTS & DEFINES ###

### TESTS ###

class TestAlg (object):

	def setup(self):
		from phylo.core.tree import *
		t = Tree()
		a = t.add_first_node ({'title': 'A'})
		b, br = t.add_node (a, {'title': 'B'})
		c, br = t.add_node (a, {'title': 'C'})
		d, br = t.add_node (b, {'title': 'D'})
		e, br = t.add_node (b, {'title': 'E'})
		f, br = t.add_node (c, {'title': 'F'})
		g, br = t.add_node (c, {'title': 'G'})

	
	def test_mrca (self):
		assert (False)
	
	def teardown(self):
		pass



