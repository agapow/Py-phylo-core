#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A simple dict-like object for storing properties.

In phylotree, nodes and branches are basically lists of key-values (topology
is stored in the tree proper). This class thus serves as a useful base for
those.

"""
# TODO: restrict keys to strings


__docformat__ = 'restructuredtext en'


### IMPORTS ###

__all__ = [
	'PropertyList',
]


### IMPLEMENTATION ###

class PropertyList (object):
	"""
	A simple key-value list, realised as a Python dictionary.

	This has little to offer over a standard dictionary, except to restrict key
	types to strings, and being able to be used as a key itself in
	dictionaries. These traits are useful for the phylogeny internal
	implementation. Note that not all of the dictionary interface has been
	implemented.

	For example::

		>>> p = PropertyList()
		>>> p['foo'] = 'bar'
		>>> p['foo']
		'bar'
		>>> p['baz'] = 3
		>>> p[3] = 'baz'
		Traceback (most recent call last):
		...
		AssertionError: only string keys (not '<type 'int'>') allowed in property lists
		>>> d = {}
		>>> d[p] = 3
		>>> d[p]
		3

	"""
	# NOTE: why not use a dictionary itself? Because dictionaries are mutable
	# and we need to use the node/branch propertylist as a key inside a tree
	# NOTE: we cannot sublcass dict directly, as this prevents the propertylist
	# from being used as a key.
	
	## LIFECYCLE:
	def __init__ (self, *args, **kwargs):
		"""
		Construct a mapping of key-value pairs.
		
		Note that the restriction on string-only keys in not currently enforced
		in this constructor.
		
		For example::
		
			>>> p1 = PropertyList({'foo': 1, 'bar': 2})
			>>> p1['foo'] == 1
			True
			>>> p2 = PropertyList(foo=1, bar=2)
			>>> p2['foo'] == 1
			True
			
		"""
		self._props = dict (*args, **kwargs)

	## ACCESSORS:
	def __getitem__ (self, key):
		return self._props[key]

	def get (self, key, default=None):
		return self._props.get (key, default)
		
	def has_key (self, key):
		return key in self
		
	def __contains__ (self, key):
		return key in self._props

	def items (self):
		return self._props.items()
			
	def keys (self):
		return self._props.keys()
		
	def values (self):
		return self._props.values()

	def __repr__ (self):
		return '%s (%s)' % (self.__class__.__name__, str (self._props))

	## MUTATORS:
	def __setitem__ (self, key, value):
		assert (isinstance (key, basestring)), \
			"only string keys (not '%s') allowed in property lists" % type (key)
		self._props[key] = value

	def __delitem__ (self, key):
		del self._props[key]
		
	def clear (self):
		self._props.clear()



### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
