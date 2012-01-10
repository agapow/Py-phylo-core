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
	a key. Thus, nodes may be shared between trees, and separate
	implementations for rooted and unrooted trees aren't needed.

	"""
	# NOTE: little functionality currently needed, but may be required later.
	def __init__ (self, *args, **kwargs):
		PropertyList.__init__ (self, *args, **kwargs)

	def name (self, default=None):
		"""
		Returns the name or title of the node.
		
		For example::
		
			>>> n = Node()
			>>> n.name() == None
			True
			>>> n.name ('no name') == 'no name'
			True
			>>> n['name'] = 'foo'
			>>> n.name() == 'foo'
			True
		
		"""
		return self.get ('name', default)

### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
