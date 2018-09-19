#!/usr/bin/env python
# Copyright (c) 2007 NHLBI, NIH
# Copyright (c) 2010 The George Washington University
# Authors: Chongzhi Zang, Weiqun Peng, Dustin E Schones and Keji Zhao
#
# This software is distributable under the terms of the GNU General
# Public License (GPL) v2, the text of which can be found at
# http://www.gnu.org/copyleft/gpl.html. Installing, importing or
# otherwise using this module constitutes acceptance of the terms of
# this License.
#
# Disclaimer
# 
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# Comments and/or additions are welcome (send e-mail to:
# wpeng@gwu.edu).
#
# Version 1.1  6/9/2010

"""
This module contains classes of genome data, e.g. chromsomes
per species, the size of the chromosomes, etc.
"""

import re, os, sys, shutil

GenomeDataError = "Error in GenomeData class";

bg_number_chroms = 1; 
bg_length_of_chrom = 100000000; 

background_chroms = [];
background_chrom_lengths = {};
for i in range(0,bg_number_chroms):
	background_chroms.append( 'chr' + str(i+1));
	background_chrom_lengths['chr' + str(i+1)] = bg_length_of_chrom;


mm8_chroms = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9',
	     'chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17',
	     'chr18','chr19','chrX', 'chrY', 'chrM']

mm9_chroms = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9',
             'chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17',
             'chr18','chr19','chrX', 'chrY', 'chrM']

mm10_chroms = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9',
             'chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17',
             'chr18','chr19','chrX', 'chrY', 'chrM']

rn4_chroms = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9',
	     'chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17',
	     'chr18','chr19','chr20','chrX','chrM']

hg18_chroms = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9',
	     'chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17',
	     'chr18','chr19','chr20','chr21','chr22','chrX','chrY','chrM']

hg19_chroms = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9',
	     'chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17',
	     'chr18','chr19','chr20','chr21','chr22','chrX','chrY','chrM']

sacCer1_chroms = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9',
		 'chr10','chr11','chr12','chr13','chr14','chr15','chr16','chrM']

dm2_chroms = ['chr2h', 'chr2L', 'chr2R', 'chr3h', 'chr3L',
	     'chr3R','chr4','chr4h','chrM','chrU','chrX','chrXh','chrYh']

dm3_chroms = ['chr2L', 'chr2LHet', 'chr2R', 'chr2RHet', 'chr3L', 'chr3LHet',
	     'chr3R', 'chr3RHet', 'chr4','chrX','chrXHet', 'chrYHet', 'chrU', 'chrUextra', 'chrM']

pombe_chroms = ['chr1','chr2', 'chr3', 'mat'];

tair8_chroms = ['chr1','chr2','chr3','chr4','chr5'];

mm8_chrom_lengths = {'chr1':197069962, 'chr2':181976762, 'chr3':159872112,
		     'chr4':155029701, 'chr5':152003063, 'chr6':149525685,
		     'chr7':145134094, 'chr8':132085098, 'chr9':124000669,
		     'chr10':129959148, 'chr11':121798632, 'chr12':120463159,
		     'chr13':120614378, 'chr14':123978870, 'chr15':103492577, 
		     'chr16':98252459, 'chr17':95177420, 'chr18':90736837,
		     'chr19':61321190, 'chrX':165556469, 'chrY':16029404,
		     'chrM':16299}

mm9_chrom_lengths = {'chr1':197195432, 'chr2':181748087, 'chr3':159599783,
                     'chr4':155630120, 'chr5':152537259, 'chr6':149517037,
                     'chr7':152524553, 'chr8':131738871, 'chr9':124076172,
                     'chr10':129993255, 'chr11':121843856, 'chr12':121257530,
                     'chr13':120284312, 'chr14':125194864, 'chr15':103494974, 
                     'chr16':98319150, 'chr17':95272651, 'chr18':90772031,
                     'chr19':61342430, 'chrX':166650296, 'chrY':15902555,
                     'chrM':16299}

mm10_chrom_lengths= {'chr1':195471971, 'chr2':182113224, 'chr3':160039680,
                     'chr4':156508116, 'chr5':151834684, 'chr6':149736546,
                     'chr7':145441459, 'chr8':129401213, 'chr9':124595110,
                     'chr10':130694993, 'chr11':122082543, 'chr12':120129022,
                     'chr13':120421639, 'chr14':124902244, 'chr15':104043685,
                     'chr16':98207768, 'chr17':94987271, 'chr18':90702639,
                     'chr19':61431566, 'chrX':171031299, 'chrY':91744698,
                     'chrM':16299}

rn4_chrom_lengths = {'chr1':267910886, 'chr2':258207540, 'chr3':171063335,
		     'chr4':187126005, 'chr5':173096209, 'chr6':147636619,
		     'chr7':143002779, 'chr8':129041809, 'chr9':113440463,
		     'chr10':110718848, 'chr11':87759784, 'chr12':46782294,
		     'chr13':111154910, 'chr14':112194335, 'chr15':109758846, 
		     'chr16':90238779, 'chr17':97296363, 'chr18':87265094,
		     'chr19':59218465, 'chr20':55268282, 'chrX':160699376,
		     'chrM':16300}



hg18_chrom_lengths = {'chr1':247249719, 'chr2':242951149, 'chr3':199501827,
		      'chr4':191273063, 'chr5':180857866, 'chr6':170899992,
		      'chr7':158821424, 'chr8':146274826, 'chr9':140273252,
		      'chr10':135374737, 'chr11':134452384, 'chr12':132349534,
		      'chr13':114142980, 'chr14':106368585, 'chr15':100338915,
		      'chr16':88827254, 'chr17':78774742, 'chr18':76117153,
		      'chr19':63811651, 'chr20':62435964, 'chr21':46944323,
		      'chr22':49691432, 'chrX':154913754, 'chrY':57772954,
		      'chrM':16571}

hg19_chrom_lengths = {'chr1':249250621,  'chr2':243199373, 'chr3':198022430,
		      'chr4':191154276, 'chr5':180915260, 'chr6':171115067,
		      'chr7':159138663,  'chr8':146364022, 'chr9':141213431,
		      'chr10':135534747, 'chr11':135006516, 'chr12':133851895,
		      'chr13':115169878, 'chr14':107349540, 'chr15':102531392,
		      'chr16':90354753,  'chr17':81195210,  'chr18':78077248,
		      'chr19':59128983,  'chr20':63025520,  'chr21':48129895,
		      'chr22':51304566,  'chrX':155270560,  'chrY':59373566,
		      'chrM':16571}


dm2_chrom_lengths = {'chr2h':1694122, 'chr2L':22407834, 'chr2R':20766785,
		     'chr3h':2955737, 'chr3L':23771897, 'chr3R':27905053,
		     'chr4h':88110, 'chr4':1281640, 'chrXh':359526,
		     'chrX':22224390, 'chrYh':396896, 'chrM':19517,
		     'chrU':8724946}

dm3_chrom_lengths = {'chr2L':23011544, 
			'chr2LHet':368872, 
			'chr2R':21146708, 
			'chr2RHet':3288761, 
			'chr3L':24543557, 
			'chr3LHet':2555491,
			'chr3R':27905053,
			'chr3RHet':2517507, 
			'chr4':1351857,
			'chrX':22422827,
			'chrXHet':204112, 
			'chrYHet':347038, 
			'chrU':10049037, 
			'chrUextra':29004656, 
			'chrM':19517}


sacCer1_chrom_lengths = {'chr1':230208, 'chr2':813136, 'chr3':316613,
			 'chr4':1531914, 'chr5':576869, 'chr6':270148,
			 'chr7':1090944, 'chr8':562639, 'chr9':439885,
			 'chr10':745446, 'chr11':666445, 'chr12':1078173,
			 'chr13':924430, 'chr14':784328, 'chr15':1091285,
			 'chr16':948060, 'chrM':85779}


pombe_chrom_lengths = {'chr1':5580032,'chr2':4541604,'chr3':2453783,
		       'mat':41249}

tair8_chrom_lengths = {'chr1':30427671, 'chr2':19698289, 'chr3':23459830,
		       'chr4':18585056, 'chr5':26975502}


species_chroms = {'mm8':mm8_chroms, 
			'mm9':mm9_chroms, 
                        'mm10':mm10_chroms,
			'hg18':hg18_chroms,
			'hg19':hg19_chroms,
		  	"dm2":dm2_chroms, 
			"dm3":dm3_chroms, 
			"sacCer1":sacCer1_chroms,
		  	"pombe":pombe_chroms, 
			'rn4':rn4_chroms,
			'tair8':tair8_chroms,
		  	'background':background_chroms};


species_chrom_lengths={'mm8':mm8_chrom_lengths,
		       'mm9':mm9_chrom_lengths,
                       'mm10':mm10_chrom_lengths,
		       'hg18':hg18_chrom_lengths,
		       'hg19':hg19_chrom_lengths,
		       'dm2':dm2_chrom_lengths,
		       'dm3':dm3_chrom_lengths,
		       'sacCer1':sacCer1_chrom_lengths,
		       'pombe':pombe_chrom_lengths,
		       'rn4':rn4_chrom_lengths,
		       'tair8':tair8_chrom_lengths,
		       'background':background_chrom_lengths};




