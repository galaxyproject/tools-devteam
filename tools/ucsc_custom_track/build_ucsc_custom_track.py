#!/usr/bin/env python
"""
Build a UCSC genome browser custom track file
"""

import sys

FILE_TYPE_TO_TRACK_TYPE = {'bed': None, 'bedstrict': None, 'bed6': None, 'bed12': None, 'bedgraph': 'bedGraph', 'wig': 'wiggle_0'}
CHUNK_SIZE = 2**20  # 1 mb


def get_track_line_is_interval(file_type, name, description, color, visibility):
    if file_type in FILE_TYPE_TO_TRACK_TYPE:
        track_type = FILE_TYPE_TO_TRACK_TYPE[file_type]
        is_interval = False
    else:
        track_type = None
        is_interval = True
    track_line = 'track '
    if track_type:
        track_line += f"type={track_type} "
    track_line += f'name="{name}" description="{description}" color={color} visibility={visibility}\n'
    return track_line, is_interval


num_tracks = 0
skipped_lines = 0
first_invalid_line = 0
args = sys.argv[1:]
out_fname = args.pop(0)
with open(out_fname, "w") as out:
    while args:
        # Suck in one dataset worth of arguments
        in_fname = args.pop(0)
        file_type = args.pop(0)
        colspec = args.pop(0)
        name = args.pop(0)
        description = args.pop(0)
        color = args.pop(0).replace('-', ',')
        visibility = args.pop(0)
        track_line, is_interval = get_track_line_is_interval(file_type, name, description, color, visibility)
        # Do the work
        out.write(track_line)
        with open(in_fname) as in_file:
            if not is_interval:
                while True:
                    chunk = in_file.read(CHUNK_SIZE)
                    if chunk:
                        out.write(chunk)
                    else:
                        break
            else:
                # Assume type is interval (don't pass this script anything else!)
                try:
                    c, s, e, st = (int(x) - 1 for x in colspec.split(","))
                except ValueError:
                    try:
                        c, s, e = (int(x) - 1 for x in colspec.split(",")[:3])
                        st = -1  # strand column is absent
                    except Exception:
                        sys.exit("Columns in interval file invalid for UCSC custom track.")

                i = 0
                for i, line in enumerate(in_file):
                    line = line.rstrip('\r\n')
                    if line and not line.startswith('#'):
                        fields = line.split("\t")
                        if st > 0:
                            # strand column is present
                            try:
                                out.write(f"{fields[c]}\t{fields[s]}\t{fields[e]}\t{i}\t0\t{fields[st]}\n")
                            except Exception:
                                skipped_lines += 1
                                if not first_invalid_line:
                                    first_invalid_line = i + 1
                        else:
                            try:
                                out.write(f"{fields[c]}\t{fields[s]}\t{fields[e]}\n")
                            except Exception:
                                skipped_lines += 1
                                if not first_invalid_line:
                                    first_invalid_line = i + 1
        out.write("\n")  # separating newline
        num_tracks += 1

print(f"Generated a custom track containing {num_tracks} subtracks.")
if skipped_lines:
    print(f"Skipped {skipped_lines} invalid lines starting at #{first_invalid_line}")
