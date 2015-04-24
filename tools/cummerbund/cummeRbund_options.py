import sqlite3

def get_genes( database_path ):
    conn = sqlite3.connect( database_path )
    gene_ids = conn.execute( 'SELECT gene_short_name, gene_id FROM genes ORDER BY gene_short_name' )
    return [ ( gene_id[ 0 ], gene_id[ 1 ], False ) for gene_id in gene_ids ]

def get_samples( database_path ):
    conn = sqlite3.connect( database_path )
    samples = conn.execute( 'SELECT sample_name FROM samples ORDER BY sample_name' )
    return [ ( sample[ 0 ], sample[ 0 ], False ) for sample in samples ]
