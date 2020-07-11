#!/usr/bin/env python
# Greg Von Kuster

import sys

from rpy2.robjects import r, vectors
from rpy2.robjects.packages import importr


def main():
    # Handle input params
    in_fname = sys.argv[1]
    out_fname = sys.argv[2]
    try:
        column = int(sys.argv[3]) - 1
    except Exception:
        sys.exit("Column not specified, your query does not contain a column of numerical data.")
    title = sys.argv[4]
    xlab = sys.argv[5]
    breaks = int(sys.argv[6])
    if breaks == 0:
        breaks = "Sturges"
    if sys.argv[7] == "true":
        density = True
    else:
        density = False
    if len(sys.argv) >= 9 and sys.argv[8] == "true":
        frequency = True
    else:
        frequency = False

    matrix = []
    skipped_lines = 0
    first_invalid_line = 0
    invalid_value = ''
    i = 0
    for i, line in enumerate(open(in_fname)):
        valid = True
        line = line.rstrip('\r\n')
        # Skip comments
        if line and not line.startswith('#'):
            # Extract values and convert to floats
            row = []
            try:
                fields = line.split("\t")
                val = fields[column]
                if val.lower() == "na":
                    row.append(float("nan"))
            except Exception:
                valid = False
                skipped_lines += 1
                if not first_invalid_line:
                    first_invalid_line = i + 1
            else:
                try:
                    row.append(float(val))
                except ValueError:
                    valid = False
                    skipped_lines += 1
                    if not first_invalid_line:
                        first_invalid_line = i + 1
                        invalid_value = fields[column]
        else:
            valid = False
            skipped_lines += 1
            if not first_invalid_line:
                first_invalid_line = i + 1

        if valid:
            matrix.extend(row)

    if skipped_lines < i:
        try:
            grdevices = importr('grDevices')
            graphics = importr('graphics')
            vector = vectors.FloatVector(matrix)
            grdevices.pdf(out_fname, 8, 8)
            histogram = graphics.hist(vector, probability=not frequency, main=title, xlab=xlab, breaks=breaks)
            if density:
                density = r.density(vector)
                if frequency:
                    scale_factor = len(matrix) * (histogram['mids'][1] - histogram['mids'][0])  # uniform bandwidth taken from first 2 midpoints
                    density['y'] = map(lambda x: x * scale_factor, density['y'])
                graphics.lines(density)
            grdevices.dev_off()
        except Exception as exc:
            sys.exit("%s" % str(exc))
    else:
        if i == 0:
            sys.exit("Input dataset is empty.")
        else:
            sys.exit("All values in column %s are non-numeric." % sys.argv[3])

    print("Histogram of column %s. " % sys.argv[3])
    if skipped_lines > 0:
        print("Skipped %d invalid lines starting with line #%d, '%s'." % (skipped_lines, first_invalid_line, invalid_value))


if __name__ == "__main__":
    main()
