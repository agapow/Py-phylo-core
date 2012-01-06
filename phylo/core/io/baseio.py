#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base classes for writing and reading trees.

This package does not actually provide any IO functionality, just base classes
for a consistent interface.

"""
# TODO: can we allow for writing multiple trees?
# TODO: and iterating over output trees.

__docformat__ = 'restructuredtext en'



### IMPORTS ###

from exceptions import NotImplementedError
import cStringIO

from dialect import Dialect

__all__ = [
	'BaseReader',
	'BaseWriter',
]


### IMPLEMENTATION ###

class BaseIO (object):
	"""
	An abstract base class for phylogeny I/O operations.

	This has little actual functionality, other than ensuring that dialects
	are set correctly and can be accessed easily.

	"""
	def __init__ (self, dialect=None):
		"""
		C'tor for the class.

		:Params:
			dialect Dialect or dict
				A set of properties for IO behaviour.

		"""
		if (dialect is None):
			dialect = Dialect()
		if (not isinstance (dialect, Dialect)):
			dialect = Dialect (dialect)
		self.dialect = dialect

	def get_dialect (prop, default=None):
		"""
		Get an IO dialect property.

		Similar to (and uses) the dictionary 'get' method.

		:Params:
			prop string
				The property name.
			default
				The value to return if the property is not set.

		:Returns:
			The property value (or default value).

		"""
		return self.dialect.get (prop, default)

	def set_dialect (prop, value):
		"""
		Set an IO dialect property.

		Similar to (and uses) the dictionary 'set' method.

		:Params:
			prop string
				The property name.
			value
				The value to set the property to.

		"""
		return self.dialect.set (prop, value)

	def has_dialect (prop):
		"""
		Check for the existence of an IO dialect property.

		Similar to (and uses) the dictionary 'has_key' method.

		:Params:
			prop string
				The property name.

		:Returns:
			A boolean for existence.

		"""
		return self.dialect.has_key (prop)


class BaseReader (BaseIO):
	"""
	Am abstract base class for phylogeny readers.

	This just serves as an interface and pools some common functionality.
	"""
	# TODO: next an iter over trees function

	def __init__ (self, dialect=None):
		BaseIO.__init__ (self, dialect)

	def read (self, src):
		"""
		Read a tree from a stream or file.

		This just performs a bit of house keeping and hands off to ``_read``
		to do the actual work.

		:Params:
			in
				This can be an open file, file-like object or the path to a
				file.

		:Returns:
			A phylotree.

		"""
		if (not hasattr (src, 'read')):
			src = open (src, 'r')
		return self._read (src)

	def _read (self, src):
		"""

		This is where the actual work is done. Subclasses must override this
		method.

		:Params:
			in
				An open file or file-like object.

		:Returns:
			A phylotree.

		"""
		raise NotImplementedError ('must override method in subclass')

	def read_from_string (self, str):
		buf = cStringIO.StringIO (str)
		return self.read (buf)


class BaseWriter (BaseIO):
	"""
	Am abstract base class for phylogeny writers.

	This just serves as an interface and pools some common functionality.
	"""
	def __init__ (self, dialect=None):
		BaseIO.__init__ (self, dialect)

	def write (self, tree, dest):
		"""
		Write the tree to the stream or file.

		This just performs a bit of house keeping and hands off to ``_write``
		to do the actual work.

		:Params:
			out
				This can be an open file, file-like object or the path to a
				file.

		"""
		if (not hasattr (dest, 'write')):
			dest = open (dest, 'w')
		return self._write (tree, dest)

	def _write (self, tree, dest):
		"""

		This is where the actual work is done. Subclasses must override this
		method.

		:Params:
			tree
				A rooted or unrooted phylogeny.
			out
				An open file or file-like object.

		"""
		raise NotImplementedError ('must override method in subclass')

	def write_to_string (self, tree):
		buf = cStringIO.StringIO()
		self.write (tree, buf)
		return buf.getvalue()


### TEST & DEBUG ###

def _doctest ():
   import doctest
   doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
   _doctest()


### END ########################################################################
