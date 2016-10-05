#!/usr/bin/env python
"""
usage: %prog bed_file_1 bed_file_2 out_file
    -1, --cols1=N,N,N,N: Columns for chr, start, end, strand in first file
    -2, --cols2=N,N,N,N,N: Columns for chr, start, end, strand, name/value in second file
    -z, --allow_zeros: Include zeros in calculations
"""

import collections
import sys
from galaxy.tools.util.galaxyops import *
from bx.cookbook import doc_optparse


#export PYTHONPATH=~/galaxy/lib/
#running command python WeightedAverage.py interval_interpolate.bed value_interpolate.bed interpolate_result.bed

def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def FindRate(chromosome, start_stop, dictType):
    OverlapList = []
    for tempO in dictType[chromosome]:
        DatabaseInterval = [tempO[0], tempO[1]]
        Overlap = GetOverlap( start_stop, DatabaseInterval )
        if Overlap > 0:
            OverlapList.append([Overlap, tempO[2]])
    
    if len(OverlapList) > 0:
        SumRecomb = 0
        SumOverlap = 0
        for member in OverlapList:
            SumRecomb += member[0]*member[1]
            SumOverlap += member[0]
        averageRate = SumRecomb/SumOverlap
        return averageRate
    else:
        return 'NA'


def GetOverlap(a, b):
    return min(a[1], b[1])-max(a[0], b[0])

def get_float_no_zero( field ):
    rval = float( field )
    assert rval
    return rval


options, args = doc_optparse.parse( __doc__ )

try:
    chr_col_1, start_col_1, end_col_1, strand_col1 = parse_cols_arg( options.cols1 )
    chr_col_2, start_col_2, end_col_2, strand_col2, name_col_2 = parse_cols_arg( options.cols2 )
    input1, input2, input3 = args
except Exception, eee:
    print eee
    stop_err( "Data issue: click the pencil icon in the history item to correct the metadata attributes." )

if options.allow_zeros:
    get_value = float
else:
    get_value = get_float_no_zero
RecombChrDict = collections.defaultdict(list)

skipped = 0
for line in open( input2 ):
    temp = line.strip().split()
    try:
        value = get_value( temp[ name_col_2 ] )
    except Exception:
        skipped += 1
        continue
    tempIndex = [ int( temp[ start_col_2 ] ), int( temp[ end_col_2 ] ), value ]
    RecombChrDict[ temp[ chr_col_2 ] ].append( tempIndex )

print "Skipped %d features with invalid values" % (skipped)

fdd = open( input3, 'w' )
for line in open( input1 ):
    line = line.strip()
    temp = line.split('\t')
    chromosome = temp[ chr_col_1 ]
    start = int( temp[ start_col_1 ] )
    stop = int( temp[ end_col_1 ] )
    start_stop = [start, stop]
    RecombRate = FindRate( chromosome, start_stop, RecombChrDict )
    try:
        RecombRate = "%.4f" % (float(RecombRate))
    except:
        RecombRate = RecombRate
    fdd.write( "%s\t%s\n" % ( line, RecombRate ) )
fdd.close()
