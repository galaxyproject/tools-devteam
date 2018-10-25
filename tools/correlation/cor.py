#!/usr/bin/env python
#Greg Von Kuster
"""
Calculate correlations between numeric columns in a tab delim file.
usage: %prog infile output.txt columns method
"""

import sys
import rpy2.robjects as robjects
r = robjects.r


def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()
    
def main():
    method = sys.argv[4]
    assert method in ( "pearson", "kendall", "spearman" )

    try:
        column_string = sys.argv[3]
        columns = list()
        for col in column_string.split(','):
            if '-' in col:
                s, e = col.split('-')
                col = list(range(int(s), int(e) + 1))
                columns.extend(col)
            else:
                columns.append(int(col))
    except:
        stop_err( "Problem determining columns, perhaps your query does not contain a column of numerical data." )

    matrix = []
    skipped_lines = 0
    first_invalid_line = 0
    invalid_value = ''
    invalid_column = 0

    for i, line in enumerate( open( sys.argv[1] ) ):
        valid = True
        line = line.rstrip('\n\r')

        if line and not line.startswith( '#' ): 
            # Extract values and convert to floats
            row = []
            for column in columns:
                column -= 1
                fields = line.split( "\t" )
                if len( fields ) <= column:
                    valid = False
                else:
                    val = fields[column]
                    if val.lower() == "na": 
                        row.append( float( "nan" ) )
                    else:
                        try:
                            row.append( float( fields[column] ) )
                        except:
                            valid = False
                            skipped_lines += 1
                            if not first_invalid_line:
                                first_invalid_line = i+1
                                invalid_value = fields[column]
                                invalid_column = column+1
        else:
            valid = False
            skipped_lines += 1
            if not first_invalid_line:
                first_invalid_line = i+1

        if valid:
            matrix += row 

    if skipped_lines < i:
        # Run correlation
        try:
            fv = robjects.FloatVector(matrix)
            m = r['matrix'](fv, ncol=len(columns),byrow=True)
            rslt_mat = r.cor(m, use="pairwise.complete.obs", method=method )
            value = []
            for ri in range(1, rslt_mat.nrow + 1):
                row = []
                for ci in range(1, rslt_mat.ncol + 1):
                    row.append(rslt_mat.rx(ri,ci)[0])
                value.append(row)
        except Exception as exc:
            stop_err("%s" % str( exc ))
        
        with open( sys.argv[2], "w" ) as out:
            for row in value:
                out.write("%s\n" % "\t".join( map( str, row ) ))

    if skipped_lines > 0:
        msg = "..Skipped %d lines starting with line #%d. " %( skipped_lines, first_invalid_line )
        if invalid_value and invalid_column > 0:
            msg += "Value '%s' in column %d is not numeric." % ( invalid_value, invalid_column )
        print(msg)

if __name__ == "__main__":
    main()
