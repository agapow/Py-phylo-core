#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A class for nodes within phylogenetic trees.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from phylo.core.impl.propertylist import PropertyList

__all__ = [
	'Node',
]


### IMPLEMENTATION ###

class Node (PropertyList):
	"""
	A node in a phylogeny.

	This serves to contain node properties and annotations. The actual topology
	(connections between nodes) are maintained by the tree class, with this as
	a key. Thus, nodeas may be shared between trees, and seperate
	implementations for rooted and unrooted trees aren't needed.

	"""
	# NOTE: little functionality currently needed, but may be required later.
	def __init__ (self, *args, **kwargs):
		PropertyList.__init__ (self, *args, **kwargs)



### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
