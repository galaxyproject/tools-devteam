'''
Annotates a tabular file with information from the Drug-Gene Interaction (DGI) database.
'''

import optparse, json, urllib2, sys, re

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

    # -- Make connection and get results. --

    # Get gene list.
    gene_list = []
    lines = []
    for line in input_file:
        entry = line.split('\t')[gene_name_col].strip()
        # Some annotations may be of the form 
        #    <gene_name>(<splicing_info>) or <gene_name>;<gene_name>(splicing_info)
        gene_list.append(entry.split(';')[0].split('(')[0])
        lines.append(line.strip())
    
    # Query for results.
    query_str = 'http://dgidb.genome.wustl.edu/api/v1/interactions.json?genes=%s' % ','.join(set(gene_list))
    if options.expert_curated:
        query_str += '&source_trust_levels=Expert%20curated'
    results = urllib2.urlopen(query_str).read()
    results_dict = json.loads(results)
    
    # Process results.
    matched_results = results_dict['matchedTerms']
    for result in matched_results:
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
