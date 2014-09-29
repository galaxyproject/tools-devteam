#!/usr/bin/env python

# Reads a tabular file and replaces a target sequence (currently 'NA') with a number in columns that have numerical values.
# Limitations: (a) can only take input from stdin and (b) cannot specify target or replacement.

import sys
import os
import tempfile

# Constants.
SEPARATOR = '\t'
TARGET = 'NA'
REPLACEMENT = -1
# List of known numerical columns.
NUMERICAL_COLUMNS = ['1000g2012apr_all', 'esp6500si_all']

# Use tempfile to store data.
temp_out = tempfile.NamedTemporaryFile(delete=False)

# Use first line to set up data structure and identify numerical columns.
first_line = sys.stdin.readline()
fields = first_line.strip().split(SEPARATOR)
numerical_cols = []
for i, f in enumerate(fields):
    if f in NUMERICAL_COLUMNS:
        numerical_cols.append(i)

# Data structure is a 2-element list for each fields; first element is # of string elements and second element is # of number elements.
col_type_counts = [ [0, 0] for i in range( len(fields) ) ]

# Set up function to process lines.
def process_line_fields(fields):
    '''
    Process fields in a line.
    '''
    for i, f in enumerate(fields):
        # Ignore targets in calculation.
        if f == TARGET:
            continue

        # Assume it's a number.
        type_index = 1
        try:
            float(f)
        except:
            # Not a number.
            type_index = 0
        col_type_counts[i][type_index] += 1


# Process first line.
process_line_fields(fields)
temp_out.write(first_line)

# Process N-1 lines.
for line in sys.stdin:
    fields = line.strip().split(SEPARATOR)
    process_line_fields(fields)
    temp_out.write(line)

# Close temp file so that it can be read.
temp_name = temp_out.name
temp_out.close()

# Get column type based on label or consensus.
col_types = range(len(col_type_counts))
for i, counts in enumerate(col_type_counts):
    if i in numerical_cols:
        col_type = 'number'
    elif counts[0] > counts[1]:
        col_type = 'string'
    else:
        col_type = 'number'
    col_types[i] = col_type

# Replace target in number columns.
for line in open(temp_name, 'r'):
    fields = line.strip().split(SEPARATOR)
    for i, f in enumerate(fields):
        if fields[i] == TARGET and col_types[i] == 'number':
            fields[i] = str(REPLACEMENT)
    print SEPARATOR.join(fields)

# Clean up temp file.
temp_out.close()
os.unlink(temp_out.name)



