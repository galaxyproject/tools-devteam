#!/usr/bin/env python
# Dan Blankenberg
"""
Takes a Multiple Alignment FASTA file and concatenates
sequences for each species, resulting in one sequence
alignment per species.
"""

import sys
import tempfile
from collections import OrderedDict

from utils.maf_utilities import iter_fasta_alignment


def __main__():
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    species = OrderedDict()
    cur_size = 0
    for components in iter_fasta_alignment(input_filename):
        species_not_written = list(species.keys())
        for component in components:
            if component.species not in species:
                species[component.species] = tempfile.TemporaryFile(mode="r+")
                species[component.species].write("-" * cur_size)
            species[component.species].write(component.text)
            try:
                species_not_written.remove(component.species)
            except ValueError:
                # this is a new species
                pass
        for spec in species_not_written:
            species[spec].write("-" * len(components[0].text))
        cur_size += len(components[0].text)
    with open(output_filename, 'w') as out:
        for spec, f in species.items():
            f.seek(0)
            out.write(">%s\n%s\n" % (spec, f.read()))


if __name__ == "__main__":
    __main__()
