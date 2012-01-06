#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A simple class for holding I/O options.

This is a bit of syntactic sugar to aid readability. In the case of I/O classes
or functions, some cases may have a wide variety of options and possible
behaviours. For example::

   write_newick_tree (t, inc_branch_lens=True, inc_support_vals=False,
      inc_root_len=False, use_translation_table=True, quote_names=True,
      format_support_vals='%.2f', insert_line_breaks=True, ...)

This leads to a large number of arguments with accompanying scope for error. In
addition, many of these options are used in sets. For example options allowable
in Nexus files, options allowable in MrBayes, options that keep all information
in a tree ...

A dialect therefore is a way of grouping and passing options for I/O. Largely it
functions as a dictionary, with the added ability to define default values that
can be overridden explicitly. In practice, dialects should be used like this::

	# define a dialect with default values
	class FooDialect (Dialect):
	   defaults = {
	      'support_format': '%.2f',
	      'include_support': True,
	      'quote_all_names': False,
	   }
	
	class FooWriter (BaseWriter):
	
		def __init__ (self, dialect={}):
			# IO class has default dialect
			# This can be overridden in instances
			d = FooDialect().merge (dialect)
			BasePhyloWriter.__init__ (self, d)
			

One weakness of this approach is that mis-spelt dialect options (e.g.
"quote_nmaes") won't be picked up. 

"""

# TODO: modify dialect so you can't merge options that don't exist? So as to
# prevent the mispelling problem. 

__docformat__ = 'restructuredtext en'



### IMPORTS ###

__all__ = [
   'Dialect',
]


### CONSTANTS & DEFINES ###

ALLOWED = True
FORBIDDEN = False


### IMPLEMENTATION ###

class Dialect (dict):
   """
   A class for collecting reader/writer options.

   There's no real need for this class, other than just to aid readability.
   """
   defaults = {}
   def __init__ (self, *args, **kwargs):
      default_options = self.defaults.copy()
      new_options = dict (*args, **kwargs)
      default_options.update (new_options)
      dict.__init__ (self, default_options)
      self._validate()
      #self['singletons'] = ALLOWED

   def _validate (self):
      pass




### TEST & DEBUG ###

def _doctest ():
   import doctest
   doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
   _doctest()


### END ########################################################################
