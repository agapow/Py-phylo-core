Introduction
============

phylo.core is a Python package for representing phylogenetic trees. Features
include:






Design & philosophy
===================

phylo.core sprang to life many years ago when I was writing a webservice that
needed to manipulate and display trees. Since then it has mutated, changed name
and occasionally surfaced publicly in a few pieces of software. Its current form
is result of me wanting to clean up the design and better prepare it for reuse
in my own work, and incidentally for others that may find it useful.

* This core package provides *just* the tree. Algorithms, IO, drawing etc. are
  all for other packages. While part of this is just restricting the scope of
  the package, its also allowing for other tree classes with the same API but
  different implementations. These may have their own efficiencies and drawbacks
  in specialised cases (e.g. cTree, jTree, ImmutableTree) but can still be used
  by external algorithms.

* As this is just one tree implementation and with my own needs in mind,
  whenever a choice had to be made between making the tree class easily maleable
  or efficient, the former won out every time.
  
* Following on from this, while early designs of the tree realised it as
  multiple classes, enforcing different topologies (e.g. Rooted, Unrooted), this
  was eventually abandoned. Too many questions and problems arose when types had
  to be converted (e.g. derooting), enforcing validity proved to be too hard,
  especially with different ideas of what entailed a valid tree and when
  mutators required the tree had to pass through an intermediate invalid state.
  For this, and for maximum flexibility, few restrictions are placed on what
  sort of trees are allowed: bifurcating vs polytomous, nodes with a single
  descendant ...

* The flipside of this is that it's entirely possible to use the API to make
  nonsensical trees: orphaning nodes, creating loops, setting negative
  distances. The API won't won't *help* you do this, but it is possible. With
  validity being such a tough problem, we leave it to the user to build a tree
  in whatever way they consider "right".

* Nodes and branches exist almost as just markers, containers for the various
  properties of those points in the tree. This allows all manipulations of those
  tree components to be done in a unified way through the tree.

* It seems likely that this will be used on implementations of Python other than
  CPython (especially JPython) and so no Python features beyond 2.5 are assumed.


Limitations


Alternatives
============

There are a number of good Python phylogenetic libraries out there, some of
which are listed below. Why use phylo.core rather than these? 

* Nodes and branches may be easily labelled with multiple properties.

* Branch length mathematics can be overridden and done in non-additive ways

* A variety of traversal iterators are provided

* No restrictions are placed on topology - bifurcating and polytomous trees are
  allowed

* Trees can be freely rerooted, derooted and rotated - a rooted tree is just
  an unrooted tree with extra information

Otherwise, you could look here:

* DendroPy <http://packages.python.org/DendroPy/>


References
==========

