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

from Bio import AlignIO

from phylo.nexus import NewickReader


### CONSTANTS & DEFINES


### IMPLEMENTATION ###

def progress_msg (s):
	print ('%s ...' % s)


def assign_snps (aln):
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
	progress_msg ("%s SNPs found" % len (snp_cols))
	
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


def sort_snps (tree, snp_dict):
	"""
	Sorts the snps into tips, monophyletic and non-monophyletic.
	
	Args:
		tree (Tree): a phylo.core phylogeny
		snp_dict (dict): a dict of location - alleles, where alleles are a dict of a
			value at that location and a list of the tip names with that value
		
	""" 
	# lists to sort records into
	tips = []
	mono = []
	non_mono = []

	# map node names to nodes
	node_dict = {}
	for t in tree.iter_tips():
		node_dict[t.title] = t

	# do the sorting
	for locn, var_dict in snp_dict.iteritems():
		for res, taxa in var_dict.iteritems():
			record = (locn, res, taxa)
			if len (taxa) == 1:
				tips.append (record)
			else:
				nodes = [node_dict[n] for n in taxa]
				if tree.is_monophyletic (nodes):
					print (record)
					mono.append (record)
				else:
					non_mono.append (record)
					print (record)

	# sort the recs, just for neatness
	tips.sort()
	mono.sort()
	non_mono.sort()

	## Postconditions & return:
	return tips, mono, non_mono

def text_report (tip_snps, mono_snps, non_mono_snps):
	def print_rec (x):
		print ("- %s%s: %s" % x)

	print ("Tips:")
	for r in tip_snps:
		print_rec (r)
	print ("Mono:")
	for r in mono_snps:
		print_rec (r)
	print ("Non-mono:")
	for r in non_mono_snps:
		print_rec (r)

### MAIN ###

def parse_aln (hndl):
	return AlignIO.read (hndl, 'fasta')


def parse_tree (hndl):
	rdr = NewickReader ({'node_annotations': True})
	return rdr.read (hndl)


def parse_args (arg_list):
	parser = argparse.ArgumentParser (
		description='Label subtrees of a phylogeny with characteristic SNPs')
	parser.add_argument ('tree_hndl', metavar='TREE_FILE', type=argparse.FileType('r'),
		help='a file containing a phylogeny in Newick format')
	parser.add_argument ('aln_hndl', metavar='ALN_FILE', type=argparse.FileType('r'),
		help='a file containing an alignment in Fasta format')
	args = parser.parse_args()
	return args


def main (options):
	aln = parse_aln (options.aln_hndl)
	progress_msg ("The alignment has %s sequences" % len (aln))
	tree = parse_tree (options.tree_hndl)
	progress_msg ("The tree has %s nodes" % len (tree))
	snp_map = assign_snps (aln)
	var_cnt = sum ([len(k) for k in snp_map.values()])
	progress_msg ("%s variants have been found" % var_cnt)
	t_snps, m_snps, n_snps = sort_snps (tree, snp_map)
	text_report (t_snps, m_snps, n_snps)


if __name__ == '__main__':
	options = parse_args (sys.argv)
	main (options)


### END #######################################################################
