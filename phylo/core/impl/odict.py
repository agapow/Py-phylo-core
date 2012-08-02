#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An ordered dictionary.

Ordered dicts are used in the standard tree to hold topology, so that a
consistent order of branches can be kept and manipulated. A bit hacky but it works. While an ordered dict is available in Python 2.7+, we have existing
software running under 2.6 and Jython, which lack a suitable class. Hence, we
load the official class if available and otherwise drop in a compatiable
alternative.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

__all__ = [
	'Odict',
]

import exceptions

try:
	from collections import OrderedDict as Odict

except exceptions.ImportError:
	from _odict import OrderedDict as Odict

from collections import deque


### IMPLEMENTATION ###

class Odict (dict):
	"""
	A simple ordered dictionary.
	
	This allows keys and their accompanying values to be accessed in a
	consistent order as items are added to a dictionary, rather than an
	indeterminate one based on dictionary internals. By default, items are kept
	in the order they are added. This order may be manipulated and sorted. 
	
	For example::
	
		>>> od = Odict()
		>>> od['c'] = '2'; od['b'] = '1'; od['a'] = '3'
		>>> ''.join (od.keys())
		'cba'
		>>> ''.join (od.ordered_keys())
		'cba'
		>>> od.items()
		[('c', '2'), ('b', '1'), ('a', '3')]
	
	"""
	
	## LIFECYCLE:
	def __init__ (self):
		"""
		C'tor for dictionary.
		
		We don't allow content initialisation in construction, because it
		is difficult to know what ordering due to the problem of ascertaining
		what order those items should be in. (If initialised from a mapping
		or keyword-pairs, the order is essentially arbitrary.)
		
		For example::
		
			>>> od1 = Odict()
			>>> od2 = Odict (a=1, b=2)
			Traceback (most recent call last):
			...
			TypeError: __init__() got an unexpected keyword argument 'a'
			>>> od2 = Odict({'a': 1, 'b': 2})
			Traceback (most recent call last):
			...
			TypeError: __init__() takes exactly 1 argument (2 given)
			
		"""
		# NOTE: can't use a set for the indices as they are unordered
		dict.__init__ (self)
		self._indices = deque()
		
	## ACCESSORS:
	def ordered_keys (self):
		"""
		Return the dictionary keys in order.
		
		For example::
		
			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> od.ordered_keys()
			['c', 'b', 'a']
			
		"""
		return list (self._indices)
	
	keys = ordered_keys
		
	def ordered_values (self):
		"""
		Return the dictionary keys in (key) order.

		For example::
		
			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> od.ordered_values()
			[2, 1, 3]

		"""
		return [self[k] for k in self._indices]
		
	values = ordered_values
	
	def ordered_items (self):
		"""
		Return the dictionary items in order.

		For example::
		
			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> od.ordered_items()
			[('c', 2), ('b', 1), ('a', 3)]

		"""
		return [(k, self[k]) for k in self._indices]
	
	items = ordered_items
	
	def ordered_iterkeys (self):
		"""
		Return an iterator over the dictionary keys in order.

		For example::

			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> [x for x in od.ordered_iterkeys()]
			['c', 'b', 'a']

		"""
		for k in self._indices:
			yield k
	
	iterkeys = ordered_iterkeys
	
	def ordered_itervalues (self):
		"""
		Return an iterator over the dictionary values in order.

		For example::

			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> [x for x in od.ordered_itervalues()]
			[2, 1, 3]

		"""
		for k in self._indices:
			yield self[k]
	
	itervalues = ordered_itervalues
	
	def ordered_iteritems (self):
		"""
		Return an iterator over the dictionary items in order.
		
		For example::
		
			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> [x for x in od.ordered_iteritems()]
			[('c', 2), ('b', 1), ('a', 3)]

		"""
		for k in self._indices:
			yield (k, self[k])
	
	iteritems = ordered_iteritems
	
	## MUTATORS::
	def __setitem__ (self, key, value):
		"""
		Set or update the value of an item in the dictionary.
		
		This also updates the item order if need be.
		
		For example::
		
			>>> od = Odict()
			>>> od['c'] = 2
			>>> od.ordered_keys()
			['c']
			>>> od['b'] = 1
			>>> od.ordered_keys()
			['c', 'b']
			>>> od['a'] = 3
			>>> od.ordered_keys()
			['c', 'b', 'a']
		
		"""
		dict.__setitem__ (self, key, value)
		if (key not in self._indices):
			self._indices.append (key)

	def __delitem__ (self, key):
		"""
		Delete an item in the dictionary.
		
		This also removes the item from the order.
		
		For example::
		
			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> od.ordered_keys()
			['c', 'b', 'a']
			>>> del od['c']
			>>> od.ordered_keys()
			['b', 'a']
			>>> del od['a']
			>>> od.ordered_keys()
			['b']
			
		"""
		dict.__delitem__ (self, key)
		self._indices.remove (key)
		
	def order_by_keys (self, keys):
		"""
		Change the order of keys (and thus items).
		
		The items are reordered, according to the order of the keys passed in.
		Note that these keys must have the same number and identity as the old
		keys, just in a (potentially) different order.
		
		For example::
		
			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> od.order_by_keys (['a', 'b', 'c'])
			>>> od.ordered_items()
			[('a', 3), ('b', 1), ('c', 2)]
			>>> od.order_by_keys (['a', 'b', 'c'])
			>>> od.ordered_items()
			[('a', 3), ('b', 1), ('c', 2)]
			>>> od.order_by_keys (['d', 'a', 'b'])
			Traceback (most recent call last):
			...
			AssertionError: new keys are different to old keys
			>>> od.order_by_keys (['b', 'a'])
			Traceback (most recent call last):
			...
			AssertionError: new keys are different to old keys
		
		"""
		# TODO: do I really need this?
		
		## Preconditions:
		new_keys = list (keys)
		assert (sorted (new_keys) == sorted (self._indices)), \
			"new keys are different to old keys"
		## Main:
		self._indices = new_keys
	
	def rotate_order (self, shift=1):
		"""
		Change the ordering by shifting, items from one end moving to the other.
		
		:Parameters:
			shift integer
				Positive shifts move the sequence right, negative to the left.
		
		For example::
		
			>>> od = Odict()
			>>> od['c'] = 2; od['b'] = 1; od['a'] = 3
			>>> od.ordered_keys()
			['c', 'b', 'a']
			>>> od.rotate_order()
			>>> od.ordered_keys()
			['a', 'c', 'b']
			>>> od.rotate_order (-1)
			>>> od.ordered_keys()
			['c', 'b', 'a']
			>>> od.rotate_order (4)
			>>> od.ordered_keys()
			['a', 'c', 'b']
		
		"""
		## Preconditions & preparation:
		#shift = shift % len (self._indices)
		## Main:
		#if shift:
		#	self._indices = self._indices[-shift:] + self._indices[:-shift]
		self._indices.rotate(shift)
		
		
	def popitem (last=True):
		"""
		Remove and return a (key, value) pair. 
		
		The pairs are returned in LIFO order if last is true or FIFO order if
		false.
		"""
		if last:
			k = self._indices.pop()
		else:
			k = self._indices.popLeft()
		return (k, dict.popitem(self, k))

	def move_to_end (self, key, last=True):
		self._indices.remove (key)
		if last:
			self.indices.append(key)
		else:
			self.indices.appendLeft(key)

			

### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
