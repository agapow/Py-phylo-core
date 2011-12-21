#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A class for branch on phylogenetic trees.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from phylo.core.impl.propertylist import PropertyList

__all__ = [
	'Branch',
]


### IMPLEMENTATION ###

class Branch (PropertyList):
	"""
	A branch in a phylogeny.

	This serves to contain branch properties and annotations. The actual
	topology (nodes the branch connects) are maintained by the tree class,
	with this as a key. Thus, branches may be shared between trees, and 
	seperate implementations for rooted and unrooted trees aren't needed.

	"""
	# NOTE: little functionality currently needed, but may be required later.
	def __init__ (self, *args, **kwargs):
		PropertyList.__init__ (self, *args, **kwargs)

	def distance (self, default=None):
		return self.get ('distance', default)



### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
