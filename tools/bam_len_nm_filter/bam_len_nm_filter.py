#!/usr/bin/python
import os
import sys
import pysam


def get_nm(read):
    return float( read.get_tag( 'NM' ) )


infile = sys.argv[1]
outfile = sys.argv[2]
threshold = float( sys.argv[3] )
min_length = int( sys.argv[4] )
single_paired = sys.argv[5]
read_with_no_tag = 0

( dirname, filename ) = os.path.split( infile )

sam=pysam.AlignmentFile( infile,'rb' )
out=pysam.AlignmentFile( outfile,'wb',template=sam )


for read in sam:
    if single_paired == "paired":
        try:
            read1=read
            read2=sam.next()

            if get_nm(read1)<=( threshold*read1.rlen ) and get_nm(read2)<=( threshold*read2.rlen ) and read1.rlen >= min_length and read1.rlen >= min_length:
                out.write( read1 )
                out.write( read2 )
            else:
                pass

        except KeyError:
                read_with_no_tag += 1

        except StopIteration:
                sam.close()
                out.close()

    elif single_paired == "single":
        try:
            if get_nm(read)<=( threshold*read.rlen ) and read.rlen >= min_length:
                out.write(read)
            else:
                pass

        except KeyError:
                read_with_no_tag += 1

        except StopIteration:
                sam.close()
                out.close()

print read_with_no_tag