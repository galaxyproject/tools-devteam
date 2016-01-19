#!/usr/bin/env python
"""
Uses fasta_to_len converter code.
"""

import sys
from utils.fasta_to_len import compute_fasta_length

compute_fasta_length( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == 'id_only' )
