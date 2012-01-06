#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Metrics that calculate distances across a tree.

"""


__docformat__ = 'restructuredtext en'


### IMPORTS ###

__all__ = [
	'rooted_evol_history',
]


### IMPLEMENTATION ###

def total_distance (tree):
	"""
	Calculate the total distance encompassed by a tree.
	
	This simply iterates over the branches and sums distances.
	"""
	# TODO: addition functor
	return sum ([b['distance'] for b in t.iter_branches()])


def rooted_subtree_history (rtree, nodes, inc_root=True):
	"""
	Calculate evolutionary history a la May-Nee or Faith.
	
	:Parameters:
		rtree
			a rooted tree
		nodes
			a subtree as defined 
	
	EH can only be calculated over a rooted tree since 
	"""
	## Preconditions:
	assert (rtree.is_rooted), \
		"evolutionary history can only be calculated over a rooted tree"
	## Main::
	stree = rtree.copy_rooted_subtree (nodes)
	
	## Postconditions & return:


### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
