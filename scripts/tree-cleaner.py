#!/usr/bin/env python

"""
Given a tree, clean up or normalize the formatting in various ways.

This script requires the following Python libraries:

* BioPython
* phylo.core
* phylo.io.newick

"""

### IMPORTS

import argparse
import sys
import re

from phylo.newick import NewickReader, NewickWriter


### CONSTANTS & DEFINES


### IMPLEMENTATION ###

### UI
# Just some simple functions for consistent handling of messages to the user.
# TODO: redirect these to stderr
 
def progress_msg (s):
	msg ('%s ...' % s)
	
def msg (s):
	print ('%s' % s)
	

### MAIN ###

def main_regex (opts):
	print "in main regex"
	rdr = NewickReader ({'node_annotations': True})
	in_tree = rdr.read (opts.in_tree_path)
	match_regex = re.compile (opts.match_pat)
	for t in in_tree.iter_tip_nodes():
		t.title = match_regex.sub (opts.replace_pat, t.title)
	wrtr = NewickWriter ()
	wrtr._dist_format = opts.distance_format[0]
	wrtr.write (in_tree, opts.out_tree_path)			

	
def parse_args (arg_list):
	"""
	Parse and check command-line arguments.
	
	Args:
		arg_list (iterable): the commandline arguments
		
	Returns:
		a structure of the parsed arguments
		
	This uses argparse and so can (and does) use positional arguments.	
	
	"""
	parser = argparse.ArgumentParser (
		description='Normalize, clean or transform tree representation',
	)
	subparsers = parser.add_subparsers (
		title='subcommands',
		description='valid subcommands',
	)
	
	regex_parser = subparsers.add_parser('rename-by-regex',
	#	aliases=['regex', 're']
	)
	regex_parser.set_defaults(func=main_regex)
	regex_parser.add_argument ('--distance-format', '-d',
		nargs=1,
		default=['%.4g'],
		metavar='FORMAT', 
		help='how to format distances in the output tree, using C/Python formatting characters'
	)
	regex_parser.add_argument ('match_pat',
		metavar='MATCH_PATTERN', 
		help='the pattern to search for in taxa names'
	)
	regex_parser.add_argument ('replace_pat',
		metavar='REPLACE_PATTERN', 
		help='the pattern to replace taxa names'
	)	
	regex_parser.add_argument ('in_tree_path',
		metavar='INPUT_TREE_FILE', 
		type=argparse.FileType('r'),
		help='a file containing a phylogeny in Newick format'
	)
	regex_parser.add_argument ('out_tree_path',
		metavar='OUTPUT_TREE_FILE', 
		type=argparse.FileType('w'),
		help='a file containing the results of the renaming in Newick format'
	)		

	args = parser.parse_args()
	return args


if __name__ == '__main__':
	options = parse_args (sys.argv)
	# call the appropriate function for the subcommand
	print options
	options.func (options)
	sys.exit(0)


### END #######################################################################
