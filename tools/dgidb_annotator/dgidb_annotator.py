'''
Annotates a tabular file with information from the Drug-Gene Interaction (DGI) database.
'''

import optparse, json, urllib2, sys

def __main__():
    # -- Parse command line. --
    parser = optparse.OptionParser()
    parser.add_option('-g', '--gene-name-col', dest='gene_name_col', help='column of gene names')
    parser.add_option('-a', '--print-all', dest='print_all', action='store_true', help='print all lines, even though without a result')
    parser.add_option('-e', '--expert-curated', dest='expert_curated', action='store_true', help='use only expert curated results')
    (options, args) = parser.parse_args()
    gene_name_col = int(options.gene_name_col) - 1

    # Open input stream.
    if len(args) > 0:
        input_file = open(args[0], 'r')
    else:
        input_file = sys.stdin

    # -- Set up gene list queries. --

    # Get gene list.
    gene_list = []
    lines = []
    for line in input_file:
        entry = line.split('\t')[gene_name_col].strip()
        # Some annotations may be of the form 
        #    <gene_name>(<splicing_info>) or <gene_name>;<gene_name>(splicing_info)
        gene_list.append(entry.split(';')[0].split('(')[0])
        lines.append(line.strip())
    
    # Set up gene lists to be ~8K because this is near the max HTTP request length.
    gene_list = ','.join(set(gene_list))
    queries = []
    MAX_QUERY_SIZE = 8000
    if len(gene_list) > MAX_QUERY_SIZE:
        # Break queries.
        queries = [ gene_list[i:i + MAX_QUERY_SIZE] for i in range(0, len(gene_list), MAX_QUERY_SIZE) ]

        # Adjust queries to include whole genes.
        for i, query in enumerate( queries[1:] ):
            part_gene, comma, remainder = query.partition(',')
            queries[i] += part_gene
            queries[i+1] = remainder
    else:
        queries = [ gene_list ]

    # -- Query and process results. --

    # Query for results.
    results = []
    for genes in queries:
        query_str = 'http://dgidb.genome.wustl.edu/api/v1/interactions.json?genes=%s' % genes
        if options.expert_curated:
            query_str += '&source_trust_levels=Expert%20curated'
        raw_results = urllib2.urlopen(query_str).read()
        results_dict = json.loads(raw_results)
        results.extend(results_dict['matchedTerms'])
        
    # Process results.
    for result in results:
        # Process result.
        processed_results = []
        result_fields = [ result['geneName'], result['geneLongName'], ','.join( result['geneCategories'] ) ]
        for interaction in result['interactions']:
            result_fields = result_fields[0:3]
            result_fields.extend( [
                interaction['interactionType'], interaction['drugName'], interaction['source']
            ] )
            processed_results.append( '\t'.join( result_fields ) )
            
        # Store processed results.
        results_dict[ result['searchTerm'] ] = processed_results

    # -- Annotate input file and produce output. --
    for line in lines:
        fields = line.split('\t')
        gene = fields[gene_name_col]
        if gene in results_dict:
            for result in results_dict[gene]:
                print line.strip() + '\t' + result
        elif options.print_all:
            print line

if __name__=="__main__": __main__()
