#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A class for tracing paths of nodes within phylogenetic trees.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

__all__ = [
	'Path',
]


### IMPLEMENTATION ###

class Path (object):
	"""
	A node in a phylogeny.

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
