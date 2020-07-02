#!/usr/bin/env python
"""
By, Guruprasad Ananda.
"""
from __future__ import print_function

import re
import sys


def main():
    if len(sys.argv) != 4:
        sys.exit("usage: convert_characters infile from_char outfile")

    try:
        fin = open(sys.argv[1], 'r')
    except Exception:
        sys.exit("Input file cannot be opened for reading.")

    from_char = sys.argv[2]

    try:
        fout = open(sys.argv[3], 'w')
    except Exception:
        sys.exit("Output file cannot be opened for writing.")

    char_dict = {'T': r'\t', 's': r'\s', 'Dt': r'\.', 'C': r',', 'D': r'-',
                 'U': r'_', 'P': r'\|', 'Co': r':'}
    # making an RE to match 1 or more occurences.
    from_ch = char_dict[from_char] + '+'
    skipped = 0

    for line in fin:
        line = line.strip()
        try:
            fout.write("%s\n" % (re.sub(from_ch, '\t', line)))
        except Exception:
            skipped += 1

    if skipped:
        print("Skipped %d lines as invalid." % skipped)


if __name__ == "__main__":
    main()
