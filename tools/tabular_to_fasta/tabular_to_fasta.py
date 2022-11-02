#!/usr/bin/env python
"""
Input: fasta, title columns (comma separated), sequence column
Output: fasta
Return tabular format sequences converted to FASTA
"""
import argparse
import sys


def stop_err(msg):
    sys.exit(msg)


def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=argparse.FileType())
    parser.add_argument('title_col')
    parser.add_argument('seq_col')
    parser.add_argument('output_file', type=argparse.FileType('w'))
    args = parser.parse_args()
    title_col = args.title_col
    seq_col = args.seq_col

    if title_col is None or title_col == 'None' or seq_col is None or seq_col == 'None':
        stop_err("Columns not specified.")
    try:
        seq_col = int(seq_col) - 1
    except ValueError:
        stop_err("Invalid Sequence Column: %s." % str(seq_col))

    title_col_list = title_col.strip().split(',')
    skipped_lines = 0
    first_invalid_line = 0
    invalid_line = ""
    i = 0

    for i, line in enumerate(args.input_file):
        error = False
        line = line.rstrip('\r\n')
        if line and not line.startswith('#'):
            fields = line.split('\t')
            fasta_title = []
            for j in title_col_list:
                try:
                    j = int(j) - 1
                    fasta_title.append(fields[j])
                except ValueError:
                    skipped_lines += 1
                    if not invalid_line:
                        first_invalid_line = i + 1
                        invalid_line = line
                    error = True
                    break
            if not error:
                try:
                    fasta_seq = fields[seq_col]
                    if fasta_title[0].startswith(">"):
                        fasta_title[0] = fasta_title[0][1:]
                    print(">%s\n%s" % ("_".join(fasta_title), fasta_seq), file=args.output_file)
                except ValueError:
                    skipped_lines += 1
                    if not invalid_line:
                        first_invalid_line = i + 1
                        invalid_line = line

    if skipped_lines > 0:
        print('Data issue: skipped %d blank or invalid lines starting at #%d: "%s"' % (skipped_lines, first_invalid_line, invalid_line))


if __name__ == "__main__":
    __main__()
