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

	def get_title (self, default=None):
		"""
		Returns the name or title of the node.
		
		For example::
		
			>>> n = Node()
			>>> n.title == None
			True
			>>> n.title = 'no title'
			>>> n.title == 'no title'
			True
			>>> n['title'] = 'foo'
			>>> n.title == 'foo'
			True
		
		"""
		return self.get ('title', default)
	
	def set_title (self, val):
		self['title'] = val
	
	title = property (get_title, set_title)
	name = title
	
	

### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
