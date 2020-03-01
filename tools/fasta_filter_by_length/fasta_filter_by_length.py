#!/usr/bin/env python
"""
Input: fasta, minimal length, maximal length
Output: fasta
Return sequences whose lengths are within the range.
"""

import sys

assert sys.version_info[:2] >= (2, 4)


def stop_err(msg):
    sys.exit(msg)


def __main__():
    input_filename = sys.argv[1]
    try:
        min_length = int(sys.argv[2])
    except Exception:
        stop_err("Minimal length of the return sequence requires a numerical value.")
    try:
        max_length = int(sys.argv[3])
    except Exception:
        stop_err("Maximum length of the return sequence requires a numerical value.")
    output_filename = sys.argv[4]
    tmp_size = 0  # -1
    tmp_buf = ''
    at_least_one = 0
    with open(output_filename, 'w') as output_handle, open(input_filename, 'r') as input_handle:
        for line in input_handle:
            if not line or line.startswith('#'):
                continue
            if line[0] == '>':
                if min_length <= tmp_size <= max_length or (min_length <= tmp_size and max_length == 0):
                    output_handle.write(tmp_buf)
                    at_least_one = 1
                tmp_buf = line
                tmp_size = 0
            else:
                if max_length == 0 or tmp_size <= max_length:
                    tmp_size += len(line.rstrip('\r\n'))
                    tmp_buf += line
        # final flush of buffer
        if min_length <= tmp_size <= max_length or (min_length <= tmp_size and max_length == 0):
            output_handle.write(tmp_buf.rstrip('\r\n'))
            at_least_one = 1
    if at_least_one == 0:
        print("There is no sequence that falls within your range.")


if __name__ == "__main__":
    __main__()
