#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various base classes for later IO implementation

This package does not actually provide any IO functionality, just base classes
for a consistent interface.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from dialect import *
from baseio import *


### TEST & DEBUG ###

def _doctest ():
   import doctest
   doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
   _doctest()


### END ########################################################################
