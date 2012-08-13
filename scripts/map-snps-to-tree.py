#!/usr/bin/env python

"""
Given a tree and an alignment, label internal nodes with the snps unique to that subtree.

This script requires the following Python libraries:

* BioPython
* phylo.core
* phylo.io.newick

"""

### IMPORTS

import argparse
import sys
import itertools

from Bio import AlignIO

from phylo.nexus import NewickReader


### CONSTANTS & DEFINES


### IMPLEMENTATION ###

def progress_msg (s):
	print ('%s ...' % s)


def assign_snps (aln):
	"""
	Which columns of an alignment are heterogenous and what is there?
	
	Args:
		aln: a BioPython multiple alignment
		
	Returns:
		the sites with snps, and the variants and associated taxa names. This is rendered
		as a dict with locations as the keys. The values are dicts themselves, with
		allele states as the keys and a list of taxa names as the value.
	
	"""
	# find out which cols are diverse, building a hash of locations vs chars
	# not the most efficient way to do this, but it's a handy preliminary step
	snp_cols = {}
	col_cnt = len (aln[0])
	for i in range (col_cnt):
		col = aln[:,i]
		char_set = set (list (col))
		char_set.discard ('-')
		if 1 < len (char_set):
			snp_cols[i] = char_set
	progress_msg ("%s SNP sites found" % len (snp_cols))
	
	# now make a hash of every SNP and the corresponding taxa within
	seq_cnt = len (aln)
	seq_names = [sr.id for sr in aln]
	snp_distrib = {}

	for k, v in snp_cols.iteritems():
		snp_members = {}
		for c in v:
			snp_members[c] = []
		for i in range (seq_cnt):
			residue = aln[i,k]
			snp_members[residue].append (seq_names[i])
		snp_distrib[k] = snp_members

	return snp_distrib


def map_tip_names_to_nodes (tree):
	# map node names to nodes for convenience
	names_to_nodes = {}
	iterable = tree.iter_nodes()
	for t in itertools.ifilter (lambda n: tree.is_node_tip (n), iterable):
		names_to_nodes[t.title] = t
	return names_to_nodes


def generate_node_names (tree):
	nodes_to_names = {}
	for n in tree.iter_nodes_postorder():
		if (tree.is_node_tip (n)):
			nodes_to_names[n] = n.title
		else:
			# for internal nodes, make a name from the first part of the first child's
			# and last part of the last childs name
			children = tree.node_children (n)
			assert (2 <= len (children)), "detected a singleton node"
			child_names = [nodes_to_names[m] for m in (children[0], children[-1])]
			new_name = "%s/%s" % (
				child_names[0].split('/')[0],
				child_names[1].split('/')[-1],
			)
			nodes_to_names[n] = new_name
	return nodes_to_names



def sort_snps (tree, snp_dict, ignore_majority=False):
	"""
	Maps the snps onto the tree, highlighting the interesting ones.
	
	Args:
		tree (Tree): a phylo.core phylogeny
		snp_dict (dict): a dict of location - alleles, where alleles are a dict of a
			value at that location and a list of the tip names with that value. See
			assign_snps for details.
		ignore_majority (bool): don't report the most prevalent SNP in a column. This
			is useful since the most prevalent is usually the ancestral and hence
			uninteresting.
	
	For brevity, we don't bother to report snps that exist solely on tips.
	
	""" 
	# TODO: need a tip reporting function?
	# store results as [aln_col, residue, node]
	results = []

	# map node names to nodes for convenience
	names_to_nodes = map_tip_names_to_nodes (tree)
		
	# give the inner nodes names
	nodes_to_names = generate_node_names (tree)
			
	# for every alignment column ...
	for locn, var_dict in snp_dict.iteritems():
		# XXX: would be easier if I produced an appropriate data structure in the
		# previous step, but it works and I ain't gonna change it.
		
		# if we're ignoring the majority, set the majority state to None
		if ignore_majority:
			# find the majority state
			max_state = None
			max_freq = 0
			for state, node_names in var_dict.iteritems():
				if (max_freq < len(node_names)):
					max_freq = len(node_names)
					max_state = state
			# now set it to None
			max_names = var_dict[max_state]
			del var_dict[max_state]
			var_dict[None] = max_names
		
		
		# list of nodes and what is monophyletic where, fill with tip data
		states_at_nodes = {}
		for state, node_names in var_dict.iteritems():
			for n in node_names:
				node = names_to_nodes[n]
				states_at_nodes[node] = state

				
		# now traverse tree and inherit state from below
		for n in tree.iter_nodes_postorder():
			if (not tree.is_node_tip (n)):
				child_states = set ([states_at_nodes[c] for c in tree.node_children (n)])
				if None in child_states:
					states_at_nodes[n] = None
				elif (1 < len (child_states)):
					states_at_nodes[n] = None
				else:
					states_at_nodes[n] = list (child_states)[0]
					for c in tree.node_children (n):
						states_at_nodes[c] = None
					
		# record results
		for n, s in states_at_nodes.iteritems():
			# only report internals
			if (tree.is_node_internal (n) and s):
				results.append ([locn, s, nodes_to_names[n]])
				
	## Postconditions & return:
	return results

def text_report (results):
	def print_rec (x):
		print ("- %s%s: %s" % tuple(x))

	print ("SNP monophyley at internal nodes found in %s cases:" % len(results))
	for r in sorted (results, cmp=lambda a, b: cmp (int(a[0]), int(b[0]))):
		print_rec (r)


### MAIN ###

def parse_aln (hndl):
	"""
	Reads and parses an alignment.
	
	Args:
		hndl: a handle opening for reading, containing a Fasta alignment
		
	Returns:
		a BioPython multiple alignment object
		
	"""
	return AlignIO.read (hndl, 'fasta')


def parse_tree (hndl):
	"""
	Reads and parses a phylogeny.
	
	Args:
		hndl: handle open for reading, containing a Newick-formatted tree
		
	Returns:
		a phylo.core Tree
	
	"""
	rdr = NewickReader ({'node_annotations': True})
	return rdr.read (hndl)


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
		description='Map characteristic SNPs to a subtree within a phylogeny',
		epilog='''Taking an alignment and a phylogeny of that alignment, this script
			locates the origin of those SNPs within the phylogeny as the most recent
			common ancestor of the different SNP states. (Of course, this is only a
			parsimonious and perhaps simplistic location - more accurate mapping could
			be done with ancestral state reconstruction.) 
			A literal interpretation of this algorithm would lead to a lot of output
			with little meaning, so the information is reduced in two ways:
			1. SNPs that map only to tips are not reported.
			2. The -i option will ignore the most common state in a column, which will
			   often be the ancestral state at the root.
			'''
	)
	parser.add_argument ('-i', '--ignore-majority', action='store_true',
		help='ignore the most common allele in a column')
	parser.add_argument ('tree_hndl', metavar='TREE_FILE', type=argparse.FileType('r'),
		help='a file containing a phylogeny in Newick format')
	parser.add_argument ('aln_hndl', metavar='ALN_FILE', type=argparse.FileType('r'),
		help='a file containing an alignment in Fasta format')
	args = parser.parse_args()
	return args


def test():
	"""
	Some code to walk the script through its paces.
	"""
	# make a tree
	from phylo.core.tree import Tree
	t = Tree()
	r = t.add_root ({'title': 'root'})
	nabcd, b = t.add_node (r, {'title': 'ABCD'})
	nef, b = t.add_node (r, {'title': 'EF'})
	nab, b = t.add_node (nabcd, {'title': 'AB'})
	ncd, b = t.add_node (nabcd, {'title': 'CD'})
	na, b = t.add_node (nab, {'title': 'A'})
	nb, b = t.add_node (nab, {'title': 'B'})
	nc, b = t.add_node (ncd, {'title': 'C'})
	nd, b = t.add_node (ncd, {'title': 'D'})
	ne, b = t.add_node (nef, {'title': 'E'})
	nf, b = t.add_node (nef, {'title': 'F'})
	
	from Bio.SeqRecord import SeqRecord
	from Bio.Seq import Seq
	from Bio.Align import MultipleSeqAlignment
	seqdata = [
		['A', 'XYGT'],
		['B', 'AYGT'],
		['C', 'ACGT'],
		['D', 'ACGT'],
		['E', 'ACGT'],
		['F', 'ACGT'],
	]
	srs = [SeqRecord (Seq (x[1]), id=x[0], name=x[0]) for x in seqdata]
	aln = MultipleSeqAlignment (srs)
	
	return t, aln
	
	
def main (options):
	"""
	Do the main work of script.
	
	Args:
		options: an argparse structure with program options
		
	"""
	progress_msg ("Reading tree from: %s" % options.tree_hndl)
	progress_msg ("Reading alignment from: %s" % options.aln_hndl)
	progress_msg ("Ignoring the majority allele in column: %s" % options.ignore_majority)
			
	# read in the data
	aln = parse_aln (options.aln_hndl)
	progress_msg ("The alignment has %s sequences" % len (aln))
	tree = parse_tree (options.tree_hndl)
	progress_msg ("The tree has %s nodes" % len (tree))
	
	# digest down to variant loci and snps therein
	snp_map = assign_snps (aln)
	var_cnt = sum ([len(k) for k in snp_map.values()])
	progress_msg ("%s variants have been found" % var_cnt)
	
	# deduce which tip variants map to which internal nodes
	results = sort_snps (tree, snp_map, ignore_majority=options.ignore_majority)
	text_report (results)


if __name__ == '__main__':
	options = parse_args (sys.argv)
	main (options)


### END #######################################################################
