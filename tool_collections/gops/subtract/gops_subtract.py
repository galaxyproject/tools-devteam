#!/usr/bin/env python
"""
Find regions of first interval file that do not overlap regions in a second
interval file. Interval files can either be BED or GFF format.

usage: %prog interval_file_1 interval_file_2 out_file
    -1, --cols1=N,N,N,N: Columns for start, end, strand in first file
    -2, --cols2=N,N,N,N: Columns for start, end, strand in second file
    -m, --mincols=N: Require this much overlap (default 1bp)
    -p, --pieces: just print pieces of second set (after padding)
    -G, --gff1: input 1 is GFF format, meaning start and end coordinates are 1-based, closed interval
    -H, --gff2: input 2 is GFF format, meaning start and end coordinates are 1-based, closed interval
"""
from __future__ import print_function

import fileinput
import sys

from bx.cookbook import doc_optparse
from bx.intervals.io import GenomicInterval, NiceReaderWrapper
from bx.intervals.operations.subtract import subtract
from bx.tabular.io import ParseError
from galaxy.tools.util.galaxyops import fail, parse_cols_arg, skipped

from utils.gff_util import convert_bed_coords_to_gff, GFFFeature, GFFReaderWrapper

assert sys.version_info[:2] >= ( 2, 4 )


def main():
    mincols = 1

    options, args = doc_optparse.parse( __doc__ )
    try:
        chr_col_1, start_col_1, end_col_1, strand_col_1 = parse_cols_arg( options.cols1 )
        chr_col_2, start_col_2, end_col_2, strand_col_2 = parse_cols_arg( options.cols2 )
        if options.mincols:
            mincols = int( options.mincols )
        pieces = bool( options.pieces )
        in1_gff_format = bool( options.gff1 )
        in2_gff_format = bool( options.gff2 )
        in_fname, in2_fname, out_fname = args
    except:
        doc_optparse.exception()

    # Set readers to handle either GFF or default format.
    if in1_gff_format:
        in1_reader_wrapper = GFFReaderWrapper
    else:
        in1_reader_wrapper = NiceReaderWrapper
    if in2_gff_format:
        in2_reader_wrapper = GFFReaderWrapper
    else:
        in2_reader_wrapper = NiceReaderWrapper

    g1 = in1_reader_wrapper( fileinput.FileInput( in_fname ),
                             chrom_col=chr_col_1,
                             start_col=start_col_1,
                             end_col=end_col_1,
                             strand_col=strand_col_1,
                             fix_strand=True )
    if in1_gff_format:
        # Subtract requires coordinates in BED format.
        g1.convert_to_bed_coord = True

    g2 = in2_reader_wrapper( fileinput.FileInput( in2_fname ),
                             chrom_col=chr_col_2,
                             start_col=start_col_2,
                             end_col=end_col_2,
                             strand_col=strand_col_2,
                             fix_strand=True )
    if in2_gff_format:
        # Subtract requires coordinates in BED format.
        g2.convert_to_bed_coord = True

    out_file = open( out_fname, "w" )
    try:
        for feature in subtract( [g1, g2], pieces=pieces, mincols=mincols ):
            if isinstance( feature, GFFFeature ):
                # Convert back to GFF coordinates since reader converted automatically.
                convert_bed_coords_to_gff( feature )
                for interval in feature.intervals:
                    out_file.write( "%s\n" % "\t".join( interval.fields ) )
            elif isinstance( feature, GenomicInterval ):
                out_file.write( "%s\n" % "\t".join( feature.fields ) )
            else:
                out_file.write( "%s\n" % feature )
    except ParseError as exc:
        out_file.close()
        fail( "Invalid file format: %s" % str( exc ) )

    out_file.close()

    if g1.skipped > 0:
        print(skipped( g1, filedesc=" of 2nd dataset" ))
    if g2.skipped > 0:
        print(skipped( g2, filedesc=" of 1st dataset" ))


if __name__ == "__main__":
    main()
